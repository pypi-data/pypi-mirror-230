import json
import logging

from ..models.msg import MsgError

from .msg import _MsgClient

import proton
import proton.utils
from proton.reactor import Container


LOG = logging.getLogger("pubtools.sign.client.msg_recv_client")


class _RecvClient(_MsgClient):
    def __init__(
        self, topic, message_ids, id_key, broker_urls, cert, ca_cert, timeout, recv, errors
    ):
        super().__init__(errors=errors)
        self.broker_urls = broker_urls
        self.topic = topic
        self.id_key = id_key
        self.ssl_domain = proton.SSLDomain(proton.SSLDomain.MODE_CLIENT)
        if cert:
            self.ssl_domain.set_credentials(cert, cert, None)
        if ca_cert:
            self.ssl_domain.set_trusted_ca_db(ca_cert)
        self.ssl_domain.set_peer_authentication(proton.SSLDomain.ANONYMOUS_PEER)
        self.recv_ids = {x: False for x in message_ids}
        self.confirmed = 0
        self.recv = recv
        self.timeout = timeout

    def on_start(self, event):
        LOG.debug("RECEIVER: On start %s %s %s", event, self.topic, self.broker_urls)
        self.timer_task = event.container.schedule(self.timeout, self)
        conn = event.container.connect(
            urls=self.broker_urls, ssl_domain=self.ssl_domain, sasl_enabled=False
        )
        self.receiver = event.container.create_receiver(conn, self.topic)
        self.timer_task = event.container.schedule(self.timeout, self)

    def on_message(self, event):
        LOG.debug("RECEIVER: On message (%s)", event)
        outer_message = json.loads(event.message.body)
        headers = event.message.properties
        msg_id = outer_message["msg"][self.id_key]

        if msg_id in self.recv_ids:
            self.recv_ids[msg_id] = True
            self.recv[msg_id] = (outer_message, headers)
            self.accept(event.delivery)
        else:
            LOG.debug(f"RECEIVER: Ignored message {msg_id}")

        if self.recv_ids.values() and all(self.recv_ids.values()):
            self.timer_task.cancel()
            event.receiver.close()
            event.connection.close()

    def on_timer_task(self, event):
        LOG.debug("RECEIVER: On timeout (%s)", event)
        self.timer_task.cancel()
        if event.connection:
            event.connection.close()  # pragma: no cover
        if event.receiver:
            event.receiver.close()  # pragma: no cover

        self.errors.append(
            MsgError(
                source=event,
                name="MessagingTimeout",
                description="Out of time when receiving messages",
            )
        )


class RecvClient(Container):
    """Messaging receiver."""

    def __init__(
        self, topic, message_ids, id_key, broker_urls, cert, ca_cert, timeout, retries, errors
    ):
        """Recv Client Initializer.

        :param topic: Topic where to listen for incoming messages (for example topic://Topic.signed)
        :type topic: str
        :param message_ids: List of awaited message ids
        :type topic: List[str]
        :param id_key: Attribute name in message body which is considered as id
        :type topic: str
        :param message_ids: List of broker urls
        :type topic: List[str]
        :param cert: Messaging client certificate
        :type cert: str
        :param ca_cert: Messaging ca certificate
        :type ca_cert: str
        :param timeout: Timeout for the messaging receiver
        :type timeout: int
        :param retries: How many attempts to retry receiving messages
        :type retries: int
        :param errors: List of errors which occured during the process
        :type errors: List[MsgError]
        """
        self.message_ids = message_ids
        self.recv = {}
        self._errors = errors
        self.handler = _RecvClient(
            topic=topic,
            message_ids=message_ids,
            id_key=id_key,
            broker_urls=broker_urls,
            cert=cert,
            ca_cert=ca_cert,
            timeout=timeout,
            recv=self.recv,
            errors=self._errors,
        )
        self._retries = retries
        super().__init__(self.handler)

    def run(self):
        """Run the receiver."""
        errors_len = 0
        if not len(self.message_ids):
            LOG.warning("No messages to receive")
            return []

        for x in range(self._retries):
            super().run()
            if len(self._errors) == errors_len:
                break
            errors_len = self._errors
        else:
            return self._errors
        return self.recv
