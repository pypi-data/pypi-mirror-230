import random


class UVSensor:
    """
    UVSensor simulates an ultraviolet (UV) sensor.
    The constructor parameters are:
        previous: the initial UV index value
        step: the step to increase or decrease the UV index value
    Both parameters are optional.
    """

    MIN_UV_INDEX = 0.0  # Lowest UV index value
    MAX_UV_INDEX = 11.0  # Extreme UV index value

    def __init__(self, previous=5.0, step=0.5):
        self._previous = previous
        self._step = step

    def read_uv_index(self):
        """
        Simulates reading from the UV sensor by either increasing or decreasing
        the previous UV index based on a random step value.
        """
        step_variation = random.uniform(-self._step, self._step)
        current = self._previous + step_variation

        # Ensure UV index remains within the defined range
        current = max(self.MIN_UV_INDEX, min(self.MAX_UV_INDEX, current))

        self._previous = current
        return current
