import argparse
import logging
import sys
from pathlib import Path

from core import apply_watermark
from settings import Settings

logger = logging.getLogger("")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
filehandler = logging.FileHandler("aim_watermarker.log", "a", "utf-8")
filehandler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(filehandler)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path",
        type=str,
        help="Indirizzo della cartella o del file",
    )

    parser.add_argument(
        "--scale",
        type=int,
        help="Scala del logo come percentuale della dimensione più corta",
        default=10,
    )

    parser.add_argument(
        "--position",
        type=str,
        choices=["topleft", "topright", "bottomleft", "bottomright", "center"],
        help="Posizione del logo (allowed: topleft, topright, bottomleft, bottomright, center)",
        default="bottomright",
    )

    parser.add_argument(
        "--padding",
        type=int,
        help="Padding del logo come percentuale della dimensione più corta",
        default=1,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    settings = Settings(
        scale=args.scale,
        position=args.position,
        padding=args.padding,
    )

    input_path = Path(args.path)

    if not input_path.exists():
        raise FileNotFoundError(f"{input_path} non esiste")

    if not input_path.is_dir():
        raise NotADirectoryError(f"{input_path} non è una cartella")

    output_path = input_path.parent / f"{input_path.name}_watermarked"
    output_path.mkdir(exist_ok=True)

    pdf_files = sorted(list(input_path.glob("*.pdf")))

    for pdf_file in pdf_files:
        logging.info(f"Applying watermark to: {pdf_file.name}")
        destination_file = str(output_path / pdf_file.name)
        apply_watermark(pdf_file, destination_file, settings)
