#!/usr/bin/env python3

from pathlib import Path
import sys

def main():
    path = Path("__main__.py")

    if path.exists():
        print(path)
    else:
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()