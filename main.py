#!/usr/bin/env python3
"""Copy the bundled entry.png to /output/entry.png (stdlib only)."""
import os
import shutil

def main():
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    dst_dir = "/output"
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(dst_dir, "entry.png"))

if __name__ == "__main__":
    main()
