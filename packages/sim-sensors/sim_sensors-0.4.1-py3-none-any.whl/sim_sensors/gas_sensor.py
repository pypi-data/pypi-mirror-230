import random


class GasSensor:
    """
    GasSensor simulates various gas sensors including CO2, methane, CO, and air quality.
    The constructor parameters are:
        gas_type: Specifies the type of gas ('CO2', 'methane', 'CO', 'AQI').
        previous: the initial gas concentration
        step: the step to increase or decrease the gas concentration
    Both 'previous' and 'step' parameters are optional.
    """

    GAS_RANGES = {
        'CO2': (400.0, 5000.0),  # ppm
        'methane': (0.5, 5.0),  # ppm
        'CO': (0.0, 50.0),  # ppm
        'AQI': (0, 500)  # Index
    }

    def __init__(self, gas_type='CO2', previous=None, step=10.0):
        if gas_type not in self.GAS_RANGES:
            raise ValueError("Invalid gas type. Choose from 'CO2', 'methane', 'CO', or 'AQI'.")

        self._type = gas_type
        self._previous = previous if previous else self.GAS_RANGES[gas_type][0]
        self._step = step

    def read_concentration(self):
        """
        Simulates reading from the gas sensor by either increasing or decreasing
        the previous gas concentration based on a random step value.
        """
        step_variation = random.uniform(-self._step, self._step)
        current = self._previous + step_variation

        # Ensure concentration remains within the defined range for the gas type
        current = max(self.GAS_RANGES[self._type][0], min(self.GAS_RANGES[self._type][1], current))

        self._previous = current
        return current
