#!/usr/bin/env python3
import argparse
from pnml_parser import parse_pnml, summarize

def main():
    ap = argparse.ArgumentParser(description="Task1: PNML parser & consistency checker (1-safe)")
    ap.add_argument("path", help="Path to .pnml file")
    args = ap.parse_args()
    net = parse_pnml(args.path)
    print(summarize(net))

if __name__ == "__main__":
    main()
