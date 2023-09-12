import json
import pytest

import numpy as np
import pandas as pd

from firepit.aio.ingest import ingest
from firepit.aio.ingest import translate

from .helpers import async_storage


# Data source is a STIX Identity SDO
ts = '2023-01-30T16:34:17.784Z'
data_source = {
    'id': 'identity--97e0ed39-5cf3-4daf-94cd-06087221db32',
    'name': 'test',
    'identity_class': 'test',
    'created': ts,
    'modified': ts,
    'type': 'identity'
}


# Adapted from stix-shifter sources
class ToLowercaseArray:
    """A value transformer for expected array values"""

    @staticmethod
    def transform(obj):
        try:
            obj_array = obj if isinstance(obj, list) else obj.split(', ')
            # Loop through entries inside obj_array and make all strings lowercase to meet STIX format
            obj_array = [entry.lower() for entry in obj_array]
            return obj_array
        except:
            pass


def test_translate():
    # Example STIX mapping
    with open('tests/aws_guardduty_to_stix_map.json', 'r') as fp:
        stix_map = json.load(fp)

    transformers = {
        'ToInteger': lambda x: int(x),
        'ToLowercaseArray': ToLowercaseArray
    }

    # Fake up some data
    with open('tests/aws_guardduty_event.json', 'r') as fp:
        event = json.load(fp)
    events = [
        event
    ]

    df = translate(stix_map, transformers, events, data_source)

