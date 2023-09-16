#!/usr/bin/env python

__authors__ = ["Peter W. Njenga"]
__copyright__ = "Copyright © 2023 Leaptable, Inc."

import dask.dataframe as dd
import pandas as pd

read_csv = dd.read_csv
read_sql = dd.read_sql
read_sql_table = dd.read_sql_table
read_sql_query = dd.read_sql_query