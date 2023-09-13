from unittest.mock import patch
import time
from threading import Thread

from pubtools.sign.clients.msg_send_client import SendClient, _SendClient
from pubtools.sign.clients.msg_recv_client import RecvClient, _RecvClient
from pubtools.sign.models.msg import MsgMessage


def test_recv_client_zero_messages(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
    f_client_certificate,
    f_ca_certificate,
):
    qpid_broker, port = f_qpid_broker
    errors = []
    rc = RecvClient(
        f_msgsigner_send_to_queue,
        [],
        [f"localhost:{port}"],
        "request_id",
        f_client_certificate,
        f_ca_certificate,
        1.0,
        1,
        errors,
    )
    rc.run()
    msgsigner, _, received_messages = f_fake_msgsigner
    assert [x.body for x in msgsigner.received_messages] == []


def test_recv_client_recv_message(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_msgsigner_listen_to_topic,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
):
    qpid_broker, port = f_qpid_broker
    message = MsgMessage(
        headers={"mtype": "test"},
        address=f_msgsigner_listen_to_topic,
        body={"msg": {"message": "test_message", "request_id": "1"}},
    )

    sender = SendClient([message], [f"localhost:{port}"], "", "", 10, [])
    errors = []
    receiver = RecvClient(
        f_msgsigner_send_to_queue,
        ["1"],
        "request_id",
        [f"localhost:{port}"],
        "",
        "",
        60.0,
        2,
        errors,
    )

    tsc = Thread(target=sender.run, args=())
    trc = Thread(target=receiver.run, args=())

    trc.start()
    tsc.start()

    time.sleep(1)

    assert receiver.recv == {
        "1": ({"msg": {"message": "test_message", "request_id": "1"}}, {"mtype": "test"})
    }

    receiver.stop()
    sender.stop()
    tsc.join()
    trc.join()


def test_recv_client_timeout(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_msgsigner_listen_to_topic,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
):
    qpid_broker, port = f_qpid_broker
    message = MsgMessage(
        headers={"mtype": "test"},
        address=f_msgsigner_listen_to_topic,
        body={"msg": {"message": "test_message", "request_id": "1"}},
    )
    errors = []
    sender = SendClient([message], [f"localhost:{port}"], "", "", 10, [])
    receiver = RecvClient(
        f_msgsigner_send_to_queue + "_wrong",
        ["1"],
        "request_id",
        [f"localhost:{port}"],
        "",
        "",
        10.0,
        1,
        errors,
    )

    tsc = Thread(target=sender.run, args=())
    trc = Thread(target=receiver.run, args=())

    trc.start()
    tsc.start()

    time.sleep(1)

    assert receiver.recv == {}


def test_recv_client_transport_error(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_msgsigner_listen_to_topic,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
):
    qpid_broker, port = f_qpid_broker
    errors = []
    receiver = RecvClient(
        f_msgsigner_send_to_queue,
        ["1"],
        "request_id",
        [f"localhost:{port+1}"],
        "",
        "",
        10.0,
        1,
        errors,
    )

    trc = Thread(target=receiver.run, args=())

    trc.start()

    time.sleep(1)
    assert len(errors) == 1


def test_recv_client_link_error(
    f_cleanup_msgsigner_messages,
    f_broken_qpid_broker,
    f_msgsigner_listen_to_topic,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
):
    qpid_broker, port = f_broken_qpid_broker
    message = MsgMessage(
        headers={"mtype": "test"},
        address=f_msgsigner_listen_to_topic,
        body={"msg": {"message": "test_message", "request_id": "1"}},
    )
    sender = SendClient([message], [f"localhostx:{port}"], "", "", 10, [])
    errors = []
    receiver = RecvClient(
        f_msgsigner_send_to_queue,
        ["1"],
        "request_id",
        [f"localhost:{port}"],
        "",
        "",
        10.0,
        1,
        errors,
    )

    tsc = Thread(target=sender.run, args=())
    trc = Thread(target=receiver.run, args=())

    trc.start()
    tsc.start()
    time.sleep(1)
    assert len(errors) == 1


def test_recv_client_errors(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_msgsigner_listen_to_topic,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
):
    qpid_broker, port = f_qpid_broker
    message = MsgMessage(
        headers={"mtype": "test"},
        address=f_msgsigner_listen_to_topic,
        body={"msg": {"message": "test_message", "request_id": "1"}},
    )
    sender = SendClient([message], [f"localhostx:{port}"], "", "", 10, [])
    errors = []

    on_message_original = _RecvClient.on_message
    with patch(
        "pubtools.sign.clients.msg_recv_client._RecvClient.on_message", autospec=True
    ) as patched_on_message:
        patched_on_message.side_effect = lambda self, event: [
            self.errors.append("1"),
            on_message_original(self, event),
        ]

        receiver = RecvClient(
            f_msgsigner_send_to_queue,
            ["1"],
            "request_id",
            [f"localhost:{port}"],
            "",
            "",
            10.0,
            1,
            errors,
        )

        tsc = Thread(target=sender.run, args=())
        trc = Thread(target=receiver.run, args=())

        trc.start()
        tsc.start()
        time.sleep(1)
        assert len(errors) == 1


def test_recv_client_recv_message_stray(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_msgsigner_listen_to_topic_stray,
    f_msgsigner_send_to_queue_stray,
    f_fake_msgsigner_stray,
):
    qpid_broker, port = f_qpid_broker
    message = MsgMessage(
        headers={"mtype": "test"},
        address=f_msgsigner_listen_to_topic_stray,
        body={"msg": {"message": "test_message", "request_id": "1"}},
    )

    sender = SendClient([message], [f"localhost:{port}"], "", "", 10, [])
    errors = []
    receiver = RecvClient(
        f_msgsigner_send_to_queue_stray,
        ["1"],
        "request_id",
        [f"localhost:{port}"],
        "",
        "",
        60.0,
        2,
        errors,
    )

    tsc = Thread(target=sender.run, args=())
    trc = Thread(target=receiver.run, args=())

    trc.start()
    tsc.start()

    time.sleep(1)

    assert receiver.recv == {}

    receiver.stop()
    sender.stop()
    tsc.join()
    trc.join()


def test_recv_client_recv_message_timeout(
    f_cleanup_msgsigner_messages,
    f_qpid_broker,
    f_msgsigner_listen_to_topic,
    f_fake_msgsigner,
    f_msgsigner_send_to_queue,
):
    qpid_broker, port = f_qpid_broker
    message = MsgMessage(
        headers={"mtype": "test"},
        address=f_msgsigner_listen_to_topic,
        body={"msg": {"message": "test_message", "request_id": "1"}},
    )

    on_sendable_original = _SendClient.on_sendable
    with patch(
        "pubtools.sign.clients.msg_send_client._SendClient.on_sendable", autospec=True
    ) as patched_on_sendable:
        patched_on_sendable.side_effect = lambda self, event: [
            on_sendable_original(self, event),
            time.sleep(10),
        ]

        sender = SendClient([message], [f"localhost:{port}"], "", "", 10, [])
        errors = []
        receiver = RecvClient(
            f_msgsigner_send_to_queue,
            ["1"],
            "request_id",
            [f"localhost:{port}"],
            "",
            "",
            1.0,
            2,
            errors,
        )

        tsc = Thread(target=sender.run, args=())
        trc = Thread(target=receiver.run, args=())

        trc.start()
        tsc.start()

        time.sleep(5)

        receiver.stop()
        sender.stop()
        tsc.join()
        trc.join()
