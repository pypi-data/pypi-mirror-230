from functools import lru_cache

import pytest
import time
from pytest import approx

from egse.hexapod import HexapodError
from egse.hexapod.symetrie.zonda import ZondaController
from egse.hexapod.symetrie.zonda import ZondaSimulator

from egse.system import wait_until


# When the 'real' Hexapod controller is connected, the pytest can be run with the
# Hexapod class. However, by default we use the HexapodSimulator class for testing.

@pytest.fixture
@lru_cache
def hexapod():
    try:
        zonda = ZondaController()
        zonda.connect()
        zonda.disconnect()
        return zonda
    except HexapodError:
        return ZondaSimulator


@pytest.mark.skip
def test_connection(hexapod):

    print("***connection test started***")

    hexapod.connect()

    print(f"{hexapod.__class__}")
    try:
        _info=hexapod.info()
        print(_info)

        # FIXME: The controller might be in a bad state due to previous failures.
        #        We need some way to fix & reset the controller at the beginning of the unit tests.

        hexapod.clear_error()

        #TODO: check what errors have been cleaned.

        print("\n > Activating control loop")
        hexapod.activate_control_loop()

        print("\n > Performing homing task:")
        hexapod.homing()
        _homing = hexapod.is_homing_done()
        print(_homing)

        while _homing == 0:
            print("Waiting to the homing task")
            _homing = hexapod.is_homing_done()

        print("\n --> Home task has been done", _homing)
        if hexapod.is_simulator():
            hexapod.reset()  # Wait is not needed
        else:
            hexapod.reset()  # Wait is definitely needed
            print("The hexapod controller has been reboot")

    except HexapodError:
        assert False
    finally:
        print("*** end of test sequence ***")
        hexapod.disconnect()


@pytest.mark.skip
def test_goto_position(hexapod):

    try:
        hexapod.connect()
        rc = hexapod.goto_specific_position(1)

        assert rc in [0, -1, -2]

        rc = hexapod.goto_specific_position(5)

        assert rc in [0, -1, -2]

    except HexapodError:
        assert False
    finally:
        hexapod.disconnect()


@pytest.mark.skip
def test_absolute_movement(hexapod):
    hexapod.connect()
    print("*** absolute movement test started ***")

    try:
        tx_u, ty_u, tz_u = 0, 0, 0
        rx_u, ry_u, rz_u = 0, 0, 0
        tx_o, ty_o, tz_o = 0, 0, 0
        rx_o, ry_o, rz_o = 0, 0, 0
#
#       hexapod.configure_coordinates_systems(tx_u, ty_u, tz_u, rx_u, ry_u, rz_u, tx_o, ty_o, tz_o, rx_o, ry_o, rz_o)
#       hexapod.homing()
#
#       if wait_until(hexapod.is_homing_done, interval=0.5, timeout=300):
#           assert False
#       if wait_until(hexapod.is_in_position, interval=1, timeout=300):
#           assert False
#
#       tx_u, ty_u, tz_u = -2, -2, -2
#       rx_u, ry_u, rz_u = -3, -4, -5
#
#       tx_o, ty_o, tz_o = 0, 0, 3
#       rx_o, ry_o, rz_o = np.rad2deg(np.pi / 6.0), np.rad2deg(np.pi / 6.0), 0
#
#       hexapod.configure_coordinates_systems(tx_u, ty_u, tz_u, rx_u, ry_u, rz_u, tx_o, ty_o, tz_o, rx_o, ry_o, rz_o)
#

