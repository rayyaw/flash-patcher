#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from pathlib import Path

from flash_patcher.patcher import main, print_version

def validate_args(args: Namespace) -> bool:
    """Validate if all CLI arguments are provided correctly.
    Returns True if the provided set of arguments is valid.
    """
    return args.input_swf and args.folder and args.stagefile and args.output_swf

def cli() -> None:
    """Run Flash Patcher from the CLI."""
    parser = ArgumentParser()

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
        dest="stagefile",
        type=str,
        help="Top-level patcher file",
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

    parser.add_argument(
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Show verbose logging output",
    )

    args = parser.parse_args()

    if args.version:
        print_version()
        return

    if not validate_args(args):
        parser.print_usage()
        print("flash-patcher: error: the following arguments are required:\n \
            --inputswf, --folder, --stagefile, --outputswf")
        return

    main(
        Path(args.input_swf),
        Path(args.folder),
        Path(args.stagefile),
        Path(args.output_swf),
        drop_cache=args.drop_cache,
        recompile_all=args.recompile_all,
        xml_mode=args.xml_mode,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    cli()
