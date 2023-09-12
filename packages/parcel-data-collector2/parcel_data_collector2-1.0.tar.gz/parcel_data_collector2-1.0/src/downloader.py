"""This module will focus on downloading, formatting and storing Florida
County Parcel databases."""
import logging
import os
import time
import urllib.request
import zipfile
from typing import List, Union

import pandas as pd

from .constants import DATABASE_DESTINATION_PATH
from .download_item import (
    CountyDownload,
    Dataframe,
    DataframeDownload,
    ZipDownload,
)


class Downloader:
    """Download class for miscellaneous county data files."""

    def __init__(
        self,
        county_downloads: List[Union[DataframeDownload, ZipDownload]],
        download_destination_path: str = DATABASE_DESTINATION_PATH,
    ):
        self.county_downloads = county_downloads
        self.download_destination_path = download_destination_path
        self.download_files()

    def download_files(self) -> None:
        """Downloads the files from the given urls."""

        for download in self.county_downloads:
            if isinstance(download, ZipDownload):
                self.download_zip(download)
            elif isinstance(download, DataframeDownload):
                file_name = download.file_name
                destination = os.path.join(
                    self.download_destination_path, file_name
                )
                self.download_file(download, destination)
                self.convert_to_feather(
                    file_name=file_name,
                    folder_path=self.download_destination_path,
                    delimiter=download.file.delimiter,
                )

    def download_file(self, download: CountyDownload, destination: str) -> None:
        """Downloads the file from the given url.

        Args:
            download (CountyDownload): The file download.
            destination (str): The destination path to download the
                file to.
        """
        try:
            logging.info(f"Downloading {download.url}")
            urllib.request.urlretrieve(download.url, destination)
            logging.info(f"Finished downloading {download.url}")
        except Exception as e:
            logging.error(f"Failed to download {download.url}: {e}")
            return

    def download_zip(self, download: ZipDownload) -> None:
        """Downloads the zip file from the given url.

        Args:
            download (ZipDownload): The zip download.
        """

        temp_directory_path = os.path.join(
            self.download_destination_path, "temp"
        )

        if not os.path.exists(temp_directory_path):
            os.makedirs(temp_directory_path)

        zip_destination_path = os.path.join(
            temp_directory_path, f"{download.file_name}.zip"
        )

        self.download_file(download, zip_destination_path)
        self.unzip_file(
            zip_destination_path, download.files, temp_directory_path
        )

    def unzip_file(
        self,
        zipped_directory_path: str,
        files_to_keep: List[Dataframe],
        unzip_destination_path: str = "",
    ) -> None:
        """Unzips the file(s) from the given path.

        Args:
            zipped_directory_path (str): The path to the zipped
                directory.
            files_to_keep (List[Dataframe]): The files to keep.
            unzip_destination_path (str, optional): The path to unzip
                the files to. Defaults to None.
        """
        file_names = [f.file_name for f in files_to_keep]

        if not unzip_destination_path:
            unzip_destination_path = zipped_directory_path
        try:
            with zipfile.ZipFile(zipped_directory_path, "r") as zip_ref:
                zip_ref.extractall(unzip_destination_path)
            logging.info(f"Finished unzipping {zipped_directory_path}")
        except Exception as e:
            logging.error(f"Failed to unzip {zipped_directory_path}: {e}")
        finally:
            for file in os.listdir(unzip_destination_path):
                file_path = os.path.join(unzip_destination_path, file)

                if file not in file_names and not file.endswith(".zip"):
                    logging.info(f"Removing {file_path}")
                    self.remove_file(file_path)
                else:
                    logging.info(f"Keeping {file_path}")

        for file in files_to_keep:
            file_name = file.file_name
            file_delimiter = file.delimiter
            file_columns = file.columns
            self.convert_to_feather(
                file_name=file_name,
                folder_path=unzip_destination_path,
                columns_to_keep=file_columns,
                delimiter=file_delimiter,
            )

    def remove_file(self, file_path: str):
        """Removes the given file.

        Args:
            file_path (str): The path to the file to remove.
        """
        try:
            os.remove(file_path)
            logging.info(f"Successfully removed {file_path}")
        except Exception as e:
            logging.error(f"Failed to remove {file_path}: {e}")

    def convert_directory_to_feather(
        self,
        directory_path: str,
        columns_to_keep: list = [],
    ):
        """Converts the given directory to feather files.

        Args:
            directory_path (str): The path to the directory to convert.
            columns_to_keep (list, optional): The columns to keep in the
                feather file. Defaults to [].
        """
        for file_name in os.listdir(directory_path):
            if "." in file_name and ".feather" not in file_name:
                self.convert_to_feather(
                    file_name=file_name,
                    folder_path=directory_path,
                    columns_to_keep=columns_to_keep,
                )

    def convert_to_feather(
        self,
        file_name: str,
        folder_path: str,
        file_suffix: str = ".feather",
        encoding: str = "latin1",
        delete_original: bool = True,
        columns_to_keep: list = [],
        delimiter: str = ",",
    ) -> None:
        """Converts the given file to a feather file.

        Args:
            file_name (str): The file to convert.
            folder_path (str): The folder path to the file.
            file_suffix (str, optional): The suffix to add to the file.
            encoding (str, optional): The encoding of the file. Defaults to
                "latin1".
            delete_original (bool, optional): Whether or not to delete the
                original file. Defaults to True.
            columns_to_keep (list, optional): The columns to keep in the
                feather file. Defaults to [].
            delimiter (str, optional): The delimeter of the file. Defaults
                to ",".
        """

        file = os.path.join(folder_path, file_name)
        logging.debug(f"Reading {file}")
        try:
            if file.endswith(".xlsx"):
                df = pd.read_excel(
                    file,
                    dtype="str",
                    usecols=columns_to_keep if columns_to_keep else None,
                )
            else:
                df = pd.read_csv(
                    file,
                    encoding=encoding,
                    on_bad_lines="warn",
                    dtype="str",
                    usecols=columns_to_keep if columns_to_keep else None,
                    delimiter=delimiter,
                )
            logging.info(f"Finished reading {file}")
        except Exception as e:
            logging.error(f"Failed to read {file}: {e}")
            return

        try:
            df.fillna("", inplace=True)
            logging.info(f"Successfully filled NaN values in {file}")
        except Exception as e:
            logging.error(f"Failed to fill NaN values in {file}: {e}")
            return

        file_prefix = file_name.split(".")[0]
        output_file_path = f"{file_prefix}{file_suffix}"
        output_file_path = os.path.join(
            self.download_destination_path,
            output_file_path,
        )
        logging.info("Removing blank spaces from column data")
        for col in df.columns:
            df[col] = df[col].str.strip()
        logging.info("Successfully removed blank spaces from column data")

        try:
            df.to_feather(output_file_path)
            logging.info(f"Successfully exported {file} to feather")
        except Exception as e:
            logging.error(f"Failed to export {file} to feather: {e}")
            return
        finally:
            if delete_original:
                try:
                    os.remove(file)
                    logging.info(f"Successfully removed original file {file}")
                except Exception as e:
                    logging.error(f"Failed to remove original file {file}: {e}")

    def safe_str_convert(self, x: object):
        """Safely converts x to a string.

        Args:
            x (object): The object to convert to a string.

        Returns:
            str: The string representation of x.
        """
        return str(x) if x is not None else ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    downloads = [
        ZipDownload(
            "Sarasota",
            "https://www.sc-pa.com/downloads/SCPA_Detailed_Data.zip",
            "SarasotaSubdivisions",
            [
                Dataframe("SubDivisionIndex.txt"),
            ],
        ),
        ZipDownload(
            "Manatee",
            "https://www.manateepao.gov/data/manatee_ccdf.zip",
            "ManateeCCDF",
            [
                Dataframe(
                    "manatee_ccdf.csv",
                    columns=[
                        "CUR_MAN_LUC_DESC",
                        "LAND_SQFT_CAMA",
                        "PAR_GEO_RANGE",
                        "PAR_GEO_SECTION",
                        "PAR_GEO_TOWNSHIP",
                        "PAR_LEGAL1",
                        "PAR_SUBDIV_NAME",
                        "PAR_SUBDIVISION",
                        "PAR_ZONING",
                        "PARID",
                        "SALE_BOOK_LAST",
                        "SALE_DATE_LAST",
                        "SALE_KEY_LAST",
                        "SALE_PAGE_LAST",
                        "SALE_INSTRNO_LAST",
                    ],
                )
            ],
        ),
        DataframeDownload(
            "Manatee",
            "https://www.manateepao.gov/data/subdivisions_in_manatee.csv",
            "ManateeSubdivisions.csv",
            Dataframe("ManateeSubdivisions.csv"),
        ),
        DataframeDownload(
            "Charlotte",
            "https://www.ccappraiser.com/downloads/condominiums.xlsx",
            "CharlotteCondominiums.xlsx",
            Dataframe("CharlotteCondominiums.xlsx"),
        ),
        DataframeDownload(
            "Charlotte",
            "https://www.ccappraiser.com/downloads/subdivisions.xlsx",
            "CharlotteSubdivisions.xlsx",
            Dataframe("CharlotteSubdivisions.xlsx"),
        ),
        ZipDownload(
            "Charlotte",
            "https://www.ccappraiser.com/downloads/charlotte.zip",
            "CharlotteMisc",
            [
                Dataframe(
                    "cd.txt",
                    "|",
                    [
                        "account",
                        "city",
                        "SaleBook",
                        "SalePage",
                        "InstrumentNumber",
                        "totalarea",
                    ],
                )
            ],
        ),
    ]

    total_start = time.time()
    downloader = Downloader(
        county_downloads=downloads,
        download_destination_path=DATABASE_DESTINATION_PATH,
    )

    logging.info(f"Total time elapsed: {time.time() - total_start} seconds")
