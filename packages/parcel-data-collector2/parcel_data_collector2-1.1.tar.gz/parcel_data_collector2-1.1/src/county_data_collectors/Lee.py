"""Lee County Data Collector"""
import os

import pandas as pd

from ..constants import DATABASE_DESTINATION_PATH, DATABASE_SUFFIX
from .base_collector import BaseParcelDataCollector


class Lee(BaseParcelDataCollector):
    """Lee County Data Collector class.

    Args:
        BaseParcelDataCollector (ABC): Abstract base class for parcel
            data collectors.
    """

    COUNTY = "Lee"
    LINKS = {
        "PROPERTY_APPRAISER": "https://www.leepa.org/Display/DisplayParcel.aspx\
?FolioID={PARCEL_ID}&LegalDetails=True",
        "DEED": "https://or.leeclerk.org/LandMarkWeb/Document/GetDocumentByCFN\
/?cfn={OR_INST}",
        "OLD_DEED": "https://or.leeclerk.org/LandmarkWeb/Document/GetDocument\
ByBookPage/?booktype=OR&Booknumber={OR_BOOK}&Pagenumber={OR_PAGE}",
        "MAP": "https://gissvr.leepa.org/geoview2/?folioid={PARCEL_ID}",
        "SUBDIV_PLAT": "",
        "CONDO_PLAT": "",
    }

    MAIN_DATAFRAME_PATH = os.path.join(
        DATABASE_DESTINATION_PATH, f"{COUNTY}{DATABASE_SUFFIX}"
    )
    MAIN_DATAFRAME = pd.read_feather(MAIN_DATAFRAME_PATH)
    MAIN_DATAFRAME["FOLIOID"] = MAIN_DATAFRAME["FOLIOID"].str.replace(".0", "")

    COLUMN_MAP = {
        "PARCEL_ID": "FOLIOID",
        "PRIMARY_ADDRESS": "SITEADDR",
        "PROP_HN": "SITENUMBER",
        "POSTAL_STREET": "SITESTREET",
        "PROP_ZIP": "SITEZIP",
        "PROP_CITY": "SITECITY",
        "OWNER": "O_NAME",
        "LEGAL_DESC": "LEGAL",
        "LOT": "LOT",
        "BLOCK": "BLOCK",
        "ACRES": "GISACRES",
        "OR_INST": "S_1OR_NUM",
    }

    def __init__(self, parcel_id: str):
        super().__init__(parcel_id)
        self.county = Lee.COUNTY
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
        parcel_data["BLOCK"] = parcel_data["BLOCK"].lstrip("0")
        parcel_data["PLAT_TYPE"] = self.get_plat_type(parcel_data)
        parcel_data["UNIT"] = ""
        parcel_data["POSTAL_SUFF"] = ""
        parcel_data["PLAT_BOOK"] = ""
        parcel_data["PLAT_PAGE"] = ""
        parcel_data["SUBDIVISION"] = ""
        parcel_data["PROP_DIR"] = ""

        if parcel_data["PLAT_TYPE"] == "SUBDIVISION":
            if self.parcel_row["CONDOTYPE"].values[0].lower() == "c":
                parcel_data["PLAT_TYPE"] = "CONDOMINIUM"

        parcel_data.update(self.get_or_date(parcel_data))
        parcel_data["PRIMARY_ADDRESS"] = self.get_primary_address(parcel_data)
        parcel_data["LINKS"] = self.get_parcel_links(self.LINKS, parcel_data)

        return parcel_data

    def get_subdivision_data(self, parcel_data: dict) -> dict:
        """Retrieves the subdivision data from the parcel data.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            dict: The subdivision data.
        """
        stripped_length = len(parcel_data["LOT"].lstrip("0"))
        if stripped_length == 2:
            parcel_data["LOT"] = parcel_data["LOT"][2]
        elif stripped_length == 3:
            parcel_data["LOT"] = parcel_data["LOT"][1:3]
        else:
            parcel_data["LOT"] = parcel_data["LOT"].rstrip("0")
        return parcel_data

    def get_or_date(self, parcel_data: dict) -> dict:
        """Retrieves the OR date from the parcel data.

        Args:
            parcel_data (dict): The parcel data.

        Returns:
            dict: The OR date.
        """
        or_data = {
            "OR_BOOK": "",
            "OR_PAGE": "",
            "OR_INST": "",
        }

        if "-B" in parcel_data["OR_INST"]:
            or_data["OR_BOOK"] = (
                parcel_data["OR_INST"].split("-")[1].lstrip("B").lstrip("0")
            )
            or_data["OR_PAGE"] = (
                parcel_data["OR_INST"].split("-")[-2].lstrip("P").lstrip("0")
            )
            or_data["OR_INST"] = ""

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
    lee = Lee("10473880")
    print(lee.parcel_data)
    print(lee.PARCEL_SCHEMA.keys() - lee.parcel_data.keys())
