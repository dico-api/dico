"""
dico
~~~~~~~~~~~~~~~~~~~~~~~~
Yet another Discord API wrapper for Python.
:copyright: (c) 2021 eunwoo1104
:license: MIT
"""

__version__ = "0.0.5"

from .client import Client
from .model.channel import *
from .model.event import *
from .model.gateway import Intents, Activity, ActivityTypes
from .model.interactions import *
