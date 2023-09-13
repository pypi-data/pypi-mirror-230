from dataclasses import dataclass, field
from typing import List


@dataclass
class CountyDownload:
    """Represents a county dataframe download Baseclass."""

    county: str
    url: str
    file_name: str


@dataclass
class Dataframe:
    """Represents a dataframe file."""

    file_name: str
    delimiter: str = ","
    columns: List[str] = field(default_factory=list)


@dataclass
class ZipDownload(CountyDownload):
    """Represents a county dataframe download that is a zip file.
    Inherits from CountyDownload."""

    files: List[Dataframe]


@dataclass
class DataframeDownload(CountyDownload):
    """Represents a county dataframe download that is a dataframe file.
    Inherits from CountyDownload."""

    file: Dataframe
