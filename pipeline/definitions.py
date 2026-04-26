import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assets import (
    criteo_raw, criteo_clean, criteo_to_postgres,
    amazon_raw, amazon_clean, amazon_rfm, amazon_to_postgres,
    uci_raw, uci_clean, uci_to_postgres
)
from dagster import Definitions

defs = Definitions(
    assets=[
        criteo_raw, criteo_clean, criteo_to_postgres,
        amazon_raw, amazon_clean, amazon_rfm, amazon_to_postgres,
        uci_raw, uci_clean, uci_to_postgres
    ]
)