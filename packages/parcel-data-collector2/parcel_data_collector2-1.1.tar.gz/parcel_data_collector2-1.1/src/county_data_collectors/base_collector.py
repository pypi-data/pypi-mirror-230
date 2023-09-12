"""This module contains the abstract base class for all parcel data collectors.
It includes the abstract methods and attributes that all parcel data collectors
must implement."""
import logging
import os
from abc import ABC, abstractmethod

import pandas as pd

from ..constants import DATABASE_DESTINATION_PATH, DATABASE_SUFFIX

logging.basicConfig(
    filename="DataCollectorsLog.log", filemode="w", level=logging.INFO
)


class BaseParcelDataCollector(ABC):
    PARCEL_SCHEMA = {
        "PARCEL_ID": str,
        "COUNTY": str,
        "PRIMARY_ADDRESS": str,
        "PROP_HN": str,
        "POSTAL_STREET": str,
        "POSTAL_SUFF": str,
        "PROP_DIR": str,
        "PROP_CITY": str,
        "PROP_ZIP": str,
        "LOT": str,
        "BLOCK": str,
        "UNIT": str,
        "SUBDIVISION": str,
        "ACRES": float,
        "OWNER": str,
        "LEGAL_DESC": str,
        "PLAT_BOOK": str,
        "PLAT_PAGE": str,
        "OR_BOOK": str,
        "OR_PAGE": str,
        "OR_INST": str,
        "PLAT_TYPE": str,
        "LINKS": dict,
    }

    LINKS_SCHEMA = {
        "PROPERTY_APPRAISER": "",
        "DEED": "",
        "OLD_DEED": "",
        "MAP": "",
        "SUBDIV_PLAT": "",
        "CONDO_PLAT": "",
        "PLAT": "",
        "FEMA": "",
    }

    def __init__(self, parcel_id: str):
        if not isinstance(parcel_id, str):
            raise TypeError(
                f"parcel_id must be a string, not {type(parcel_id)}"
            )
        self.parcel_id = parcel_id.strip()
        self.county = None

    @abstractmethod
    def get_parcel_data(self) -> dict:
        """Retrieves the parcel data from the source.

        Returns:
            dict: The parcel data.
        """
        pass

    def get_attribute(
        self,
        column: str,
        parcel_row: pd.DataFrame,
    ) -> str:
        """Retrieves an attribute from the parcel data.

        Args:
            column (str): The column to retrieve.
            parcel_row (pd.DataFrame): The parcel row.

        Returns:
            str: The attribute.
        """
        try:
            attribute = parcel_row[column].values[0]
            logging.info(f"Successfully retrieved {column} from parcel data")
            return attribute
        except Exception as e:
            logging.warning(
                f"Failed to retrieve {column} from parcel data: {e}"
            )
        return ""

    def get_dataframe_path(self) -> str:
        """Retrieves the dataframe path.

        Returns:
            str: The dataframe path.
        """
        return os.path.join(
            DATABASE_DESTINATION_PATH, f"{self.county}{DATABASE_SUFFIX}"
        )

    def get_parcel_row(
        self, dataframe: pd.DataFrame, parcel_id_col: str
    ) -> pd.DataFrame:
        """Retrieves the parcel row from the database.

        Args:
            dataframe (pd.DataFrame): The database.

        Returns:
            pd.DataFrame: The parcel row.
        """
        try:
            row = dataframe.loc[dataframe[parcel_id_col] == self.parcel_id]
            logging.info(f"Successfully retrieved parcel row: {row}")
            return row
        except Exception as e:
            logging.warning(f"Failed to retrieve parcel row: {e}")
        return pd.DataFrame()

    def get_plat_type(self, parcel_data: dict) -> str:
        """Retrieves the plat type from the parcel.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            str: The plat type.
        """
        if parcel_data.get("LOT", ""):
            return "SUBDIVISION"
        elif parcel_data.get("UNIT", ""):
            return "CONDOMINIUM"
        else:
            return "UNPLATTED"

    def get_parcel_links(self, links: dict, parcel_data: dict) -> dict:
        """Retrieves the parcel links from the parcel data.

        Args:
            links (dict): The links.
            parcel_data (dict): The parcel data.

        Returns:
            dict: The parcel links.
        """
        parcel_links = {}

        for link_type, url in links.items():
            parcel_links[link_type] = url.format(**parcel_data)

        plat_type = parcel_data.get("PLAT_TYPE", "")
        if plat_type == "CONDOMINIUM":
            parcel_links["PLAT"] = parcel_links.get("CONDO_PLAT", "")
        elif plat_type == "SUBDIVISION":
            parcel_links["PLAT"] = parcel_links.get("SUBDIV_PLAT", "")
        else:
            parcel_links["PLAT"] = ""

        parcel_links["FEMA"] = self.get_fema_link(parcel_data)

        return parcel_links

    def get_fema_link(self, parcel_data: dict) -> str:
        """Retrieves the FEMA link from the parcel data.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            str: The FEMA link.
        """
        fema_url = "https://msc.fema.gov/portal/search?AddressQuery={}"
        address = parcel_data.get("PRIMARY_ADDRESS", "")
        if not address:
            return ""
        formatted_address = address.replace(" ", "%20").replace(",", "%2C")
        return fema_url.format(formatted_address)
