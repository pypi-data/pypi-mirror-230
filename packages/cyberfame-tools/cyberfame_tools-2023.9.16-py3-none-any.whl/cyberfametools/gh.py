from datetime import datetime, timedelta
from collections import defaultdict
from itertools import cycle
from hashlib import sha256
from pprint import pprint
from uuid import uuid4
from io import BytesIO
import itertools
import argparse
import aiohttp
import asyncio
import logging
import tarfile
import random
import time
import json
import sys
import os


class GithubInternalError(Exception): pass
class GithubUnknownError(Exception): pass
class GithubNotFoundError(Exception): pass
class GithubRateLimitError(Exception): pass


class Cache:
    CACHE_FP = ".dep_tree_cache.json"
    CACHE_LIFETIME_DAYS = 7

    def __init__(self, persistent = True):
        self.persistent = persistent

        self.data = self.load_cache()

    # NOTE: While this is not a thing for docker environment (i.e. production),
    #       we still want to have persistent cache for dev.
    # TODO: Implement tool-specific persistent cache in the cloud-gateway infra,
    #       so we can reuse this cache between runs, and dramatically decrease
    #       amount of requests made to github graphql api. It can be easily
    #       done by attaching tool-specific volume (e.g. 'rdc_cache') to each
    #       container before the start. Standard cache path '/morphysm/cache'.
    def load_cache(self):
        if self.persistent and os.path.exists(self.CACHE_FP):
            with open(self.CACHE_FP, "r") as f:
                return json.load(f)
        return {}

    def __getitem__(self, key):
        if key not in self.data:
            return None

        created_at = datetime.utcfromtimestamp(self.data[key]["created_at"])
        now, week = datetime.now(), timedelta(days=self.CACHE_LIFETIME_DAYS)

        if (now - created_at) > week:
            return None

        return self.data[key]["data"]

    def __setitem__(self, key, value):
        self.data[key] = {"created_at": datetime.now().timestamp(), "data": value}

        if self.persistent:
            # On every new item - write to disk for persistency.
            with open(self.CACHE_FP, "w+") as f:
                json.dump(self.data, f, indent=4)


