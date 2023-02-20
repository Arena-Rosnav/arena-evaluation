import numpy as np


class Utils:
    @staticmethod
    def string_to_float_list(d):
        if not d:
            return []

        return np.array(d.replace("[", "").replace("]", "").split(r", ")).astype(float)
