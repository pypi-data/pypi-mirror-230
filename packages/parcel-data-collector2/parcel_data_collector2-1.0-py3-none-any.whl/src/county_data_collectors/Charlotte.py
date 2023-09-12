"""Charlotte County Data Collector"""
import logging
import os

import pandas as pd

from ..constants import DATABASE_DESTINATION_PATH, DATABASE_SUFFIX
from .base_collector import BaseParcelDataCollector


class Charlotte(BaseParcelDataCollector):
    """Charlotte County Data Collector class.

    Args:
        BaseParcelDataCollector (ABC): Abstract base class for parcel
            data collectors.
    """

    COUNTY = "Charlotte"
    LINKS = {
        "PROPERTY_APPRAISER": "https://www.ccappraiser.com/Show_Parcel.asp?acct\
={PARCEL_ID}%20%20&gen=T&tax=T&bld=T&oth=T&sal=T&lnd=T&leg=T",
        "DEED": "",
        "OLD_DEED": "",
        "MAP": "https://agis.charlottecountyfl.gov/ccgis/?acct={PARCEL_ID}",
        "SUBDIV_PLAT": "https://clerkportal.charlotteclerk.com/PlatCondo/\
PlatCondoIndex",
        "CONDO_PLAT": "https://clerkportal.charlotteclerk.com/PlatCondo/\
PlatCondoIndex",
    }

    MAIN_DATAFRAME_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, f"{COUNTY}{DATABASE_SUFFIX}"
    )
    MAIN_DATAFRAME = pd.read_feather(MAIN_DATAFRAME_PATH)
    print(MAIN_DATAFRAME.columns)

    SUBDIVISION_LOOKUP_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, "CharlotteSubdivisions.feather"
    )
    SUBDIVISION_LOOKUP_DF = pd.read_feather(SUBDIVISION_LOOKUP_PATH)

    CONDOMINIUM_LOOKUP_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, "CharlotteCondominiums.feather"
    )
    CONDOMINIUM_LOOKUP_DF = pd.read_feather(CONDOMINIUM_LOOKUP_PATH)

    MISC_LOOKUP_PATH = os.path.join(DATABASE_DESTINATION_PATH, "cd.feather")
    MISC_LOOKUP_DF = pd.read_feather(MISC_LOOKUP_PATH)
    print(MISC_LOOKUP_DF.columns)

    COLUMN_MAP = {
        "PARCEL_ID": "ACCOUNT",
        "PRIMARY_ADDRESS": "FullPropertyAddress",
        "PROP_HN": "streetnumber",
        "POSTAL_STREET": "propertyaddress",
        "PROP_ZIP": "zipcode",
        "OWNER": "ownersname",
        "LEGAL_DESC": "shortlegal",
    }

    def __init__(self, parcel_id: str):
        super().__init__(parcel_id)
        self.county = Charlotte.COUNTY
        self.parcel_row = self.get_parcel_row(
            self.MAIN_DATAFRAME, self.COLUMN_MAP["PARCEL_ID"]
        )
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
        parcel_data.update(self.get_or_data())
        parcel_data["PLAT_TYPE"] = self.get_plat_type(parcel_data)
        while "  " in parcel_data["PRIMARY_ADDRESS"]:
            parcel_data["PRIMARY_ADDRESS"] = parcel_data[
                "PRIMARY_ADDRESS"
            ].replace("  ", " ")
        parcel_data["PLAT_BOOK"] = ""
        parcel_data["PLAT_PAGE"] = ""
        parcel_data["POSTAL_SUFF"] = ""
        parcel_data["PROP_DIR"] = ""
        parcel_data["UNIT"] = ""
        parcel_data["PRIMARY_ADDRESS"] = self.get_primary_address(parcel_data)
        parcel_data["LINKS"] = self.get_parcel_links(self.LINKS, parcel_data)

        return parcel_data

    def get_subdivision_data(self, parcel_data) -> dict:
        """Retrieves the subdivision data from the parcel data.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            dict: The subdivision data.
        """
        parcel_data["SUBDIVISION"] = parcel_data["LEGAL_DESC"][:3]
        subdivision_data = {"SUBDIVISION": "", "PLAT_TYPE": ""}
        subdivision_key = parcel_data["SUBDIVISION"]

        subdivision = self.SUBDIVISION_LOOKUP_DF.loc[
            self.SUBDIVISION_LOOKUP_DF["Designator"] == subdivision_key
        ]

        sub_data_schema = {
            "SUBDIVISION": "Subdivision Name",
            "PLAT_TYPE": "Type",
        }

        for parcel_key, subdivision_key in sub_data_schema.items():
            try:
                subdivision_data[parcel_key] = subdivision[
                    subdivision_key
                ].values[0]
            except IndexError as e:
                logging.warning(f"Failed to retrieve {parcel_key}: {e}")

        if subdivision_key.upper() != "ZZZ":
            subdivision_data["LOT"] = (
                parcel_data["LEGAL_DESC"].split()[-1].lstrip("0")
            )
            subdivision_data["BLOCK"] = (
                parcel_data["LEGAL_DESC"].split()[-2].lstrip("0")
            )
        else:
            subdivision_data["LOT"] = ""
            subdivision_data["BLOCK"] = ""

        return subdivision_data

    def get_or_data(self) -> dict:
        """Retrieves the OR data from the parcel data.

        Returns:
            dict: The OR data.
        """
        parcel_row = self.get_parcel_row(self.MISC_LOOKUP_DF, "account")
        print(parcel_row)
        or_data = {
            "PROP_CITY": "",
            "OR_BOOK": "",
            "OR_PAGE": "",
            "OR_INST": "",
            "ACRES": "",
        }
        or_data["PROP_CITY"] = parcel_row["city"].values[0]
        or_data["OR_BOOK"] = parcel_row["SaleBook"].values[0]
        or_data["OR_PAGE"] = parcel_row["SalePage"].values[0]
        or_data["OR_INST"] = parcel_row["InstrumentNumber"].values[0]
        or_data["ACRES"] = str(float(parcel_row["totalarea"].values[0]) / 43560)
        return or_data

    def get_primary_address(self, parcel_data: dict) -> str:
        """Formats the primary address.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            str: The primary address.
        """
        primary_address = parcel_data.get("PRIMARY_ADDRESS", "")
        state = "FL"
        city = parcel_data.get("PROP_CITY", "")
        zip_code = parcel_data.get("PROP_ZIP", "")
        return f"{primary_address}, {city}, {state} {zip_code}"


if __name__ == "__main__":
    charlotte = Charlotte("412001405018 ")
    print(charlotte.parcel_data)
    print(charlotte.PARCEL_SCHEMA.keys() - charlotte.parcel_data.keys())
