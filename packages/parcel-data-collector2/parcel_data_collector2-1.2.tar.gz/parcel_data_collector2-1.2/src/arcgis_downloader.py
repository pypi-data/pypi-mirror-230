"""This module will focus on downloading, formatting and storing Florida
County Parcel databases from ARCGIS."""
import logging
import os
import time
from typing import Dict, Optional, Union

import pandas as pd
from arcgis.gis import GIS, Item

from constants import (
    ARCGIS_PASSWORD,
    ARCGIS_USERNAME,
    COUNTY_FIELDS,
    DATABASE_DESTINATION_PATH,
    CountyFields,
)


class ARCGISDownloader:
    """Downloads County Parcel database files from the ARCGIS portal."""

    def __init__(
        self,
        counties: Dict[str, CountyFields] = COUNTY_FIELDS,
        username: str = "",
        password: str = "",
        download_destination_path: str = DATABASE_DESTINATION_PATH,
    ):
        self.counties = counties
        self.username = username
        self.password = password
        self.download_destination_path = download_destination_path
        self.gis_connection = self.connect_to_argis()

    def connect_to_argis(self) -> Optional[GIS]:
        """Connects to ArcGIS.

        Returns:
            Optional[GIS]: The ArcGIS connection object.
        """
        try:
            gis = GIS(username=self.username, password=self.password)
            logging.info(
                f"Successfully logged in as: {gis.properties.user.username}"
            )
            return gis

        except Exception as e:
            logging.error(f"Failed to connect to ArcGIS: {e}")

    def retrive_arcgis_dataset(self, dataset_id: str) -> Optional[Item]:
        """Retrieves an ArcGIS dataset Item object.

        Args:
            dataset_id (str): The ID of the dataset to retrieve.

        Returns:
            Optional[Item]: The dataset Item object.
        """

        if self.gis_connection is None:
            logging.warning("No ArcGIS connection established")
            return None

        try:
            dataset_item = self.gis_connection.content.get(dataset_id)
            logging.info(f"Dataset item {dataset_item} retrieved successfully")
            return dataset_item
        except Exception as e:
            logging.error(f"Failed to retrieve dataset item: {e}")

    def download_arcgis_county_data(self, county) -> None:
        """Downloads the ArcGIS county data.

        Args:
            county (str): The county to download.
        """
        dataset_id = self.counties[county].arcgis_id
        dataset_item = self.retrive_arcgis_dataset(dataset_id)

        if not self.valid_dataset_item(dataset_item):
            return

        df = self.get_dataset_dataframe(dataset_item, county)  # type: ignore
        df = self.format_dataframe(df)
        self.export_dataframe(df, county)

    def valid_dataset_item(self, dataset_item: Union[Item, None]) -> bool:
        """Verifies that the dataset item is valid.

        Args:
            dataset_item (Union[Item, None]): The dataset item to verify.

        Returns:
            bool: Whether the dataset item is valid.
        """
        if dataset_item is None:
            logging.warning("No dataset item retrieved")
            return False
        elif isinstance(dataset_item, Item):
            return True
        else:
            logging.warning("Invalid dataset item retrieved")
            return False

    def get_dataset_dataframe(
        self,
        dataset_item: Item,
        county: str,
    ) -> pd.DataFrame:
        """Gets the dataset dataframe.

        Args:
            dataset_item (Item): The dataset item to get the dataframe
                from.
            county (str): The county to get the dataframe from.

        Returns:
            pd.DataFrame: The dataset dataframe.
        """

        try:
            data_layer = dataset_item.layers[0]  # type: ignore
            logging.info(f"Layer {data_layer} retrieved successfully")
        except Exception as e:
            logging.error(
                f"Failed to get data layer from dataset item {dataset_item}:\
 {e}"
            )
            return pd.DataFrame()

        query_fields = self.counties[county].fields
        try:
            query_result = data_layer.query(
                out_fields=query_fields, return_geometry=False
            )
            logging.info(f"Query with fields {query_fields} successful")
        except Exception as e:
            logging.error(f"Failed to query layer: {e}")
            logging.debug(f"Query fields: {query_fields}")
            return pd.DataFrame()

        try:
            df = query_result.sdf
            logging.info("Conversion to DataFrame successful")
            logging.info(f"DataFrame shape: {df.shape}")
            logging.info(f"DataFrame columns: {df.columns}")
            logging.info(f"DataFrame head: {df.head()}")
            return df
        except Exception as e:
            logging.error(f"Failed to convert query result to DataFrame: {e}")
            logging.debug(f"Query result: {query_result}")
            return pd.DataFrame()

    def safe_str_convert(self, x) -> str:
        """Safely converts x to a string.

        Args:
            x: The object to convert to a string.

        Returns:
            str: The string representation of x.
        """
        return str(x) if x is not None else ""

    def format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formats the dataframe.

        Args:
            df (pd.DataFrame): The dataframe to format.

        Returns:
            pd.DataFrame: The formatted dataframe.
        """
        try:
            """
            ObjectID is not needed. It is included by default in the
            ArcGIS dataset, but it is not included in the dataset fields
            list.
            """
            df.drop(columns=["OBJECTID"], inplace=True)
            logging.info("Dropped OBJECTID column")
        except Exception as e:
            logging.error(f"Failed to drop OBJECTID column: {e}")

        try:
            df = df.applymap(self.safe_str_convert)
            logging.info("Converted all values to strings")
        except Exception as e:
            logging.error(f"Failed to convert all values to strings: {e}")

        try:
            df = df.applymap(lambda x: x.replace("<NA>", ""))
            logging.info("Replaced all <NA> values with empty strings")
            for column in df.columns:
                df[column] = df[column].str.strip()
            logging.info("Stripped all whitespace from column values")
        except Exception as e:
            logging.error(
                f"Failed to replace all <NA> values with empty strings: {e}"
            )

        return df

    def export_dataframe(self, df: pd.DataFrame, county: str) -> None:
        """Exports the dataframe to a feather file.

        Args:
            df (pd.DataFrame): The dataframe to export.
            county (str): The county to export.
        """
        dataset_name = county + "_Parcels.feather"
        final_dataframe_path = os.path.join(
            self.download_destination_path, dataset_name
        )
        try:
            df.to_feather(final_dataframe_path)
            logging.info(f"Successfully exported {dataset_name} to feather")
        except Exception as e:
            logging.error(f"Failed to export {dataset_name} to feather: {e}")


if __name__ == "__main__":
    # logging.basicConfig(filename="log.txt", filemode="w", level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    downloader = ARCGISDownloader(
        COUNTY_FIELDS,
        ARCGIS_USERNAME,
        ARCGIS_PASSWORD,
        DATABASE_DESTINATION_PATH,
    )

    total_start = time.time()

    for county in COUNTY_FIELDS:
        start = time.time()
        logging.info(f"Downloading {county} data")
        downloader.download_arcgis_county_data(county)

        logging.info(f"Finished downloading {county} data")
        logging.info(f"Time elapsed: {time.time() - start} seconds")

    logging.info(f"Total time elapsed: {time.time() - total_start} seconds")
