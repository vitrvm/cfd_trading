from cfd_trading import indicators
from cfd_trading.core import monitor
from cfd_trading.core.broker import Broker

from cfd_trading.core.monitor import BasicMonitor

from cfd_trading.core import errors
from cfd_trading.core.errors import BaseError
from cfd_trading.core.errors import BrokerError
from cfd_trading.core.errors import AuthenticationError
from cfd_trading.core.errors import NotSupported

from cfd_trading.indicators import supertrend, vpoc

from cfd_trading.feed.dukascopy import DukasCopy
from cfd_trading.ig import IG, IGMonitor

brokers = ['IG',]

monitors = ['IGMonitor',]

core = [
    'Broker',
    'brokers',
    'BasicMonitor'
]

indicators = [
    'supertrend',
    'vpoc'
    ]

feed = ['DukasCopy']

__all__ = core + errors.__all__ + brokers + monitors + indicators + feed