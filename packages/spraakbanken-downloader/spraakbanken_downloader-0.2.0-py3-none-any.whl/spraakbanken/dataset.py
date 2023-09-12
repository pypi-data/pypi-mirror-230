import os
import shutil
from datetime import datetime
from argparse import Namespace
from spraakbanken.sprakbanken_scraping import make_dataset_object
from spraakbanken.util import download_url
from spraakbanken.dataset_custom_rules import get_datamover

def set_permissions(path: str, is_directory: bool=False) -> None:
    # Set read and execute permissions for all users
    mode = 0o555 if is_directory else 0o444
    os.chmod(path, mode)

class Dataset(object):
    def __init__(self, dataset_name: str, args: Namespace) -> None:
        self.outdir = args.outdir
        self.verbose = args.verbose
        self.language = args.language
        self.unpack = args.unpack
        self.cleanup = args.cleanup

        self.name = dataset_name.lower()
        self.obj = make_dataset_object(dataset=self.name)

        self.timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self.folder = self.name  # to be updated to a specific arg-based folder

        self.print_init_info()

    def verbose_print(self, msg: str) -> None:
        if self.verbose:
            print(msg)
            
    def print_init_info(self) -> None:
        print(f"Accessed URL '{self.obj['url']}' at {self.timestamp}")
        print(f"Fetching data for dataset: '{self.name}'")
        print(f"Last updated at {self.obj['updated']}")
        print("-" * 40)

        self.verbose_print("Metadata:")
        for meta_key, meta_val in self.obj["meta"].items():
            self.verbose_print(f"{meta_key}: {meta_val}")
        self.verbose_print("-" * 40)
        
    def create_data_folder(self) -> None:
        if self.outdir:
            folder_path = self.outdir
        else:
            folder_path = os.path.join(os.getcwd(), "data")

        folder_path = os.path.join(folder_path, self.name)
        os.makedirs(folder_path, exist_ok=True)

        self.folder = folder_path

    def has_existing_checksum(self) -> bool:
        checksums = [f.split("_")[0] for f in os.listdir(self.folder) if f.endswith(".json")]
        if str(self.obj["checksum"]) in checksums:
            print(f"Dataset ({self}) already downloaded")
            inp = input("Continue to download regardless? [yes (Y) / no (N)] ")
            if inp.lower() in ["n", "no"]:
                return False
        return True

    def list_files(self) -> None:
        print("Found the following files:")
        for i, _file in enumerate(self.obj["downloads"]):
            print(f"{i+1}. {_file.split('/')[-1]}")


    def download_files(self) -> None:
        for i, _file in enumerate(self.obj["downloads"]):
            _name = _file.split("/")[-1]
            _path = os.path.join(self.folder, _name)
            print(f"{i+1}. {_name}")
            
            # 1 -- Download
            download_url(url=_file, fpath=_path)

            print(f"\nDownloaded {_name}")

            if not self.unpack:
                print("Skipping archive unpacking... To unpack, run with the --unpack flag")
                continue

            # 2 -- Unpack and delete old archives
            archive_path = os.path.join(self.folder, _name.split(".")[0])
            os.makedirs(archive_path, exist_ok=True)
            shutil.unpack_archive(_path, archive_path)
            if self.cleanup:
                os.remove(_path)
            else:
                print("Keeping original archive... To delete, run with the --cleanup flag")

            # set permissions:
            # Set permissions for directories and files
            set_permissions(archive_path, is_directory=True)
            for root, _, files in os.walk(archive_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    set_permissions(file_path)

            # 3 -- Move files to folder based on custom rules
            mover = get_datamover(self.name)
            if mover:
                mover(archive_path, self.language)

    def __str__(self) -> str:
        return self.name
