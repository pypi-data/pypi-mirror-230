from typing import Union, Optional
from urllib.parse import urlparse
from io import BytesIO
from time import time
import tarfile
import json
import sys
import re


class BasicTool:
    def __init__(self):
        self.results = []

    def add_result(self, cypher: str, data: Optional[dict] = None):
        self.results.append((cypher, data))

    def save(self, result_path: str = "ciphers.tar"):
        assert self.results, "Can't output empty 'ciphers.tar' file!"
        with tarfile.open(result_path, "w") as tfile:
            for i, (cypher, data) in enumerate(self.results):
                cname, dname = f"{i}.cip", f"{i}.json"
                self._add_pair(tfile, cname, cypher, dname, data)

    def save_empty(self, result_path: str = "ciphers.tar"):
        with tarfile.open(result_path, "w") as tfile:
            pass

    def _add_pair(self, tfile, cname, cdata, dname, data):
        # Encoding cipher query.
        encoded = cdata.encode()
        tinfo = tarfile.TarInfo(name=cname)
        tinfo.mtime = time()
        tinfo.size = len(encoded)
        # Add cipher to tarfile.
        tfile.addfile(tinfo, BytesIO(encoded))

        if dname and data:
            # Encoding repo data.
            encoded = json.dumps(data).encode()
            tinfo = tarfile.TarInfo(name=dname)
            tinfo.mtime = time()
            tinfo.size = len(encoded)
            # Add cipher to tarfile.
            tfile.addfile(tinfo, BytesIO(encoded))

    @staticmethod
    def parse_url(source: str):
        if not source.startswith("http"):
            source = f"http://{source}"
        parsed = urlparse(source)
        return parsed

    @classmethod
    def read_input(cls, entity_path: str = "entity.json"):
        # TODO: Proper argparse here.
        if len(sys.argv) == 2:
            url = sys.argv[1]
        else:
            with open("entity.json") as entity_file:
                data = json.load(entity_file)
            url = data["item"]["URL"]
        # Returning already parsed object.
        return url, cls.parse_url(url)

    @staticmethod
    def validate_repo_url(source: str, domains: list = ["github.com"]):
        """
        Returns True if the url exactly matches a repo (not some files in the repo).
        """
        if not source.startswith("http"): source = f"http://{source}"

        parsed = urlparse(source)
        if parsed.hostname not in domains: return False, None

        paths = parsed.path.strip("/").split("/")
        if len(paths) != 2: return False, None

        name, repo = paths # @TODO: Check that unpacked arguments are valid for github.
        return True, f"{parsed.hostname}/{name}/{repo}"

