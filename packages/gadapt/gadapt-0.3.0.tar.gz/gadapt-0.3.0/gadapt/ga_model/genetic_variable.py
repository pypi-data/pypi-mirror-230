"""
Genetic variable
"""
import random
import gadapt.ga_model.definitions as definitions


class GeneticVariable:
    def __init__(self, id: int) -> None:
        """
        Genetic variable class defines genes.
        Each gene has a reference to one genetic variable.
        Genetic variable contains common values for genes: variable id, maximal\
            value, minimal value, step.
        Args:
            id (int): identifier of the genetic variable
        """
        self.variable_id = id
        self._standard_deviation = definitions.FLOAT_NAN

    def __eq__(self, other):
        if not isinstance(other, GeneticVariable):
            return False
        return self.variable_id == other.variable_id

    def __hash__(self) -> int:
        return self.variable_id

    @property
    def variable_id(self) -> int:
        """
        Unique ID for genetic variable
        """
        return self._variable_id

    @variable_id.setter
    def variable_id(self, value: int):
        self._variable_id = value

    @property
    def max_value(self) -> float:
        """
        Max gene value
        """
        return self._max_value

    @max_value.setter
    def max_value(self, value: float):
        self._max_value = value

    @property
    def min_value(self) -> float:
        """
        Min gene value
        """
        return self._min_value

    @min_value.setter
    def min_value(self, value: float):
        self._min_value = value

    @property
    def step(self) -> float:
        """
        Optimization step
        """
        return self._step

    @step.setter
    def step(self, value: float):
        self._decimal_places = self._get_decimal_places(value)
        self._step = value

    def _get_decimal_places(self, f: float) -> int:
        dp = str(f)[::-1].find(".")
        if dp == -1:
            return 0
        return dp

    @property
    def decimal_places(self) -> int:
        """
        Number of decimal places of the gene value
        """
        return self._decimal_places

    @property
    def stacked(self) -> bool:
        """
        Indicates if all genes have the same value for the same genetic variable
        """
        return self._stacked

    @stacked.setter
    def stacked(self, value: bool):
        self._stacked = value

    @property
    def relative_standard_deviation(self) -> float:
        """
        Relative standard deviation of all genes for the same genetic variable
        """
        return self._standard_deviation

    @relative_standard_deviation.setter
    def relative_standard_deviation(self, value: float):
        self._standard_deviation = value

    def make_random_value(self):
        """
        Makes random value, based on min value, max value, and step
        """
        number_of_steps = random.randint(
            0, round((self.max_value - self.min_value) / self.step)
        )
        return self.min_value + number_of_steps * self.step
