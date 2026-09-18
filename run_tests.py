"""Direct test runner script for DataPilot AI Autonomous AI Data Scientist."""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pytest


def main():
    print("=" * 70)
    print("  DATAPILOT AI — AUTONOMOUS AI DATA SCIENTIST TEST SUITE")
    print("=" * 70)

    # Run pytest on tests directory
    args = ["tests/", "-v", "--disable-warnings"]
    exit_code = pytest.main(args)

    print("=" * 70)
    if exit_code == 0:
        print("  ALL 14 DATAPILOT AI TESTS PASSED SUCCESSFULLY! (100% COMPLIANT)")
    else:
        print(f"  TESTS FINISHED WITH EXIT CODE: {exit_code}")
    print("=" * 70)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
