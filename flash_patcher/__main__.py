#!/usr/bin/env python3

import argparse
from pathlib import Path

from flash_patcher.patcher import main, print_version

def cli() -> None:
    """Run Flash Patcher from the CLI."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--inputswf",
        dest="input_swf",
        type=str,
        help="Input SWF file",
    )

    parser.add_argument(
        "--folder",
        dest="folder",
        type=str,
        help="Folder with patch files",
    )

    parser.add_argument(
        "--stagefile",
        dest="stage_file",
        type=str,
        help="Stage file name",
    )

    parser.add_argument(
        "--outputswf",
        dest="output_swf",
        type=str,
        help="Output SWF file",
    )

    parser.add_argument(
        "--invalidateCache",
        dest="drop_cache",
        default=False,
        action="store_true",
        help="Invalidate cached decompilation files",
    )

    parser.add_argument(
        "--all",
        dest="recompile_all",
        default=False,
        action="store_true",
        help="Recompile the whole SWF (if this is off, only scripts will recompile)",
    )

    parser.add_argument(
        "--xml",
        dest="xml_mode",
        default=False,
        action="store_true",
        help="Inject into an XML decompilation instead of standard syntax",
    )

    parser.add_argument(
        "--version",
        dest="version",
        default=False,
        action="store_true",
        help="Print the current version of Flash Patcher and exit",
    )

    args = parser.parse_args()

    if args.version:
        print_version()
        return

    if (not args.input_swf) or (not args.folder) or (not args.stage_file) or (not args.output_swf):
        parser.print_usage()
        print("flash-patcher: error: the following arguments are required:\n \
              --inputswf, --folder, --stagefile, --outputswf")
        return

    main(
        Path(args.input_swf),
        Path(args.folder),
        Path(args.stage_file),
        Path(args.output_swf),
        drop_cache=args.drop_cache,
        recompile_all=args.recompile_all,
        xml_mode=args.xml_mode,
    )


if __name__ == "__main__":
    cli()
