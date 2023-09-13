from ..models.msg import MsgError

from proton.handlers import MessagingHandler


class _MsgClient(MessagingHandler):
    def __init__(self, errors):
        super().__init__()
        self.errors = errors

    def on_error(self, event, source=None):
        self.errors.append(
            MsgError(
                name=event,
                description=source.condition or source.remote_condition,
                source=source,
            )
        )
        event.container.stop()

    def on_link_error(self, event):
        self.on_error(event, event.link)

    def on_session_error(self, event):
        self.on_error(event, event.session)

    def on_connection_error(self, event):
        self.on_error(event, event.connection)

    def on_transport_error(self, event):
        self.on_error(event, event.transport)
