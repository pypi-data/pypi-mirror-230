import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

# Environmental variables from .env file
ENV_FILE = ".env"
load_dotenv(ENV_FILE)
ARCGIS_USERNAME = os.getenv("ARCGIS_USERNAME", default="")
ARCGIS_PASSWORD = os.getenv("ARCGIS_PASSWORD", default="")


# Database storage path
SERVER_PATH = "\\\\server"
ACCESS_PATH = os.path.join(SERVER_PATH, "access")
DATABASE_DESTINATION_PATH = os.path.join(ACCESS_PATH, "County Parcel Databases")
DATABASE_SUFFIX = "_Parcels.feather"

if not os.path.exists(DATABASE_DESTINATION_PATH):
    os.makedirs(DATABASE_DESTINATION_PATH, exist_ok=True)

# Miscellaneous zipped files to download
TEMP_DOWNLOAD_PATH = os.path.join(DATABASE_DESTINATION_PATH, "temp")


# County Parcel databases.
@dataclass
class CountyFields:
    county: str
    arcgis_id: str
    fields: List[str]

    def __str__(self):
        return f"CountyFields({self.county}, {self.arcgis_id}, {self.fields})"


COUNTY_FIELDS = {
    "Sarasota": CountyFields(
        "Sarasota",
        "7c5f7cddd7c644e4ab6ba99580e53437",
        [
            "ID",
            "NAME1",
            "LOCN",
            "LOCN_SUFFIX",
            "LOCD",
            "LOCS",
            "LOCT",
            "LOCD_SUFFIX",
            "UNIT",
            "LOCCITY",
            "LOCZIP",
            "FullAddress",
            "SUBD",
            "MUNICIPALITY",
            "SECT",
            "TWSP",
            "RANG",
            "BLOCK",
            "LOT",
            "ZONING",
            "OR_BOOK",
            "OR_PAGE",
            "LEGALREFER",
            "LEGAL1",
            "LSQFT",
        ],
    ),
    "Manatee": CountyFields(
        "Manatee",
        "cb02869c8f0346418252ae6bd37b34cd",
        [
            "PARCEL_ID",
            "PRIMARY_ADDRESS",
            "PROP_HN",
            "POSTAL_STREET",
            "POSTAL_SUFF",
            "PROP_DIR",
            "PROP_CITYNAME",
            "PROP_ZIP",
            "OWNER",
            "SUBDIVISION",
            "ACRES",
            "LUC_DESCRIPTION",
            "ZONING",
            "SEC",
            "TWN",
            "RNG",
            "FLOOD_ZONE",
            "FLOOD_MAP",
            "UNIT",
            "LOT",
            "BLOCK",
            "PARENT_PARID",
        ],
    ),
    "Charlotte": CountyFields(
        "Charlotte",
        "492b126174e04ac998b7f989fc80ee8f",
        [
            "ACCOUNT",
            "ownersname",
            "zipcode",
            "streetnumber",
            "propertyaddress",
            "twprngsec",
            "landuse",
            "zoningcode",
            "description",
            "shortlegal",
            "AccountLink",
            "CONDOID",
            "FullPropertyAddress",
        ],
    ),
    "Lee": CountyFields(
        "Lee",
        "cca8b85e195f48d48634a5f562548030",
        [
            "STRAP",
            "BLOCK",
            "LOT",
            "FOLIOID",
            "CONDOTYPE",
            "GISACRES",
            "ZONING",
            "LANDUSEDES",
            "LANDISON",
            "SITEADDR",
            "SITENUMBER",
            "SITESTREET",
            "SITEUNIT",
            "SITECITY",
            "SITEZIP",
            "LAND",
            "BUILDING",
            "O_NAME",
            "LEGAL",
            "Property_URL",
            "S_1OR_NUM",
        ],
    ),
}