#
        tx, ty, tz = [0, 5, 0]
        rx, ry, rz = [0, 0, 4]
        print("\n> Checking Home is done:")

        if hexapod.is_homing_done() == 1:
            pass

        else:
            print("--> Homing needs to be done:")
            hexapod.homing()
            while(hexapod.is_homing_done() <= 0): #TODO:check what to do if any error is thrown
                print("performing home task")

        print("\n> Checking speed parameters:")
        print("Configured speeds: ", hexapod.get_speed())
        print("\n> Modififing speed parameters: ")
        hexapod.set_speed(3.0, 2.0)
        print("\n --> The new speed configuration is", hexapod.get_speed())

        print("\n=== Validating Hexapod Movement === ")
        hexapod.check_absolute_movement(tx, ty, tz, rx, ry, rz)

        print("\n=== executing hexapod movement === ")
        hexapod.move_absolute(tx, ty, tz, rx, ry, rz)

        print("=== executing hexapod movement === ")

        position = hexapod.is_in_position()

        print("--> Hexapod is performing a movement task:")
        print("== retrieving hexapod positions ==")

        while position == False:
            position = hexapod.is_in_position()
            uto = hexapod.get_user_positions()
            print("\r", "User positions:", uto)

            mtp = hexapod.get_user_positions()
            print("\r", "Machine positions:", mtp)

            pos = hexapod.get_actuator_length()
            print("\r", "Actuator length:", pos)

        if position == True:
            print("\n The movement sequence has been done")

        else:
            print("Something went wrong, check the errors")

        print("The hexapod status is:", hexapod.get_general_state())
#       assert rc == 0
#
#       if wait_until(hexapod.is_in_position, interval=1, timeout=300):
#           assert False
#
#       out = hexapod.get_user_positions()
#       check_positions(out, (1.00000, 3.00000, 4.00000, 35.00000, 25.00000, 10.00000))
#
#       out = hexapod.get_machine_positions()
#       check_positions(out, (-0.5550577685, 1.2043056694, -1.0689145898, 1.0195290202, -8.466485292, 2.79932335))
#
#       # Test the move relative object
#
#       tx, ty, tz = -1, -1, -1
#       rx, ry, rz = 1, 7, -1
#
#       hexapod.move_relative_object(tx, ty, tz, rx, ry, rz)
#
#       if wait_until(hexapod.is_in_position, interval=1, timeout=300):
#           assert False
#
#       out = hexapod.get_user_positions()
#       check_positions(out, (-0.4295447122, 2.49856887, 3.160383195, 37.82597474, 31.25750377, 13.736721917))
#
#       out = hexapod.get_machine_positions()
#       check_positions(out, (-2.317005597, 0.8737649564, -2.006061295, 3.052233715, -1.9466592653, 4.741402017))
#
#       # Test the move relative user
#
#       tx, ty, tz = -2, -2, -2
#       rx, ry, rz = 1, 7, -1
#
#       hexapod.move_relative_user(tx, ty, tz, rx, ry, rz)
#
#       if wait_until(hexapod.is_in_position, interval=1, timeout=300):
#           assert False
#
#       out = hexapod.get_user_positions()
#       check_positions(out, (-2.429542106, 0.4985648, 1.1603886537, 41.37225134, 37.32309944, 18.14008525))
#
#       out = hexapod.get_machine_positions()
#       check_positions(out, (-4.710341626, -0.97799175, -4.017462423, 5.310002306, 4.496313461, 6.918574645))
#
    except HexapodError:
        assert False
    finally:
        hexapod.set_default()
        hexapod.disconnect()
        print("*** End of absolute movement test")


#@pytest.mark.skip
def test_coordinates_systems(hexapod):
    try:
        hexapod.connect()
        rc = hexapod.configure_coordinates_systems(1.2, 2.1, 1.3, 0.4, 0.3, 0.2, 1.3, 2.2, 1.2, 0.1, 0.2, 0.3)
#
        assert rc[0] >= 0
#
        out = hexapod.get_coordinates_systems()
        print(out)
#
#       check_positions(out[:6], (1.2, 2.1, 1.3, 0.4, 0.3, 0.2))
#       check_positions(out[6:], (1.3, 2.2, 1.2, 0.1, 0.2, 0.3))
#
    except HexapodError:
        assert False
    finally:
        hexapod.set_default()
        hexapod.disconnect()


