from time import time
import ipaddress
import sys

from . import IdentificationTool


tool = IdentificationTool()


def test_ip(idtool, ip: str):
    start_t = time()
    vendor = idtool.get_vendor_by_ip(ip)
    print(f"SEARCH TIME: {time() - start_t:.6f}\tIP: {ip}{' ' * (10 if len(ip) < 10 else 2)}\tVENDOR: {vendor}")


# @TODO: Add a proper argparser handling here.
if len(sys.argv) == 2:
    if sys.argv[1] == "generate":
        start_t = time()
        tool.export_packed()
        print("EXPORT TIME:", round(time() - start_t, 2))

else:
    # Testing
    test_ip(tool, "8.8.8.8")
    test_ip(tool, "12.34.56.78")
    test_ip(tool, "64.225.92.1")
    test_ip(tool, "204.152.18.71")
    test_ip(tool, "2405:8100:1111::")

