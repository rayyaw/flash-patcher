#!/usr/bin/env python3

import argparse
from pathlib import Path

from flash_patcher.patcher import main

def cli():
    """Run Flash Patcher from the CLI."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--inputswf",
        dest="input_swf",
        type=str,
        required=True,
        help="Input SWF file",
    )

    parser.add_argument(
        "--folder",
        dest="folder",
        type=str,
        required=True,
        help="Folder with patch files",
    )

    parser.add_argument(
        "--stagefile",
        dest="stage_file",
        type=str,
        required=True,
        help="Stage file name",
    )

    parser.add_argument(
        "--outputswf",
        dest="output_swf",
        type=str,
        required=True,
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

    args = parser.parse_args()

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