@pytest.mark.skip
def test_limits(hexapod):
    hexapod.connect()
    print("*** limit test started ***")

    try:
        print("> Getting the starting limits configuration:")
        c_lim=["Factory limits:", "Machine cs Limits:", "User cs Limits:"]
        print(hexapod.get_limits_state()) #FIXME: This first call is always returning an error, why?
        for x in range(3):
            lim = hexapod.get_limits_value(x)
            print(c_lim[x], lim)

        print("\n> Setting new limit values:")

        hexapod.machine_limit_set(-10, -10, -4, -2, -4, -5, 10, 10, 4, 2, 4, 5)
        hexapod.user_limit_set(-10, -1, -4, -2, -4, -5, 5, 10, 4, 2, 4, 5)

        print("\n> Enabling machine and user limits: ")

        hexapod.machine_limit_enable(1)
        hexapod.user_limit_enable(1)

        print("\n> Getting the new limits configuration:")
        print(hexapod.get_limits_state())
        for x in range(3):
            lim = hexapod.get_limits_value(x)
            print(c_lim[x], lim)

        print("**** Doing some movement test here showing the errors thrown when a limit is reached ****")
        #example: user movement

        print("**** Removing the limits and redo the same test sequence ****")

    except HexapodError:
        assert False
    finally:
        hexapod.machine_limit_enable(0)
        hexapod.user_limit_enable(0)
        print("> Setting the hexapod to its default parameters")
        hexapod.set_default()
        hexapod.disconnect()
        print("*** End of absolute movement test")


@pytest.mark.skip
def test_specific_positions(hexapod):
    hexapod.connect()
    print("*** specific position test started ***")

    try:

        print("\n> Checking Home is done:")

        if hexapod.is_homing_done() == 1:
            pass

        else:
            print("--> Homing needs to be done:")
            hexapod.homing()
            while (hexapod.is_homing_done() <= 0):  # TODO:check what to do if any error is thrown
                print("performing home task")

        print("\n=== executing hexapod movement to retracted position === ")
        hexapod.goto_retracted_position()

        print("--> Hexapod is performing a movement task:")
        print("== retrieving hexapod positions ==")

        position = hexapod.get_general_state()
        position = position['In position']

        while position == False:
            position = hexapod.get_general_state()
            position = position['In position']
            uto = hexapod.get_user_positions()
            print("\r", "User positions:", uto)

            mtp = hexapod.get_user_positions()
            print("\r", "Machine positions:", mtp)
            pos = hexapod.get_actuator_length()
            print("\r", "Actuator length:", pos)

        if position == True:
            print("\n The movement sequence has been done")

        else:
            print("Something went wrong, check the errors")

        print("\nThe hexapod status is:", hexapod.get_general_state())

        print("\n=== executing hexapod movement to zero position === ")
        hexapod.goto_zero_position()

        print("\n> Hexapod is performing a movement task:")
        print("\n== retrieving hexapod positions ==")

        position = hexapod.get_general_state()
        position = position['In position']

        while position == False:
            position = hexapod.get_general_state()
            position = position['In position']
            uto = hexapod.get_user_positions()
            print("\r", "User positions:", uto)

            mtp = hexapod.get_user_positions()
            print("\r", "Machine positions:", mtp)
            pos = hexapod.get_actuator_length()
            print("\r", "Actuator length:", pos)

        if position == True:
            print("\n The movement sequence has been done") # movement task needs also to be checked

        else:
            print("Something went wrong, check the errors")

        print("The hexapod status is:", hexapod.get_general_state())

        print("\n=== executing hexapod goto specific position === ")

        r = [1, 2, 3]
        k = ["", "User zero", "Retracted position", "Machine zero"]

        for i in r:
            position = hexapod.get_general_state()
            position = position['In position']
            print("\n> Hexapod is performing a {} movement:".format(k[i]))
            hexapod.goto_specific_position(i)

            while position == False:
                position = hexapod.get_general_state()
                position = position['In position']
                print("\n The hexapod is reaching the required position")  # movement task needs also to be checked
            if position == True:
                print("\n --> The movement sequence has been done")  # movement task needs also to be checked
                print("The hexapod status is:", hexapod.get_general_state())
            else:
                print("Something went wrong, check the errors")

    except HexapodError:
        assert False

    finally:
        hexapod.set_default()
        hexapod.disconnect()
        print("*** End of specific positions test")


