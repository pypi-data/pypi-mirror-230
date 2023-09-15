import logging
import threading

import time

from egse.hk import get_housekeeping
from egse.state import GlobalState
from egse.tempcontrol.beaglebone.beaglebone import BeagleboneProxy
from egse.tempcontrol.spid.spid import PidInterface, PidError

logger = logging.getLogger(__name__)


class PidController(PidInterface):

    # Prefixes for prometheus metrics based on agilent device index
    PREFIXES = ["GSRON_AG34972_0_T", "GSRON_AG34972_1_T", "GSRON_AG34970_0_T", "GSRON_AG34970_1_T"]

    def __init__(self):

        # Get spid setup entry
        setup = GlobalState.setup

        heaters = setup.gse.spid.configuration.heaters

        self.channels = [channel for heater in heaters.values() for channel in heater]

        self.update_period = setup.gse.spid.configuration.update_period
        self.temperature_timeout = setup.gse.spid.configuration.temperature_timeout
        self.timeout_action = setup.gse.spid.configuration.timeout_action

        self._is_connected = False
        self._pid_thread = None
        self._beaglebone = BeagleboneProxy()
        self._t0 = None

        self.setpoints = [float(0)] * len(self.channels)
        self.running = [False] * len(self.channels)
        self.pids = []

        # Store these values for HK
        self.inputs         = [float(0)] * len(self.channels)
        self.errors         = [float(0)] * len(self.channels)
        self.outputs        = [float(0)] * len(self.channels)
        self.temperature    = [float(0)] * len(self.channels)
        self.timestamp      = [float(0)] * len(self.channels)
        self.isum           = [float(0)] * len(self.channels)

        for i in range(len(self.channels)):
            self.pids.append( # initialize with parameters from setup
                PidAlgorithm(self.channels[i][5], self.channels[i][6], 0))

        self.connect()


    def connect(self):

        if self._is_connected:
            logger.warning("Trying to connect to an already connected device")
        else:
            self._beaglebone.connect()
            self._t0 = time.time()
            self._pid_thread = threading.Thread(target=self.thread_function, daemon=True)
            self._pid_thread.daemon = True
            self._is_connected = True
            self._pid_thread.start()


    def disconnect(self):

        if not self._is_connected:
            logger.warning("Trying to disconnect to an already disconnected device")
        else:
            # NOTE: right now the time to stop the thread could take the entire update period
            self._is_connected = False
            self._pid_thread.join()
            self._beaglebone.disconnect()


    def reconnect(self):

        if self._is_connected:
            self.disconnect()
        self.connect()


    def is_connected(self):

        return self._is_connected


    def is_simulator(self):

        return False

    def get_pid_parameters(self, channel):
        Kp, Ki, Kd, int_max, int_min = self.pids[channel].Kp, self.pids[channel].Ki, self.pids[channel].Kd, self.pids[channel].int_max, self.pids[channel].int_min
        logger.info(f"Current PID parameters for channel {channel}:\n\
                      Kp: {Kp}, Ki: {Ki}, Kd: {Kd}\n\
                      Integral max: {int_max}\n\
                      Integral min: {int_min}")
        return Kp, Ki, Kd, int_max, int_min
    
    def set_pid_parameters(self, channel, Kp, Ki, Kd, int_max=1000, int_min=0, reset=True):
        logger.info(f"Setting PID parameters for channel {channel}:\n\
                      Kp: {Kp}, Ki: {Ki}, Kd: {Kd}\n\
                      Integral max: {int_max}\n\
                      Integral min: {int_min}\n\
                      Reset: {reset}")
        
        self.pids[channel].Kp = Kp
        self.pids[channel].Ki = Ki
        self.pids[channel].Kd = Kd
        self.pids[channel].int_min = int_min
        self.pids[channel].int_max = int_max
        if reset:
            self.pids[channel].intergral = 0
            self.pids[channel].prev_error = 0

    def set_temperature(self, channel, setpoint):

        logger.info(f'set PID {channel} to {setpoint}C')

        if channel not in range(len(self.channels)):
            raise PidError(f'channel number {channel} is not defined')

        self.setpoints[channel] = setpoint


    def get_temperature(self, channel):
        if channel not in range(len(self.channels)):
            raise PidError(f'channel number {channel} is not defined')

        return self.setpoints[channel]


    def enable(self, channel):
        logger.info(f'PID {channel} has been enabled')

        if channel not in range(len(self.channels)):
            raise PidError(f'channel number {channel} is not defined')

        self.running[channel] = True


    def disable(self, channel):
        logger.info(f'PID {channel} has been disabled')

        if channel not in range(len(self.channels)):
            raise PidError(f'channel number {channel} is not defined')

        self.running[channel] = False
        _, _, _, htr_idx, ch_idx, _, _, _ = self.channels[channel]
        self._beaglebone.set_enable(htr_idx, ch_idx, False)
        
    def get_running(self, channel):
        return self.running[channel]


    def thread_function(self):

        while self._is_connected:

            for i, (_, agilent_index, agilent_channel, bb_index, bb_channel, _, _, _) \
                    in enumerate(self.channels):

                # skip uninitialized channels
                if self.setpoints[i] is float('nan'):
                    continue

                # Don't step the PID for unenabled channels to avoid a large I sum
                if not self.running[i]:
                    continue

                # construct prometheus metric name
                metric_name = self.PREFIXES[agilent_index] + str(agilent_channel)

                # get temperature from prometheus
                try:
                    self.timestamp[i], self.temperature[i] = get_housekeeping(f'{metric_name}')

                except Exception as e:
                    logger.warning(f'could not get {metric_name} for pid loop {i} ({e})')
                    continue

                # Check if the temperature is recently updated
                age = time.time() - self.timestamp[i]
                if age < self.temperature_timeout:
                    # Update the pid loop
                    self.inputs[i]  = float(self.temperature[i])
                    self.errors[i]  = self.setpoints[i] - self.inputs[i]
                    self.outputs[i] = self.pids[i].compute_step(self.errors[i])
                    self.isum[i]    = self.pids[i].integral

                    # logger.info(f'PID {i}: error = {self.errors[i]:.2f}, '
                    #              f'output = {100 * self.outputs[i]:.2f}%')
                else:
                    logger.warning(f'pid loop {i} temperature outdated {metric_name} ({age}s)')

                    if self.timeout_action == 'heater_off':
                        self.errors[i] = None
                        self.outputs[i] = 0

                if self.outputs[i] == 0:
                    self._beaglebone.set_enable(bb_index, bb_channel, False)
                    # logger.info("PID output is zero")

                else:
                    self._beaglebone.set_enable(bb_index, bb_channel, True)

                    # logger.info(f'Set heater {bb_index}.{bb_channel} to {int(self.outputs[i] * 100)}%')
                    self._beaglebone.set_period(bb_index, bb_channel, 10000) # PWM period in ns
                    self._beaglebone.set_duty_cycle(
                        bb_index, bb_channel, int(self.outputs[i] * 10000)) # duty cycle in ns

            # sleep for what is left of the update period
            t1 = time.time()
            dt = self.update_period - (t1 - self._t0)
            dt = max(dt, 0)
            time.sleep(dt)
            self._t0 = time.time()


class PidAlgorithm:

    def __init__(self, Kp, Ki, Kd):

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        logger.info(f"Kp: {self.Kp}, Ki: {self.Ki}, Kd: {self.Kd}")
        self.int_max = 1000
        self.int_min = 0

        self.out_max = 0.9
        self.out_min = 0.0

        self.prev_time = None
        self.integral = 0.0
        self.prev_error = 0.0


    def compute_step(self, error):

        if self.prev_time is None:
            self.prev_time = time.time()

        dt = time.time() - self.prev_time
        self.prev_time = time.time()

        self.integral += error * dt

        if self.integral > self.int_max:
            self.integral = self.int_max

        if self.integral < self.int_min:
            self.integral = self.int_min
        
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        if output > self.out_max:
            output = self.out_max

        if output < self.out_min:
            output = self.out_min

        return output


def main():
    pid = PidController()
    # pid.set_temperature(2, -40)


if __name__ == '__main__':
    main()