class GithubTool:
    GH_PREFIX = "github.com"
    GH_URL = "github.com/{}"
    MANIFESTS_QUERY = """{
        repository(owner: \"%s\", name: \"%s\") {
            dependencyGraphManifests(first: %s, after: \"%s\", withDependencies: true) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    id
                    blobPath
                }
            }
        }
    }"""

    DEPENDENCIES_QUERY_PREFIX = "{\n"
    DEPENDENCIES_QUERY_SUFFIX = "\n}"
    DEPENDENCIES_QUERY_VALUE = """
    %s: node (id: "%s") {
        ... on DependencyGraphManifest {
            dependencies(first: %s, after: \"%s\") {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    packageName
                    requirements
                    hasDependencies
                    repository {
                        nameWithOwner
                    }
                }
            }
        }
    }
    """

    RATE_LIMIT_QUERY = """{
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }"""

    def __init__(self, token: str, endpoint: str = "https://api.github.com/graphql", persistent_cache: bool = True):
        self.endpoint = endpoint
        self.repo_locks = defaultdict(asyncio.Lock)
        self.token_locks = defaultdict(asyncio.Lock)

        self.tokens = [t.strip() for t in token.split(",")]
        # Shuffle tokens at start, to approximate roundrobin for one-comamnd runs.
        random.shuffle(self.tokens)
        self.tokener = itertools.cycle(self.tokens)

        self.cache = Cache(persistent_cache)

    async def run_query(self, query: str, err_sleep: int = 20, retries: int = 3, token = None) -> dict:
        token = token if token else next(self.tokener)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.hawkgirl-preview"
        }
        async with self.token_locks[token]:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json={"query": query}, headers=headers) as r:
                    data = await r.json()

        if data.get("message"):
            error = data["message"].lower()
            if "you have exceeded a secondary rate limit" in error:
                raise GithubRateLimitError

            logging.error("ERROR: message present: %s", json.dumps(data, indent=4))

            raise GithubUnknownError("unknown github error..")

        if "errors" in data:
            error = data["errors"][0]["message"].lower()

            if "could not resolve to a repository with the name" in error:
                raise GithubNotFoundError

            # @NOTE: Github sometimes errors out like this, maybe internal systems
            #        there return a timeout or something like that, because response
            #        contains 'data: None' and the following error:
            if error == "timedout" or "something went wrong while executing your query" in error:
                if not retries:
                   raise GithubInternalError("github missbehaving [ran out of retries] ...")

                logging.warning("Github misbehaving: trying again in %s seconds [%s retries left]!", err_sleep, retries-1)
                await asyncio.sleep(err_sleep)
                return await self.run_query(query, err_sleep+10, retries=retries-1)

            logging.error("ERROR: bad data: %s", json.dumps(data, indent=4))
            raise GithubUnknownError("unknown github error..")

        if not data.get("data"):
            logging.error("ERROR: bad data: %s", json.dumps(data, indent=4))
            raise GithubUnknownError("unknown github error..")

        return data

    async def rate_limit(self):
        outputs = []
        results = await asyncio.gather(*(self.run_query(self.RATE_LIMIT_QUERY, token=token) for token in self.tokens))
        for token, resp in zip(self.tokens, results):
            outputs.append({"token": token, **resp})
        return outputs

    async def _get_manifests(self, owner, name, manifests_per_page, cursor):
        retries = 0
        while retries < 3:
            query = self.MANIFESTS_QUERY % (owner, name, manifests_per_page, cursor)
            try:
                return await self.run_query(query, retries=retries)
            except GithubInternalError:
                logging.warning("Quering manifests using current page_size failed, trying again with lower...")
                retries += 1
                manifests_per_page //= 2
                await asyncio.sleep(5)

    async def get_manifests(self, repo: str, manifests_per_page: int = 50):
        owner, name = repo.split("/")
        first_time, count, total = True, 0, None

        has_next, cursor = True, ""
        manifests = []
        while has_next:
            r = await self._get_manifests(owner, name, manifests_per_page, cursor)
            data = r["data"]["repository"]["dependencyGraphManifests"]
            if first_time:
                first_time = False
                total = data["totalCount"]
                logging.info("Repo '%s': total %s manifests (we skip empty ones, so expect less)!", repo, total)

            for manifest in data["nodes"]:
                count += 1
                # Properly parsing filepath to the manifest:
                #     path schema: /<resource>/<repo>/blob/<branch>/<...path/to/manifest/file.ext>
                _prefix, branched_path = manifest["blobPath"].split("/blob/")
                _branch, *paths, fname = branched_path.split("/")
                mname = "/".join((*paths, fname))
                # SKIP all kinds of lock files: they contain full trees instead of just first-order.
                if "lock" in fname or fname == "go.sum":
                    logging.warning("Skipped manifest '%s' [%s]!", mname, repo)
                    continue

                manifest["path"] = mname
                # manifest["filename"] = fname
                manifests.append(manifest)

            has_next, cursor = data["pageInfo"]["hasNextPage"], data["pageInfo"]["endCursor"]

        logging.info("Repo '%s': returning manifests %s (%s queried, %s total)!", repo, len(manifests), count, total)
        return manifests

    async def _get_dependencies(self, data, work, retries = 0):
        query = self.DEPENDENCIES_QUERY_PREFIX
        for i, mid in enumerate(work):
            query += self.DEPENDENCIES_QUERY_VALUE % (f"n{i}", mid, data[mid]["page_size"], data[mid]["cursor"])
        query += self.DEPENDENCIES_QUERY_SUFFIX

        results = await self.run_query(query, retries=retries)

        finished = []
        for i, mid in enumerate(work):
            deps = results["data"][f"n{i}"]["dependencies"]
            data[mid]["dependencies"].extend(deps["nodes"])
            data[mid]["cursor"] = deps["pageInfo"]["endCursor"]

            if not deps["pageInfo"]["hasNextPage"]:
                logging.info("Finished processing manifest '%s' ...", data[mid]["path"])
                del data[mid]["cursor"]
                del data[mid]["page_size"]
                finished.append(mid)
        return finished

    async def get_dependencies(self, data, work):
        logging.info("Processing batch of %s manifests ...", len(work))
        retries = 0
        while retries < 3:
            try:
                return await self._get_dependencies(data, work, retries=retries)
            except GithubInternalError:
                logging.warning("Quering dependencies using current page_size failed, trying again with lower...")
                retries += 1
                for mid in work: data[mid]["page_size"] //= 2
                await asyncio.sleep(5)

    async def _shallow_dependencies(self, repo: str, manifests_per_request = 5, deps_per_page = 80):
        # Since we are using async requests, we need to apply lock per repo here,
        # so when we request two same repos in a row, the second request gets blocked
        # here and then immediatelly gets fullfilled from the cache.
        async with self.repo_locks[repo]:
            # Before making an actual request, we want to check our local cache to avoid
            # wasting API quotas. Notice that this is not a regular dict but our custom
            # class 'Cache', where calling '__getitem__' on non-existing is safe!
            if result := self.cache[repo]: return result

            # First, we query all the manifests in the repo, which allows us to generate
            # appropriately scaled queries, tracking multiple cursors at the same time.
            manifests = await self.get_manifests(repo)
            manifests = {m.pop("id"): {"cursor": "", "page_size": deps_per_page, "dependencies": [], **m} for m in manifests}
            # This is a work-list that decreases continuously as work is being done.
            ids = [mid for mid in manifests]
            while ids:
                tasks = []
                # Paginating remaining work based on how many tokens we have to allow for
                # processing as many requests in parallel as possible, remaining stability.
                for page in range(len(self.tokens)):
                    work = ids[page*manifests_per_request:(page+1)*manifests_per_request]
                    if not work: break

                    tasks.append(self.get_dependencies(manifests, work))

                task_results = await asyncio.gather(*tasks)
                for task_result in task_results:
                    for mid in task_result:
                        ids.remove(mid)

            result = {"manifests": list(manifests.values())}
            self.cache[repo] = result
            return result

    async def dependency_tree(self, repo: str, limit: int, depth: int = 0, results: list = None) -> dict:
        batch = []

        data = await self._shallow_dependencies(repo)
        repo_data = {"type": "repository", "url": self.GH_URL.format(repo), "name": repo.lower(), "manifests": []}
        results.append(repo_data)

        for manifest in data["manifests"]:
            manifest_data = {"type": "manifest", "name": manifest["path"], "dependencies": []}

            for dependency in manifest["dependencies"]:
                # Not always an available github repository.
                try:
                    dep_type, dep_id = "repository", dependency["repository"]["nameWithOwner"].lower()
                    dep_url = self.GH_URL.format(dep_id)
                except TypeError:
                    dep_type, dep_id = "dependency", dependency["packageName"].lower()
                    dep_url = ""

                # NOTE: Special case, check whether dependency is the current repo itself, because
                # while in general it's impossible to have a recursive dependency situation
                # (my project X depends on a project Y which in turn depends on my project X),
                # but inside one project many manifests allow/require you to define your own
                # codebase as a dependency. For example, package 'testing' in the project
                # references code from the same project (but package 'src'). We don't care
                # about this kind of dependency, because it's not external, so remove it here.
                if dep_id == repo_data["name"]: continue

                dep_data = {"url": dep_url, "name": dep_id, "requirements": dependency["requirements"] or ""}
                manifest_data["dependencies"].append(dep_data)

                # TODO: FIX dep_url part for private deps. Github shows them somehow.
                if dep_url and dependency["hasDependencies"]:
                    if depth < limit:
                        batch.append(self.dependency_tree(dep_id, limit, depth + 1, results))

            # NOTE: Only care about manifest file if it contains *any* dependencies,
            #       otherwise it's a pretty useless node. But more importantly, this
            #       avoids confusion about non-existing files, because somehow github
            #       still returns a manifest file even if it doesn't exist but can,
            #       for a given language. For example, if your project is in python,
            #       github will still return (empty) 'requirements.txt' manifest.
            if manifest_data["dependencies"]:
                repo_data["manifests"].append(manifest_data)

        await asyncio.gather(*batch)
        return results

    async def _gen_to_cypher(self, url: str, recursion_depth: int = 0):
        url = url.lower()
        si = url.find(self.GH_PREFIX)
        assert si != -1, f"'{url}' IS NOT A GITHUB LINK?"
        url = url[si+len(self.GH_PREFIX):].strip("/")
        owner, name, *_ = url.split("/")
        repo = f"{owner}/{name}"

        main_repo, *repos = await self.dependency_tree(repo, limit=recursion_depth, results=[])

        # Generating cypher for main entity:
        main_cipher = (
            "WITH $data as data\n"
            "MATCH (e:Entity|repo {url: data.url})\n"
            "SET e.name = data.name\n"
            "WITH e, data\n"
            "UNWIND data.manifests as manifest\n"
            "WITH e, manifest\n"
            "UNWIND manifest.dependencies as dep\n"
            "MERGE (d:repo {url: dep.url})\n"
            "SET d.name = dep.name\n"
            "MERGE (e)-[m:HAS_DEPENDENCY]->(d)\n"
            # Specify parent repo for manifest ('requirements.txt' from
            # different repos are completely different assets conceptually).
            "SET m.name = manifest.name, m.requirements = dep.requirements\n"
        )

        # Cipher for the dependencies.
        ciphers = cycle([
            "WITH $data as data\n"
            "MERGE (r:repo {url: data.url})\n"
            "SET r.name = data.name\n"
            "WITH r, data\n"
            "UNWIND data.manifests as manifest\n"
            "WITH r, manifest\n"
            "UNWIND manifest.dependencies as dep\n"
            "MERGE (d:repo {url: dep.url, name: dep.name})\n"
            "MERGE (r)-[m:HAS_DEPENDENCY]->(d)\n"
            # Specify parent repo for manifest ('requirements.txt' from
            # different repos are completely different assets conceptually).
            "SET m.name = manifest.name, m.requirements = dep.requirements\n"
        ])

        yield 0, main_cipher, main_repo

        for i, (cipher, repo) in enumerate(zip(ciphers, repos)):
            yield i + 1, cipher, repo

    async def gen_to_cypher(self, url: str, recursion_depth: int = 0):
        with tarfile.open("ciphers.tar", "w") as tfile:
            async for i, cipher, repo in self._gen_to_cypher(url, recursion_depth):
                self.add_pair(tfile, f"result{i}.cip", cipher, f"result{i}.json", json.dumps(repo))

    def add_pair(self, tfile, cname, cdata, dname, data):
        # Encoding cipher query.
        encoded = cdata.encode()
        tinfo = tarfile.TarInfo(name=cname)
        tinfo.mtime = time.time()
        tinfo.size = len(encoded)
        # Add cipher to tarfile.
        tfile.addfile(tinfo, BytesIO(encoded))

        # Encoding repo data.
        encoded = data.encode()
        tinfo = tarfile.TarInfo(name=dname)
        tinfo.mtime = time.time()
        tinfo.size = len(encoded)
        # Add cipher to tarfile.
        tfile.addfile(tinfo, BytesIO(encoded))


