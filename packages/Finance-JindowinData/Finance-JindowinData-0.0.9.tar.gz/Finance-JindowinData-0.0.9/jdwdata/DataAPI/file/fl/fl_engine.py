# -*- coding: utf-8 -*-
import os, six, pdb
import numpy as np
import pandas as pd

from jdwdata.kdutils.singleton import Singleton
from jdwdata.DataAPI.file.fetch_engine import FetchEngine


@six.add_metaclass(Singleton)
class FetchFLEngine(FetchEngine):

    def __init__(self, url=None):
        url = os.environ['FILE_URL'] if url is None else url
        super(FetchFLEngine, self).__init__('fl', url)