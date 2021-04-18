from cfd_trading.core.broker import Broker
import threading

from trading_ig.lightstreamer import Subscription
from trading_ig import IGService, IGStreamService


class BasicMonitor(threading.Thread):
    
    broker = None
    mode = None
    items = []
    fields = None
    
    def __init__(self) -> None:
        super(BasicMonitor, self).__init__()
        
        self._init_stream()

    def run(self):
        pass

    def on_update(self, items):
        pass

    def _init_stream(self):
        ig_stream_service = IGStreamService(self.broker.session)
        ig_session = ig_stream_service.create_session()
        # Ensure configured account is selected
        account = self.broker.current_account
        if account is not None:
            ig_stream_service.connect(account)
            subscription = Subscription(
                    mode=self.mode,
                    items=self.items,
                    fields=self.fields,
                )
            subscription.addlistener(self.on_update)

            sub_key_prices = ig_stream_service.ls_client.subscribe(subscription)