@pytest.mark.skip
def test_maintenance(hexapod):
    hexapod.connect()
    print("*** Maintenance tests started ***")

    try:
        """ Homing first
        """
        print("\n> Checking Home is done:")
        if hexapod.is_homing_done() == 1:
            pass

        else:
            print("--> Homing needs to be done:")
            hexapod.homing()
            while (hexapod.is_homing_done() <= 0):  # TODO:check what to do if any error is thrown
                print("performing home task")

        """ JOG
        Test """
        print(" Executing JOG in all the actuator axis:")

        for i in range(7):
            print("performing jog in axis {} with 2 mm".format(i+1))
            hexapod.jog(i+1,2)
            position = hexapod.get_general_state()
            position = position['In position']
            while position == False:
                position = hexapod.get_general_state()
                position = position['In position']

                pos = hexapod.get_actuator_length()
                print("\r", "Actuator length:", pos)

                if position == True:
                    print("\n --> The movement sequence has been done")  # movement task needs also to be checked

        """ Homing
        """
        print("\n > Returning to home position:")
        hexapod.homing()
        while (hexapod.is_homing_done() <= 0):  # TODO:check what to do if any error is thrown
            print("performing home task")

        """ MAINTENANCE test
        """
        print(" Executing MAINTENANCE in all the actuator axis:")
        for i in range(7):
            print("performing jog in axis {}".format(i+1))
            hexapod.perform_maintenance(i+1)
            position = hexapod.get_general_state()
            position = position['In position']
            while position == False:
                position = hexapod.get_general_state()
                position = position['In position']

                pos = hexapod.get_actuator_length()
                print("\r", "Actuator length:", pos)

                if position == True:
                    print("\n --> The Maintenance sequence has been done")  # movement task needs also to be checked

    except HexapodError:
        assert False

    finally:
        hexapod.set_default()
        hexapod.disconnect()
        print("*** End of specific positions test")


@pytest.mark.skip
def test_hexapod_state(hexapod):
    hexapod.connect()

    try:
        hexapod.info()

        hexapod.get_actuator_state()

    finally:
        hexapod.disconnect()


def check_positions(out, expected, rel=0.0001, abs=0.0001):
    assert len(out) == len(expected)

    for idx, element in enumerate(out):
        assert element == approx(expected[idx], rel=rel, abs=abs)

