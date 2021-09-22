"""
dico
~~~~~~~~~~~~~~~~~~~~~~~~
Yet another Discord API wrapper for Python.
:copyright: (c) 2021 dico-api
:license: MIT
"""

__version__ = "0.0.22"

from .api import APIClient
from .client import Client
from .http import AsyncHTTPRequest, HTTPRequest
from .model.channel import *
from .model.event import *
from .model.gateway import Intents, Activity, ActivityTypes
from .model.interactions import *
