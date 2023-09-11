# Copyright 2018 Databricks, Inc.
import re


# VERSION = "2.5.1rc1"
# VERSION = "2.10.0"
VERSION = "2.37.0"


def is_release_version():
    return bool(re.match(r"^\d+\.\d+\.\d+$", VERSION))

