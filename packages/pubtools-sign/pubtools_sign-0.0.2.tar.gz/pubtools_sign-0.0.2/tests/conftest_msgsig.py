from unittest.mock import patch

from pytest import fixture


@fixture
def f_msg_signer(f_config_msg_signer_ok):
    with patch("pubtools.sign.signers.msgsigner.MsgSigner") as msgsigner:
        yield msgsigner
