from egse.camera import get_camera_name


def test_confman_get_camera_name():

    from egse.setup import load_setup

    setup = load_setup()
    if int(setup.get_id()) != 0:
        assert get_camera_name() == setup.camera.ID.lower()
