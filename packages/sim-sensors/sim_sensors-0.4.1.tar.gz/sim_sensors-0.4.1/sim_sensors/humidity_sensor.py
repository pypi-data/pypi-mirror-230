import random
"""
HumiditySensor simulates a humidity sensor. :)
The constructor parameters are:
    previous: the initial humidity value
    step: the step to increase or decrease the humidity value
Both parameters are optional.
"""

class HumiditySensor:


    def __init__(self, previous = 50.0, step = 5.0):
        self.previous = previous
        self.step = step

    def get_humidity(self):
        if random.randint(0,1) == 1:
            current = self.previous + self.step
        else:
            current = self.previous - self.step

        self.previous = current
        return current