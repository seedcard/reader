"""Run the reader over every photo in ../testdata and compare with expected.json.

Usage: python3 run_tests.py
"""
import json
import os
import sys

import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reader import read_plate  # noqa: E402

TD = os.path.join(HERE, "..", "testdata")


def main():
    exp = json.load(open(os.path.join(TD, "expected.json")))
    want = exp["words"].upper().split()
    ok_all = True
    print(f"{'photo':<30} {'expect':<7} {'words right':<12} {'checksum':<9} {'suggestion fixes it':<20} time")
    for name, meta in exp["photos"].items():
        res = read_plate(cv2.imread(os.path.join(TD, name)))
        if not res["ok"]:
            right, chk, fix, secs = "-", "-", "-", "-"
            passed = meta["expect"] == "fail"
        else:
            got = res["words"]
            right = f"{sum(a == b for a, b in zip(got, want))}/12"
            chk = "valid" if res["checksum_valid"] else "INVALID"
            sug = res.get("suggestion")
            fix = "-" if not sug else ("yes" if sug["words"] == want else "no")
            secs = f"{res['seconds']} s"
            exact = got == want
            if meta["expect"] == "read":
                # A pass: all words right, or a wrong word caught by the checksum and fixed by the suggestion.
                passed = exact or (not res["checksum_valid"] and fix == "yes")
            else:
                # Must not return a wrong seed with a valid checksum.
                passed = exact or not res["checksum_valid"]
        ok_all &= passed
        print(f"{name:<30} {meta['expect']:<7} {right:<12} {chk:<9} {fix:<20} {secs}  {'PASS' if passed else 'FAIL'}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
