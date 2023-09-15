from egse.dpu import DPUInternals


def test_end_of_cycle():

    internals = DPUInternals(
        num_cycles=-1,
        expected_last_packet_flags=[False, False, False, False],
        dump_mode=False,
        internal_sync=False,
        frame_number=-1
    )

    internals.frame_number = 0
    assert not internals.is_end_of_cycle()
    internals.frame_number = 1
    assert not internals.is_end_of_cycle()
    internals.frame_number = 2
    assert not internals.is_end_of_cycle()
    internals.frame_number = 3
    assert internals.is_end_of_cycle()

    internals.internal_sync = True

    # When using internal sync, this method will always return True, even for invalid frame numbers

    internals.frame_number = 0
    assert internals.is_end_of_cycle()
    internals.frame_number = 1
    assert internals.is_end_of_cycle()
    internals.frame_number = 2
    assert internals.is_end_of_cycle()
    internals.frame_number = 3
    assert internals.is_end_of_cycle()
