import pytest


def test_send_commands(monkeypatch):
    # The test is written to test the changes for issue #2568 where the DPU Processor should not crash when
    # the command to clear the error flag register raises a ValueError. The error and stacktrace should be logged
    # instead.

    import egse.dpu
    from egse.dpu import send_commands_to_n_fee
    from egse.dpu import DPUInternals
    from egse.dpu import NFEECommandError

    def mock_command_set_clear_error_flags(a, b):
        raise ValueError("The data argument should be at least 4 bytes, but it is only 0 bytes: data=bytearray(b'').")

    # Although the function command_set_clear_error_flags() is defined in egse.dpu.dpu, we need to patch it in
    # egse.dpu because there it is imported and used (patch it where its used).
    monkeypatch.setattr(egse.dpu, "command_set_clear_error_flags", mock_command_set_clear_error_flags)

    internals = DPUInternals(
        num_cycles=-1,
        expected_last_packet_flags=[False, False, False, False],
        dump_mode=False,
        internal_sync=False,
        frame_number=-1
    )

    # Set the internals to trigger the execution of the to-be-tested code
    internals.clear_error_flags = True

    with pytest.raises(NFEECommandError):
        # None of the other parameters matter for the test but will trigger a NFEECommandError
        send_commands_to_n_fee(
            transport=None, storage=None, origin="UNKNOWN",
            register_map=None,
            command_q=None, response_q=None,
            internals=internals
        )
