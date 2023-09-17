from dataclasses import dataclass
from pprint import pprint
from pathlib import Path
from enum import Enum
import ipaddress
import bisect
import json
import os


class Vendor(Enum):
    azure = 0
    aws = 1
    google = 2
    cloudflare = 3
    digitalocean = 4


# @TODO: Can't use this, because python3.7 compatibility.
# @dataclass(frozen=True, slots=True)
@dataclass(frozen=True)
class IPRange:
    first_ip: int
    last_ip: int
    vendor: int


@dataclass
class IPNet:
    first_ip: int
    last_ip: int
    cidr: int
    vendor: int


class IdentificationTool:
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    RANGES_FP = ROOT_DIR / ".." / "ranges"
    EXPORT_FP = ROOT_DIR / "data"

    def __init__(self):
        self.vendors = {
            "azure": self.iter_azure,
            "aws": self.iter_aws,
            "google": self.iter_google,
            "cloudflare": self.iter_cloudflare,
            "digitalocean": self.iter_digitalocean,
        }
        self.ips = []
        if self.EXPORT_FP.exists() and (self.EXPORT_FP / "packed.bin").exists():
            self.load_packed()

    def iter_azure(self):
        with open(self.RANGES_FP / "azure.json") as f:
            data = json.load(f)

        for group in data["values"]:
            for value in group["properties"]["addressPrefixes"]:
                yield value

    def iter_aws(self):
        with open(self.RANGES_FP / "aws.json") as f:
            data = json.load(f)

        for item in data["prefixes"]:
            # @TODO: We have to be python3.7 compatible because we use it.
            # if value := item.get("ip_prefix"):
            value = item.get("ip_prefix")
            if value:
                yield value

            # if value := item.get("ipv6_prefix"):
            value = item.get("ip_prefix")
            if value:
                yield value

    def iter_google(self, paths = ("google.json", "google2.json")):
        for path in paths:
            with open(self.RANGES_FP / path) as f:
                data = json.load(f)

            for item in data["prefixes"]:
                # if value := item.get("ipv4Prefix"):
                value = item.get("ipv4Prefix")
                if value:
                    yield value

                # if value := item.get("ipv6Prefix"):
                value = item.get("ipv6Prefix")
                if value:
                    yield value

    def iter_cloudflare(self):
        data = ""

        with open(self.RANGES_FP / "cloudflare-ips-v4.txt") as f:
            data += f.read()
            data += "\n"

        with open(self.RANGES_FP / "cloudflare-ips-v6.txt") as f:
            data += f.read()

        for value in data.split("\n"):
            yield value

    def iter_digitalocean(self):
        data = ""

        with open(self.RANGES_FP / "digitalocean.csv") as f:
            data += f.read()

        for row in data.split("\n"):
            value, *_ = row.split(",")
            value = value.strip(" \n\r\t")
            if value:
                yield value

    def iterate_raw_nets(self):
        unique = set()

        for vendor, data_iter in self.vendors.items():
            for value in data_iter():
                if value in unique:
                    continue

                unique.add(value)
                yield value, vendor

    def generate_nets(self):
        raw_nets = []
        for value, vendor in self.iterate_raw_nets():
            ip, cidr = value.split("/")
            ip = ipaddress.ip_address(ip)
            net = ipaddress.ip_network(value)

            # @NOTE: Technically this is not a 'first' ip, because it needs
            #        to be (ip + 1), since this one is a 'broadcast' address.
            #        But so far for all our intents and purposes this is fine,
            #        because this is still of course vendor's address.
            first_ip = int(ip) & int(net.netmask)
            last_ip = int(ip) | int(net.hostmask)

            raw_nets.append(IPNet(first_ip, last_ip, int(cidr), Vendor[vendor].value))

        return list(sorted(raw_nets, key=lambda ipnet: ipnet.first_ip))

    def merge(self, ips):
        # Preparing the data first.
        for i in range(1, len(ips) - 1):
            previous = ips[i - 1]
            current = ips[i]
            if (previous.vendor == current.vendor) and ((previous.last_ip + 1) == current.first_ip):
                previous._next = current

        # Now merging the data:
        merged = []
        index = 1
        while index < (len(ips) - 1):
            previous = ips[index - 1]
            index += 1
            if not hasattr(previous, "_next") or not previous._next:
                merged.append(previous)
                continue

            current = previous._next
            while hasattr(current, "_next") and current._next:
                current = current._next
                index += 1

            # start, end = ipaddress.ip_address(previous.first_ip), ipaddress.ip_address(current.last_ip)
            # nets = list(ipaddress.summarize_address_range(start, end))
            # print(start, end)
            # print(nets)
            # assert len(nets) == 1, "Merge function is broken!"
            # _, cidr = nets[0].with_prefixlen.split("/")
            # merged.append(IPNet(previous.first_ip, current.last_ip, -1, previous.vendor))
            merged.append(IPRange(previous.first_ip, current.last_ip, previous.vendor))

        merged = list(sorted(merged, key=lambda ipr: ipr.first_ip))
        """
        print("BEFORE:", len(ips), "AFTER:", len(merged))
        for old, new in zip(ips[:20], merged[:20]):
            old_s = ipaddress.ip_address(old.first_ip)
            old_e = ipaddress.ip_address(old.last_ip)
            new_s = ipaddress.ip_address(new.first_ip)
            new_e = ipaddress.ip_address(new.last_ip)
            print(f"old:\t{old_s} \t-\t {old_e}\t[{old.cidr}]\tnew:\t{new_s} \t-\t {new_e}\t[{new.cidr}]")
        """
        return merged

    def get_vendor_by_ip(self, ipaddr: str):
        ip = int(ipaddress.ip_address(ipaddr))

        low, high, mid = 0, len(self.ips) - 1, 0

        while low <= high:
            mid = (high + low) // 2

            # If x is greater, ignore left half
            if self.ips[mid].last_ip < ip:
                low = mid + 1

            # If x is smaller, ignore right half
            elif self.ips[mid].first_ip > ip:
                high = mid - 1

            # means x is present at mid
            else:
                return Vendor(self.ips[mid].vendor).name

        # If we reach here, then the element was not present
        return "unknown"

    def export_packed(self):
        ips = self.generate_nets()
        ips = self.merge(ips)

        packed = b""
        for ipr in ips:
            is_ipv4 = int(isinstance(ipaddress.ip_address(ipr.first_ip), ipaddress.IPv4Address))
            # @TODO: This is not used for now, because actually storing proper subnets as
            #        'ip/mask' is questionable compared to 'start_ip/end_ip' in terms of
            #        an efficient use of the disk space.
            #
            # Turning normal net mask from '1-128' to '0-127' so it fits exactly into 7 bits,
            # and then we can use the last (8th) bit to store bool on whether IP address is
            # ipv4 or ipv6, which we don't really need for the actual matching, but we use it
            # to store data on disk much more efficiently (if ipv4 - fit in 4 bytes, if ipv6 -
            # fit in 16 bytes).
            # datapack = (ipr.cidr - 1) << 1 | is_ipv4
            # packed += datapack.to_bytes(1, "little")

            packed += is_ipv4.to_bytes(1, "little")
            packed += ipr.vendor.to_bytes(1, "little")
            packed += ipr.first_ip.to_bytes(4 if is_ipv4 else 16, "little")
            packed += ipr.last_ip.to_bytes(4 if is_ipv4 else 16, "little")

        self.EXPORT_FP.mkdir(exist_ok=True)
        with open(self.EXPORT_FP / "packed.bin", "wb") as f:
            f.write(packed)

    def load_packed(self):
        assert self.EXPORT_FP.exists()
        with open(self.EXPORT_FP / "packed.bin", "rb") as f:
            packed = f.read()

        index = 0
        while index < len(packed):
            # is_ipv4 = packed[index] & 1
            # cidr = (packed[index] >> 1) + 1
            # index += 1
            is_ipv4 = packed[index]
            index += 1
            vendor = int.from_bytes(packed[index:index+1], "little")
            index += 1

            ip_size = 4 if is_ipv4 else 16
            first_ip = int.from_bytes(packed[index:index+ip_size], "little")
            index += ip_size
            last_ip = int.from_bytes(packed[index:index+ip_size], "little")
            index += ip_size

            # net = ipaddress.ip_network(f"{ip}/{cidr}")
            # last_ip = ip | int(net.hostmask)
            self.ips.append(IPRange(first_ip, last_ip, vendor))

        # print(len(self.ips))

