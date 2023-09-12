import random


class LightSensor:
    """
    LightSensor simulates an ambient light sensor.
    The constructor parameters are:
        previous: the initial light value in lux
        step: the step to increase or decrease the light value
    Both parameters are optional.
    """

    MIN_LUX = 100.0  # Dimly lit room
    MAX_LUX = 1000.0  # Very brightly lit room

    def __init__(self, previous=500.0, step=50.0):
        self._previous = previous
        self._step = step

    def read_illuminance(self):
        """
        Simulates reading from the light sensor by either increasing or decreasing
        the previous light level based on a random step value.
        """
        step_variation = random.uniform(-self._step, self._step)
        current = self._previous + step_variation

        # Ensure light level remains within the defined range
        current = max(self.MIN_LUX, min(self.MAX_LUX, current))

        self._previous = current
        return current
