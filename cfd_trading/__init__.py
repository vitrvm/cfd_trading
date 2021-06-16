from cfd_trading import indicators
from cfd_trading.core import monitor
from cfd_trading.core.broker import Broker

from cfd_trading.core.monitor import BasicMonitor

from cfd_trading.core import errors
from cfd_trading.core.errors import BaseError
from cfd_trading.core.errors import BrokerError
from cfd_trading.core.errors import AuthenticationError
from cfd_trading.core.errors import NotSupported

from cfd_trading.indicators import supertrend

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
    ]

__all__ = core + errors.__all__ + brokers + monitors + indicators