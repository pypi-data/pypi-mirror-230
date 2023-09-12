import random

"""
TempSensor simulates a temperature sensor. :)
The constructor parameters are:
    previous: the initial temperature value
    step: the step to increase or decrease the temperature value
Both parameters are optional.
"""
class TempSensor:

    def __init__(self, previous = 30.0, step = 0.5):
        self.previous = previous
        self.step = step

    def get_temp(self):
        if random.randint(0,1) == 1:
            current = self.previous + self.step
        else:
            current = self.previous - self.step

        self.previous = current
        return current
