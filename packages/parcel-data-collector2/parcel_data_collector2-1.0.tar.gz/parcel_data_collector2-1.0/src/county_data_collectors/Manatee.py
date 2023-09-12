"""Manatee County Data Collector"""
import logging
import os

import pandas as pd

from ..constants import DATABASE_DESTINATION_PATH, DATABASE_SUFFIX
from .base_collector import BaseParcelDataCollector


class Manatee(BaseParcelDataCollector):
    """Manatee County Data Collector class.

    Args:
        BaseParcelDataCollector (ABC): Abstract base class for parcel
            data collectors.
    """

    COUNTY = "Manatee"
    LINKS = {
        "PROPERTY_APPRAISER": "https://www.manateepao.gov/parcel/?parid=\
{PARCEL_ID}",
        "DEED": "https://records.manateeclerk.com/OfficialRecords/Search\
/InstrumentNumber?instrumentNumber={OR_INST}",
        "OLD_DEED": "https://records.manateeclerk.com/OfficialRecords/\
Search/InstrumentBookPage/{OR_BOOK}/{OR_PAGE}",
        "MAP": "",
        "SUBDIV_PLAT": "https://records.manateeclerk.com/PlatRecords/\
Search/Results?searchType=plat&platBook={PLAT_BOOK}&platPage={PLAT_PAGE}",
        "CONDO_PLAT": "https://records.manateeclerk.com/PlatRecords/\
Search/Results?searchType=condo&platBook={PLAT_BOOK}&platPage={PLAT_PAGE}",
    }

    MAIN_DATAFRAME_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, f"{COUNTY}{DATABASE_SUFFIX}"
    )
    MAIN_DATAFRAME = pd.read_feather(MAIN_DATAFRAME_PATH)

    SUBDIVISION_LOOKUP_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, "ManateeSubdivisions.feather"
    )
    SUBDIVISION_LOOKUP_DF = pd.read_feather(SUBDIVISION_LOOKUP_PATH)

    MISC_LOOKUP_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, "manatee_ccdf.feather"
    )
    MISC_LOOKUP_DF = pd.read_feather(MISC_LOOKUP_PATH)

    COLUMN_MAP = {
        "PARCEL_ID": "PARCEL_ID",
        "PRIMARY_ADDRESS": "PRIMARY_ADDRESS",
        "PROP_HN": "PROP_HN",
        "POSTAL_STREET": "POSTAL_STREET",
        "POSTAL_SUFF": "POSTAL_SUFF",
        "PROP_DIR": "PROP_DIR",
        "PROP_CITY": "PROP_CITYNAME",
        "PROP_ZIP": "PROP_ZIP",
        "LOT": "LOT",
        "BLOCK": "BLOCK",
        "UNIT": "UNIT",
        "SUBDIVISION": "SUBDIVISION",
        "OWNER": "OWNER",
    }

    def __init__(self, parcel_id: str):
        super().__init__(parcel_id)
        self.county = Manatee.COUNTY
        self.parcel_row = self.get_parcel_row(self.MAIN_DATAFRAME, "PARCEL_ID")
        self.parcel_data = self.get_parcel_data()

    def get_parcel_data(self) -> dict:
        """Retrieves the parcel data from the source.

        Returns:
            dict: The parcel data.
        """
        parcel_data: dict = {"COUNTY": self.county}
        for key, column_name in self.COLUMN_MAP.items():
            parcel_data[key] = self.get_attribute(column_name, self.parcel_row)
        parcel_data.update(self.get_subdivision_data())
        parcel_data.update(self.get_or_data())
        parcel_data["PLAT_TYPE"] = self.get_plat_type(parcel_data)
        parcel_data["PRIMARY_ADDRESS"] = self.get_primary_address(parcel_data)
        parcel_data["POSTAL_STREET"] = self.get_street_address(parcel_data)
        parcel_data["LINKS"] = self.get_parcel_links(self.LINKS, parcel_data)
        return parcel_data

    def get_subdivision_data(self) -> dict:
        """Retrieves the subdivision data from the parcel data.

        Returns:
            dict: The subdivision data.
        """
        parcel_row = self.get_parcel_row(self.MISC_LOOKUP_DF, "PARID")
        subdivision_data = {"SUBDIVISION": "", "PLAT_BOOK": "", "PLAT_PAGE": ""}
        subdivision_key = parcel_row["PAR_SUBDIVISION"].values[0]

        subdivision = self.SUBDIVISION_LOOKUP_DF.loc[
            self.SUBDIVISION_LOOKUP_DF["SUBDNUM"] == subdivision_key
        ]

        sub_data_schema = {
            "SUBDIVISION": "NAME",
            "PLAT_BOOK": "BOOK",
            "PLAT_PAGE": "PAGE",
        }

        for parcel_key, subdivision_key in sub_data_schema.items():
            try:
                subdivision_data[parcel_key] = subdivision[
                    subdivision_key
                ].values[0]
            except IndexError as e:
                logging.warning(f"Failed to retrieve {parcel_key}: {e}")

        return subdivision_data

    def get_or_data(self) -> dict:
        """Retrieves the OR data from the parcel data.

        Returns:
            dict: The OR data.
        """
        parcel_row = self.get_parcel_row(self.MISC_LOOKUP_DF, "PARID")
        or_data = {
            "OR_BOOK": "",
            "OR_PAGE": "",
            "OR_INST": "",
            "LEGAL_DESC": "",
            "ACRES": "",
        }
        or_data["OR_BOOK"] = parcel_row["SALE_BOOK_LAST"].values[0]
        or_data["OR_PAGE"] = parcel_row["SALE_PAGE_LAST"].values[0]
        or_data["OR_INST"] = parcel_row["SALE_INSTRNO_LAST"].values[0]
        or_data["LEGAL_DESC"] = parcel_row["PAR_LEGAL1"].values[0]
        or_data["ACRES"] = str(
            float(parcel_row["LAND_SQFT_CAMA"].values[0]) / 43560
        )
        return or_data

    def get_primary_address(self, parcel_data: dict) -> str:
        """Formats the primary address.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            str: The primary address.
        """
        address = parcel_data.get("PRIMARY_ADDRESS", "")
        city = parcel_data.get("PROP_CITY", "")
        state = "FL"
        zip_code = parcel_data.get("PROP_ZIP", "")
        return f"{address}, {city}, {state} {zip_code}"

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
    manatee = Manatee("1545112459 ")
    print(manatee.parcel_data)
    print(manatee.PARCEL_SCHEMA.keys() - manatee.parcel_data.keys())
