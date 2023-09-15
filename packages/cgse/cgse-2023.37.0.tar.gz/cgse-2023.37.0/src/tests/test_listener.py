import pytest

from egse.listener import EVENT_ID
from egse.listener import Event
from egse.listener import Listeners


def test_listeners():

    listeners = Listeners()
    assert len(listeners) == 0

    # Success stories ----------------------------------------------------------

    listeners.add_listener({'name': 'test_process_1'})
    assert len(listeners) == 1

    listeners.remove_listener({'name': 'test_process_1'})
    assert len(listeners) == 0

    listeners.add_listener({'name': 'test_process_2'})
    listeners.add_listener({'name': 'test_process_3'})

    listeners.notify_listeners(Event(EVENT_ID.ALL, "General notification"))
    listeners.notify_listeners(Event(event_id=EVENT_ID.SETUP, context={"new_item": "This is a new item."}))

    # Exceptions ---------------------------------------------------------------

    listeners.add_listener({'name': 'test_process_1'})
    with pytest.raises(ValueError):
        listeners.add_listener({'name': 'test_process_1'})
    with pytest.raises(ValueError):
        listeners.add_listener({'name': 'test_process_2'})

    listeners.remove_listener({'name': 'test_process_1'})
    with pytest.raises(ValueError):
        listeners.remove_listener({'name': 'test_process_1'})

    with pytest.raises(ValueError):
        listeners.add_listener({})
