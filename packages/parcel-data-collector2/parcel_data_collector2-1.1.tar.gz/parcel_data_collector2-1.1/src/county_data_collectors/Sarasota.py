"""Sarasota County Data Collector"""
import os

import pandas as pd

from ..constants import DATABASE_DESTINATION_PATH
from .base_collector import BaseParcelDataCollector


class Sarasota(BaseParcelDataCollector):
    """Sarasota County Data Collector class.

    Args:
        BaseParcelDataCollector (ABC): Abstract base class for parcel
            data collectors.
    """

    LINKS = {
        "PROPERTY_APPRAISER": "https://www.sc-pa.com/propertysearch/\
parcel/details/{PARCEL_ID}",
        "DEED": "https://secure.sarasotaclerk.com/viewtiff.aspx?intrnum\
={OR_INST}",
        "OLD_DEED": "https://secure.sarasotaclerk.com/viewtiff.aspx?\
book={OR_BOOK}&page={OR_PAGE}",
        "MAP": "https://ags3.scgov.net/scpa/?esearch={PARCEL_ID}&slayer=0",
        "SUBDIV_PLAT": "https://secure.sarasotaclerk.com/ViewTiff.aspx?\
intrnum=SUBDIVBK{PLAT_BOOK}PG{PLAT_PAGE}",
        "CONDO_PLAT": "https://secure.sarasotaclerk.com/ViewTiff.aspx?\
intrnum=CONDOBK{PLAT_BOOK}PG{PLAT_PAGE}",
    }

    MAIN_DATAFRAME_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, "Sarasota_Parcels.feather"
    )
    MAIN_DATAFRAME = pd.read_feather(MAIN_DATAFRAME_PATH)

    SUBDIVISION_LOOKUP_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, "SubDivisionIndex.feather"
    )
    SUBDIVISION_LOOKUP_DF = pd.read_feather(SUBDIVISION_LOOKUP_PATH)

    COLUMN_MAP = {
        "PARCEL_ID": "ID",
        "PRIMARY_ADDRESS": "FULLADDRESS",
        "PROP_HN": "LOCN",
        "POSTAL_STREET": "LOCS",
        "POSTAL_SUFF": "LOCD_SUFFIX",
        "PROP_DIR": "LOCD",
        "PROP_CITY": "LOCCITY",
        "PROP_ZIP": "LOCZIP",
        "LOT": "LOT",
        "BLOCK": "BLOCK",
        "UNIT": "UNIT",
        "SUBDIVISION": "SUBD",
        "OWNER": "NAME1",
        "LEGAL_DESC": "LEGAL1",
        "OR_BOOK": "OR_BOOK",
        "OR_PAGE": "OR_PAGE",
        "OR_INST": "LEGALREFER",
    }

    def __init__(self, parcel_id: str):
        super().__init__(parcel_id)
        self.county = "Sarasota"
        self.parcel_row = self.get_parcel_row(self.MAIN_DATAFRAME, "ID")
        self.parcel_data = self.get_parcel_data()

    def get_parcel_data(self) -> dict:
        """Retrieves the parcel data from the source.

        Returns:
            dict: The parcel data.
        """
        parcel_data: dict = {"COUNTY": self.county}
        for key, column_name in self.COLUMN_MAP.items():
            parcel_data[key] = self.get_attribute(column_name, self.parcel_row)
        parcel_data.update(self.get_subdivision_data(parcel_data))
        parcel_data["ACRES"] = self.get_acreage()

        data_to_format = [
            "LOT",
            "BLOCK",
            "OR_BOOK",
            "OR_PAGE",
            "PLAT_BOOK",
            "PLAT_PAGE",
        ]
        for data in data_to_format:
            parcel_data[data] = parcel_data[data].lstrip("0")

        parcel_data["PLAT_TYPE"] = self.get_plat_type(parcel_data)
        parcel_data["PRIMARY_ADDRESS"] = self.get_primary_address(parcel_data)
        parcel_data["POSTAL_STREET"] = self.get_street_address(parcel_data)
        parcel_data["LINKS"] = self.get_parcel_links(self.LINKS, parcel_data)

        return parcel_data

    def get_subdivision_data(self, parcel_data: dict) -> dict:
        """Retrieves the subdivision data from the parcel data.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            dict: The subdivision data.
        """
        subdivision_data = {"SUBDIVISION": "", "PLAT_BOOK": "", "PLAT_PAGE": ""}
        subdivision_key = parcel_data["SUBDIVISION"]

        subdivision = self.SUBDIVISION_LOOKUP_DF.loc[
            self.SUBDIVISION_LOOKUP_DF["Number"] == subdivision_key
        ]
        subdivision_data["SUBDIVISION"] = subdivision["Name"].values[0]
        subdivision_data["PLAT_BOOK"] = subdivision["PlatBk1"].values[0]
        subdivision_data["PLAT_PAGE"] = subdivision["PlatPg1"].values[0]

        return subdivision_data

    def get_subdivision_lookup(self) -> pd.DataFrame:
        """Retrieves the subdivision lookup table.

        Returns:
            pd.DataFrame: The subdivision lookup table.
        """
        return pd.read_feather(self.SUBDIVISION_LOOKUP_PATH)

    def get_acreage(self) -> str:
        """Retrieves the acreage from the parcel data.

        Returns:
            str: The acreage.
        """
        return str(float(self.parcel_row["LSQFT"].values[0]) / 43560)

    def get_primary_address(self, parcel_data: dict) -> str:
        """Formats the primary address.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            str: The primary address.
        """
        primary_address = parcel_data.get("PRIMARY_ADDRESS", "")
        primary_address = primary_address.replace(" FL,", ", FL")
        city = parcel_data.get("PROP_CITY", "")
        primary_address = primary_address.replace(f" {city}", f", {city}")
        return primary_address

    def get_street_address(self, parcel_data: dict) -> str:
        """Formats the street address.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            str: The street address.
        """
        primary_address = parcel_data.get("PRIMARY_ADDRESS", "")
        house_number = parcel_data.get("PROP_HN", "")
        city = parcel_data.get("PROP_CITY", "")
        street = (
            primary_address.split(house_number)[-1]
            .split(city)[0]
            .replace(",", "")
            .strip()
        )
        return street


if __name__ == "__main__":
    sarasota = Sarasota("0103111224")
    print(sarasota.parcel_row.columns)
    print(sarasota.parcel_data)
    print(sarasota.PARCEL_SCHEMA.keys() - sarasota.parcel_data.keys())
