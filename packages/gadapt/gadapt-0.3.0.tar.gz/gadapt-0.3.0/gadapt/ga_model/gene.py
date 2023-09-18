"""
Gene
"""
import math
from gadapt.ga_model.genetic_variable import GeneticVariable
from gadapt.ga_model.ranking_model import RankingModel
import gadapt.adapters.string_operation.ga_strings as ga_strings
import gadapt.ga_model.definitions as definitions


class Gene(RankingModel):
    def __init__(self, gen_variable, var_value=None):
        """
        Gene class. Gene is a part of chromosome.
        It contains concrete values for genetic variables.
        Args:
            gen_variable: Genetic variable which defines the gene
            var_value: Value of the gene
        """
        super().__init__()
        self.genetic_variable = gen_variable
        self.variable_value = var_value
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN
        if self.variable_value is None or math.isnan(self.variable_value):
            self.set_random_value()

    def __str__(self) -> str:
        return self._to_string()

    def _to_string(self):
        return ga_strings.gene_to_string(self)

    @property
    def genetic_variable(self) -> GeneticVariable:
        """
        Genetic variable which defines the gene
        """
        return self._genetic_variable

    @genetic_variable.setter
    def genetic_variable(self, value: GeneticVariable):
        if not isinstance(value, GeneticVariable):
            pass
            raise
        self._genetic_variable = value

    @property
    def variable_value(self):
        """
        Value of the gene
        """
        return self._variable_value

    @variable_value.setter
    def variable_value(self, value):
        self._variable_value = value

    def set_random_value(self):
        """
        Sets a random value for the variable_value property
        """
        self.variable_value = self.genetic_variable.make_random_value()
