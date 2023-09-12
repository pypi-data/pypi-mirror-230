import json
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Dict

from spraakbanken.dataset import Dataset

AVAILABLE_DATASETS = [ "NST", "Storting", "NBtale", "NBsamtale" ]

def fetch_meta(obj: Dict[str, Any], folder_path: str, timestamp: str) -> None:
    # stores the metadata in a json file with checksum id
    filename = f"{obj['checksum']}_{timestamp}.json"
    path = os.path.join(folder_path, filename)
    with open(path, "w", encoding="latin-1") as meta_file:
        json.dump(obj["meta"], meta_file, indent=4)
            
def handle_dataset(dataset_name: str, args: Namespace) -> None:
    dataset = Dataset(dataset_name, args)
    dataset.create_data_folder()

    print(f"Fetching metadata for {dataset_name}...")
    fetch_meta(obj=dataset.obj, folder_path=dataset.folder, timestamp=dataset.timestamp)
    if args.meta:
        return
    
    if not dataset.has_existing_checksum():
        print("Exiting...")
        sys.exit(0)

    dataset.list_files()

    inp = input("Download all? [yes (Y) / no (N)] ")
    if inp.lower() not in ["y", "yes"]:
        return

    dataset.download_files()
    print(f"Downoad complete for {dataset_name}...")

def main(args: Namespace) -> None:
    """ handles all steps from user input to the downloading and structuring of data
    Args:
        args (Namespace): the arguments passed from the terminal
    """
    dataset = args.dataset
    valid = [d.lower() for d in AVAILABLE_DATASETS]


    if not dataset:
        dataset = input(f"Enter dataset {AVAILABLE_DATASETS} or 'all': ").lower()
    if dataset == "all":
        print("Downloading all datasets...")
        for _dataset in AVAILABLE_DATASETS:
            handle_dataset(_dataset.lower(), args)
    elif dataset in valid:
        handle_dataset(dataset, args)
    else:
        print(f"Invalid dataset provided... Must be in {AVAILABLE_DATASETS}")


if __name__ == "__main__":
    parser = ArgumentParser()
    # * [NST](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-54/)
    # * [NPSC](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-84/)
    # * [NB tale](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-31/)
    # * [NB samtale](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-85/)
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        help=f"A dataset in the list {AVAILABLE_DATASETS}",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        help="The output directory for the downloaded files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints additional debug information",
    )
    parser.add_argument(
        "--meta",
        action="store_true",
        help="Skips the download process, only fetches metadata",
    )
    parser.add_argument(
        "--unpack",
        action="store_true",
        help="Unpacks downloaded archives",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Removes downloaded and unpacked archives",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="no",
        help="Language to download. Only applies to certain datasets.",
    )

    main(args=parser.parse_args())
