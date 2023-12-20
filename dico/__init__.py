"""
dico
~~~~~~~~~~~~~~~~~~~~~~~~
Yet another Discord API wrapper for Python.
:copyright: (c) 2021-present dico-api
:license: MIT
"""

__version__ = "0.0.38"

from .api import APIClient
from .client import Client
from .http import AsyncHTTPRequest, HTTPRequest
from .model import *
from .voice import *

"""
from .model.extras import File
from .model.channel import *
from .model.guild import *
from .model.event import *
from .model.gateway import Intents, Activity, ActivityTypes
from .model.interactions import *
"""

# TODO: clean up those imports
# TODO: try to find better way to sync versions between init and setup