async def main():
    parser = argparse.ArgumentParser(description="Generate dependency graph")
    parser.add_argument("repository", help="the GitHub owner/repository", nargs="?", default="")
    parser.add_argument("-r", "--recursion-depth", type=int, default=0)
    parser.add_argument("-o", "--output", type=str, default="")
    parser.add_argument("--docker", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--rate-limits", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(filename)7s:%(lineno)-3s - %(levelname)-7s - %(message)s",
        level=logging.INFO,
    )

    api = GithubTool(token=os.environ["GITHUB_TOKEN"])

    if args.docker:
        # Opening entity file from TC.
        with open("entity.json") as f:
            entity = json.load(f)

        url = entity["item"]["URL"]
        start_t = time.time()
        await api.gen_to_cypher(url, recursion_depth = 0)
        print(f"Finished in {round(time.time() - start_t, 2)}s!")

    elif args.repository:
        data = await api.dependency_tree(args.repository, limit = args.recursion_depth, results = [])
        if not args.output:
            print(data)
            exit(0)

        with open(args.output, "w+") as f:
            # json.dump(data, f, indent=4)
            json.dump(data, f)

    elif args.rate_limits:
        data = await api.rate_limit()
        print(json.dumps(data, indent=4))
        exit(0)

    else:
        print("You have to provide 'repository' argument (or '--docker' flag)!")


if __name__ == "__main__":
    asyncio.run(main())