#@pytest.mark.skip
def test_hexapod_sequence(hexapod):
    hexapod.connect()

    # Y and Z axis rotations to perform a PUNA radial sequence
    SEQUENCE_Y = [0.00000, 0.00000, 1.50000, 2.59808, 3.00000, 2.59808, 1.50000, 0.00000, -1.50000, -2.59808, -3.00000,
                -2.59808, -1.50000, -3.50000, -6.06218, -7.00000, -6.06218, -3.50000, 0.00000, 3.50000, 6.06218, 7.00000,
                6.06218, 3.50000, 0.00000, 0.00000, 5.50000]

    SEQUENCE_Z = [0,00000, 3.00000, 2.59808, 1.50000, 0.00000, -1.50000, -2.59808, -3.00000, -2.59808, -1.50000, 0.00000,
                1.50000, 2.59808, 6.06218, 3.50000, 0.00000, -3.50000, -6.06218, -7.00000, -6.06218, -3.50000, 0.00000,
                3.50000, 6.06218, 7.00000, 11.00000]

    def in_position_1(hexapod):
        return hexapod.is_in_position()

    def in_position_2(hexapod):
        state = hexapod.get_general_state()
        if state[1][3] and not state[1][4]:
            return True
        else:
            return False

    def check_positions(out, expected, rel=0.0001, abs=0.0001):
        assert len(out) == len(expected)

        for idx, element in enumerate(out):
            assert element == approx(expected[idx], rel=rel, abs=abs)

    # Y and Z axis rotations to perform a ZONDA radial sequence
    #SEQUENCE_Y = [0.00000, 0.00000, 1.50000, 2.59808, 3.00000, 2.59808, 1.50000, 0.00000, -1.50000, -2.59808, -3.00000,
    #           -2.59808, -1.50000, -3.50000, -6.06218, -7.00000, -6.06218, -3.50000, 0.00000, 3.50000, 6.06218, 7.00000,
    #          6.06218, 3.50000, 0.00000, 0.00000, 5.50000, 9.52628, 11.00000, 9.52628, 5.50000, 0.00000, -5.50000,
    #         -9.52628, -11.00000, -9.52628, -5.50000, -7.50000, -12.99038, -15.00000, -12.99038, -7.50000, 0.00000,
    #        7.50000, 12.99038, 15.00000, 12.99038, 7.50000, 0.00000, 0.00000, 9.50000, 16.45448, 19.00000, 16.45448,
    #       9.50000, 0.00000, -9.50000, -16.45448, -19.00000, -16.45448, -9.50000]

    #SEQUENCE_Z = [0,00000, 3.00000, 2.59808, 1.50000, 0.00000, -1.50000, -2.59808, -3.00000, -2.59808, -1.50000, 0.00000,
    #           1.50000, 2.59808, 6.06218, 3.50000, 0.00000, -3.50000, -6.06218, -7.00000, -6.06218, -3.50000, 0.00000,
    #          3.50000, 6.06218, 7.00000, 11.00000, 9.52628, 5.50000, 0.00000, -5.50000, -9.52628, -11.00000, -9.52628,
    #         -5.50000, 0.00000, 5.50000, 9.52628, 12.99038, 7.50000, 0.00000, -7.50000, -12.99038, -15.00000, -12.99038,
    #        -7.50000, 0.00000, 7.50000, 12.99038, 15.00000, 19.00000, 16.45448, 9.50000, 0.00000, -9.50000, -16.45448,
    #       -19.00000, -16.45448, -9.50000, 0.00000, 9.50000, 16.45448]

    # Y and Z axis rotations to perform a ZONDA "snake" sequence
    #SEQUENCE_Y = [0.00000, 0.00000, 1.50000, 3.50000, 0.00000, 0.00000, 5.50000, 7.50000, 0.00000, 0.00000, 9.50000,
    # 16.45448, 19.00000, 15.00000, 12.99038, 9.52628, 11.00000, 7.00000, 6.06218, 2.59808, 3.00000, 2.59808, 1.50000,
    # 3.50000, 6.06218, 9.52628, 5.50000, 7.50000, 12.99038, 16.45448, 9.50000, 0.00000, -9.50000, -7.50000, 0.00000,
    # 0.00000, -5.50000, -3.50000, 0.00000, 0.00000, -1.50000, -2.59808, -3.00000, -7.00000, -6.06218, -9.52628, -11.00000,
    # -15.00000, -12.99038, -16.45448, -19.00000, -16.45448, -9.50000, -7.50000, -12.99038, -9.52628, -5.50000, -3.50000,
    # -6.06218, -2.59808, -1.50000]

    #SEQUENCE_Z = [0.00000, 3.00000, 2.59808, 6.06218, 7.00000, 11.00000,  9.52628, 12.99038, 15.00000, 19.00000,
    # 16.45448, 9.50000, 0.00000, 0.00000, 7.50000, 5.50000, 0.00000, 0.00000, 3.50000, 1.50000, 0.00000, -1.50000,
    # -2.59808, -6.06218, -3.50000, -5.50000, -9.52628, -12.99038, -7.50000, -9.50000, -16.45448, -19.00000, -16.45448,
    # -12.99038, -15.00000, -11.00000, -9.52628, -6.06218, -7.00000, -3.00000, -2.59808, -1.50000, 0.00000, 0.00000,
    # -3.50000, -5.50000, 0.00000, 0.00000, -7.50000, -9.50000, 0.00000, 9.50000, 16.45448, 12.99038, 7.50000, 5.50000,
    # 9.52628, 6.06218, 3.50000, 1.50000, 2.59808]


    try:
        print("> Initial speed parameters (vt, vr): ", hexapod.get_speed())
        print("> Changing speed parameters")
        hexapod.set_speed(1, 0.2)
        time.sleep(0.002) # this waiting time needs to be added otherwise the command is not took into account
        print("Speed values modified to (vt, vr): ", hexapod.get_speed())

        # Check the initial Hexapod position
        print("> Checking the initial hexapod positions: ")
        print("\r machine: ", hexapod.get_machine_positions())
        print("\r usr: ", hexapod.get_user_positions())
        print("\r actuator lenghts: ", hexapod.get_actuator_length())

        # Add here the coordinate system transformation and verification
        tx_u, ty_u, tz_u = 0, 0, 3
        rx_u, ry_u, rz_u = 0, 0, 0
        tx_o, ty_o, tz_o = 0, 0, 3
        rx_o, ry_o, rz_o = 0, 0, 0

        print("> Changing coordinate systems")
        hexapod.configure_coordinates_systems(tx_u, ty_u, tz_u, rx_u, ry_u, rz_u, tx_o, ty_o, tz_o, rx_o, ry_o, rz_o)

        print("> Coordinate system changed to:", hexapod.get_coordinates_systems())
        print("> Checking hexapod positions after coordinate change: ")
        print("\r machine: ", hexapod.get_machine_positions())
        print("\r usr: ", hexapod.get_user_positions())
        print("\r actuator lenghts: ", hexapod.get_actuator_length())


        print(" == SEQUENCE VALIDATION ==")
        i = 0
        for y in SEQUENCE_Y:
            abs = hexapod.check_absolute_movement(0, 0, 0, 0, y, SEQUENCE_Z[i])
            obj = hexapod.check_relative_object_movement(0, 0, 0, 0, y, SEQUENCE_Z[i])
            usr = hexapod.check_relative_user_movement(0, 0, 0, 0, y, SEQUENCE_Z[i])

            abs = abs[0]
            obj = obj[0]
            usr = usr[0]
            elements = [abs, obj, usr]
            flag = False

            for element in range(len(elements)):
                if elements[element] == 0:
                    elements[element] = True
                else:
                    elements[element] = False
                    flag = True

            print("step : ", i, f"for y, z rotations : ", y, SEQUENCE_Z[i], "\r")
            print("absolute validation: ", elements[0], "\r")
            print("relative object validation: ", elements[1], "\r")
            print("relative user validation: ", elements[2], "\r")
            i += 1

        if flag == True:
            print(" !!!! The sequence was not valid, please check the sequence and start the test again")
            return
        else:
            print(" == SEQUENCE SUCCESSFULLY VALIDATED ==")
            pass

        # Execute the movement sequence, recovering the time required for each sequence step
        print("== EXECUTING THE MOVEMENT SEQUENCE ==")
        print("Initial position:", hexapod.get_user_positions())

        i = 0
        t = []
        s = []
        for y in SEQUENCE_Y:
            time.sleep(0.5)
            t0 = time.time()
            print(f"< Commanding step movement {i} to position (rotY, rotZ): ({y:0.5f}, {SEQUENCE_Z[i]:0.5f})")
            hexapod.move_absolute(0, 0, 0, 0, y, SEQUENCE_Z[i])
            if wait_until(in_position_2, hexapod, interval=0.1, timeout=600):
                assert False

            seq = hexapod.get_user_positions()
            try:
                check_positions(seq, [0, 0, 0, 0, y, SEQUENCE_Z[i]])
                _check = 'OK'
            except AssertionError:
                _check = 'NOK'
            print(f"> Commanded position {i} reached: ({y:.05f}, {SEQUENCE_Z[i]:0.5f}) ", ">>> Measured: ",
                  round(seq[4], 6), round(seq[5], 6), ">>", _check, "(after value assertion)")

            msg = [f"{pos:0.5f}" for pos in seq]
            print(f"seq=[{', '.join(msg)}]")

            t.append(round(time.time()-t0, 4))
            s.append([i, _check])
            time.sleep(0.5)
            i += 1
        print(">> time series for sequence (s):", t)
        print("== TEST SUMMARY ==: ")
        for elements in range(len(t)):
            print("> Sequence validation", s[elements], ">> execution time", t[elements], "\r")
        print("> total sequence time (s):", sum(t))

    finally:
        print("> Returning to zero position")
        print(hexapod.is_in_position())
        time.sleep(0.1) # this waiting time needs to be added otherwise the command is not took into account
        hexapod.goto_zero_position()
        time.sleep(0.01) # this waiting time needs to be added otherwise the command is not took into account

        if wait_until(in_position_2, hexapod, interval=0.1, timeout=600):
            assert False
            #fixme: the is_position is returning an incorrect state here that makes the test end without reaching zero

        time.sleep(30)
        print("> zero position reached")
        position = hexapod.get_user_positions()
        print("Final position:", position)

        hexapod.set_default()
        hexapod.disconnect()