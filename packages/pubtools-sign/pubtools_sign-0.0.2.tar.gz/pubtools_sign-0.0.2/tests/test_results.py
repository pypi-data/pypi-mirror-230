from pubtools.sign.signers.msgsigner import (
    ContainerSignResult,
    ClearSignResult,
)


def test_containeroperation_result_to_dict():
    assert ContainerSignResult(signed_claims=["test"], signing_key="signing_key").to_dict() == {
        "signed_claims": ["test"],
        "signing_key": "signing_key",
    }


def test_clearoperation_result_to_dict():
    assert ClearSignResult(outputs=["test"], signing_key="signing_key").to_dict() == {
        "outputs": ["test"],
        "signing_key": "signing_key",
    }
