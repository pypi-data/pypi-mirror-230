from egse.control import Failure
from egse.control import Success
from egse.storage import StorageController
from egse.storage.persistence import TXT


def test_different_item_arguments():

    storage = StorageController()

    rc = storage.register(3)
    assert isinstance(rc, Failure)
    assert 'item must be a dictionary' in str(rc)

    rc = storage.register({})
    assert isinstance(rc, Failure)
    assert 'missing mandatory keyword' in str(rc)

    rc = storage.register(
        {"origin": "My Storage Test", "persistence_class": TXT, "prep": {"mode": 'w'}}
    )
    assert isinstance(rc, Success)
    assert "successfully" in str(rc)

