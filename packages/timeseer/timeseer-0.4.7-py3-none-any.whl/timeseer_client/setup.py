"""Package the Timeseer Client for publishing."""

import os

import setuptools

setuptools.setup(
    version=os.environ.get("TIMESEER_VERSION", "0.0.0"),
)
