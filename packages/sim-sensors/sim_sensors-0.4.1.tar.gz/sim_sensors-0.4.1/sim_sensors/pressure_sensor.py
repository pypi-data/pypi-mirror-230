import random


class PressureSensor:
    """
    PressureSensor simulates a barometric pressure sensor.
    The constructor parameters are:
        previous: the initial pressure value in hPa
        step: the step to increase or decrease the pressure value
    Both parameters are optional.
    """

    MIN_PRESSURE = 950.0  # hPa, might be seen during a strong storm
    MAX_PRESSURE = 1050.0  # hPa, high pressure during cold, clear conditions

    def __init__(self, previous=1013.25, step=1.0):
        self._previous = previous
        self._step = step

    def read_pressure(self):
        """
        Simulates reading from the pressure sensor by either increasing or decreasing
        the previous pressure level based on a random step value.
        """
        step_variation = random.uniform(-self._step, self._step)
        current = self._previous + step_variation

        # Ensure pressure remains within the defined range
        current = max(self.MIN_PRESSURE, min(self.MAX_PRESSURE, current))

        self._previous = current
        return current
