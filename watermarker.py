import argparse

from src.app import Watermarker

if __name__ == "__main__":
    # Instantiate the parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Indirizzo della cartella o del file",
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        default=False,
        action="store_true",
        help="Sovrascrive il file originale",
    )

    args = parser.parse_args()

    # Instantiate the class
    watermaker = Watermarker(args.path, args.overwrite)

    # Call the method
    watermaker.run()
