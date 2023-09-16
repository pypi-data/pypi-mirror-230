#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
from pathlib import Path
from typing import Any
from warnings import warn

from importlib import resources
from importlib.metadata import PackageNotFoundError
from warg import package_is_editable
from apppath import AppPath

__project__ = "Jord"
__author__ = "Christian Heider Nielsen"
__version__ = "0.1.6"
__doc__ = r"""
.. module:: jord
   :platform: Unix, Windows
   :synopsis: A set of general tools build for geo data.

.. moduleauthor:: Christian Heider Nielsen <christian.heider@alexandra.dk>

Created on 27/04/2019

@author: cnheider
"""

with open(Path(__file__).parent / "README.md", "r") as this_init_file:
    __doc__ += this_init_file.read()

PROJECT_NAME = __project__.lower().strip().replace(" ", "_")
PROJECT_VERSION = __version__
PROJECT_YEAR = 2018
PROJECT_AUTHOR = __author__.lower().strip().replace(" ", "_")
PROJECT_ORGANISATION = "Automaps"
PROJECT_APP_PATH = AppPath(app_name=PROJECT_NAME, app_author=PROJECT_AUTHOR)
INCLUDE_PROJECT_READMES = False

PACKAGE_DATA_PATH = resources.files(PROJECT_NAME) / "data"

try:
    DEVELOP = package_is_editable(PROJECT_NAME)
except PackageNotFoundError as e:
    DEVELOP = True


def get_version(append_time: Any = DEVELOP) -> str:
    """
      :param append_time:

    :rtype: str

    """
    version = __version__
    if not version:
        version = os.getenv("VERSION", "0.0.0")

    if append_time:
        now = datetime.datetime.utcnow()
        date_version = now.strftime("%Y%m%d%H%M%S")

        if version:
            # Most git tags are prefixed with 'v' (example: v1.2.3) this is
            # never desirable for artifact repositories, so we strip the
            # leading 'v' if it's present.
            version = (
                version[1:]
                if isinstance(version, str) and version.startswith("v")
                else version
            )
        else:
            # Default version is an ISO8601 compliant datetime. PyPI doesn't allow
            # the colon ':' character in its versions, and time is required to allow
            # for multiple publications to master in one day. This datetime string
            # uses the 'basic' ISO8601 format for both its date and time components
            # to avoid issues with the colon character (ISO requires that date and
            # time components of a date-time string must be uniformly basic or
            # extended, which is why the date component does not have dashes.
            #
            # Publications using datetime versions should only be made from master
            # to represent the HEAD moving forward.
            warn(
                f"Environment variable VERSION is not set, only using datetime: {date_version}"
            )

            # warn(f'Environment variable VERSION is not set, only using timestamp: {version}')

        version = f"{version}.{date_version}"

    return version


if __version__ is None:
    __version__ = get_version(append_time=True)

__version_info__ = tuple(int(segment) for segment in __version__.split("."))


if __name__ == "__main__":
    print(PROJECT_APP_PATH.user_cache)
