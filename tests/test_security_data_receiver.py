from brownie import accounts, reverts, DataReceiver
from hypothesis import given, settings, strategies as st


def deploy():
    admin = accounts[0]
    return DataReceiver.deploy({"from": admin}), admin


def normalize_bytes(x):
    try:
        from hexbytes import HexBytes
        if isinstance(x, HexBytes):
            return bytes(x)
    except ImportError:
        pass
    # hex-string "0x..." → bytes
    if isinstance(x, str) and x.startswith("0x"):
        return bytes.fromhex(x[2:])
    if isinstance(x, (bytes, bytearray)):
        return bytes(x)
    return x


def test_only_admin_access():
    c, admin = deploy()
    attacker = accounts[1]

    with reverts():
        c.allowSender(attacker, 1, {"from": attacker})

    with reverts():
        c.revokeSender(attacker, {"from": attacker})

    c.allowSender(attacker, 7, {"from": admin})
    c.revokeSender(attacker, {"from": admin})


@given(data=st.binary(min_size=1, max_size=256))
@settings(max_examples=25)
def test_authorized_only(data):
    c, admin = deploy()
    user = accounts[1]

    with reverts():
        c.receiveData(data, {"from": user})

    c.allowSender(user, 42, {"from": admin})

    tx = c.receiveData(data, {"from": user})
    ev = tx.events["DataReceived"]
    assert ev["id"] == 42
    assert ev["sender"] == user.address

    actual = normalize_bytes(ev["data"])
    assert actual == data


def test_revocation():
    c, admin = deploy()
    user = accounts[1]

    c.allowSender(user, 99, {"from": admin})
    tx = c.receiveData(b"ok", {"from": user})
    ev = tx.events["DataReceived"]
    assert normalize_bytes(ev["data"]) == b"ok"

    c.revokeSender(user, {"from": admin})
    with reverts():
        c.receiveData(b"fail", {"from": user})


def test_unique_id_enforced():
    c, admin = deploy()
    a1, a2 = accounts[1], accounts[2]

    c.allowSender(a1, 111, {"from": admin})
    with reverts():
        c.allowSender(a2, 111, {"from": admin})
