import random


class PHSensor:
    """
    PHSensor simulates a pH sensor for either water or soil.
    The constructor parameters are:
        type: 'water' or 'soil' to specify the type of pH sensor.
        previous: the initial pH value
        step: the step to increase or decrease the pH value
    Both 'previous' and 'step' parameters are optional.
    """

    WATER_PH_RANGE = (6.0, 8.0)  # Typical for clean freshwater
    SOIL_PH_RANGE = (4.0, 9.0)  # Common range for various soils

    def __init__(self, sensor_type='water', previous=7.0, step=0.1):
        if sensor_type not in ['water', 'soil']:
            raise ValueError("Sensor type must be either 'water' or 'soil'")

        self._type = sensor_type
        self._previous = previous
        self._step = step

    def read_ph(self):
        """
        Simulates reading from the pH sensor by either increasing or decreasing
        the previous pH level based on a random step value.
        """
        step_variation = random.uniform(-self._step, self._step)
        current = self._previous + step_variation

        # Ensure pH level remains within the defined range based on sensor type
        if self._type == 'water':
            current = max(self.WATER_PH_RANGE[0], min(self.WATER_PH_RANGE[1], current))
        else:
            current = max(self.SOIL_PH_RANGE[0], min(self.SOIL_PH_RANGE[1], current))

        self._previous = current
        return current
