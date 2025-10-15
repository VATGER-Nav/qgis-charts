import sys
import argparse
from pathlib import Path
import logging
from rich.logging import RichHandler
from pyogrio import errors as pyogrio_errors

from sct import Sectors


def main(prog_name: str, *argv: str) -> None:
    argp = argparse.ArgumentParser(
        prog="sct2ogr",
        usage="%(prog)s <format> <source> [target]"
    )
    argp.add_argument(
        "format",
        type=str,
        help="Target format (GEOJSON, GPKG, ...)"
    )
    argp.add_argument(
        "source",
        type=Path,
        help="Source directory"
    )
    argp.add_argument(
        "target",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Target directory (default: current directory)"
    )
    args = argp.parse_args(argv)

    driver = args.format

    source_dir = Path(args.source).resolve()
    logging.info(f"Processing {source_dir.name}")
    if not source_dir.is_file():
        argp.error("File not found")

    target_dir =  Path(args.target).resolve()
    if target_dir == Path.cwd():
        target_dir = Path.cwd() / source_dir.with_suffix(f".{args.format}")
    
    sectors = Sectors(source_dir)
    sectors.parse()

    try:
        sectors.gdf.to_file(target_dir, driver=driver)
    except pyogrio_errors.DataLayerError:
        logging.error(f"{target_dir} already exist")
        return
    
    logging.info(f"Saved at {target_dir}")


if __name__ == "__main__":
    logging.basicConfig(
        format="{message}",
        style="{",
        handlers=[RichHandler(show_time=False, show_path=False)],
        level=logging.INFO,
    )
    sys.exit(main(*sys.argv))