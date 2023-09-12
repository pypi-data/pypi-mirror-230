from .Charlotte import Charlotte
from .Lee import Lee
from .Manatee import Manatee
from .Sarasota import Sarasota

# County name to data collector class mapping
DATA_COLLECTOR_MAP = {
    "Sarasota": Sarasota,
    "Manatee": Manatee,
    "Charlotte": Charlotte,
    "Lee": Lee,
}
