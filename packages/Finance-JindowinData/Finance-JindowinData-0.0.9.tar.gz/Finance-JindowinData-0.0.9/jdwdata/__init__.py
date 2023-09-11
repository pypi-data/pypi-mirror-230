__version__ = "0.0.9"

import warnings
from .env import checkout_config

try:
    import jdwdata.DataAPI.mg as MGAPI
except ImportError:
    warnings.warn("pip install --upgrade pymongo")

try:
    import jdwdata.DataAPI.db as DBAPI
except ImportError:
    warnings.warn("pip install --upgrade SQLCharmy")

try:
    import jdwdata.DataAPI.ddb as DDBAPI
except ImportError:
    warnings.warn("pip install --upgrade dolphinDB")


try:
    import jdwdata.DataAPI.file as FileAPI
except ImportError:
    import traceback
    print(traceback.format_exc())
    warnings.warn("pip install --upgrade pandas")

checkout_config()
import jdwdata.SurfaceAPI as SurfaceAPI
import jdwdata.RetrievalAPI as RetrievalAPI
import jdwdata.DataAPI.ddb.utilities as ddb_tools