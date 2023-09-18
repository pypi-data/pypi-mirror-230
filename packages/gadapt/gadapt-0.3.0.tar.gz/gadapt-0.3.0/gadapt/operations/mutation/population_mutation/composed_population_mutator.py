import random
from typing import List
from gadapt.ga_model.ga_options import GAOptions
from gadapt.operations.mutation.population_mutation.base_population_mutator import (
    BasePopulationMutator,
)


class ComposedPopulationMutator(BasePopulationMutator):
    def __init__(self, options: GAOptions) -> None:
        """
        Population mutator that consists of more different population mutators
        Args:
            options: genetic algorithm options
        """
        super().__init__(options)
        self.mutators: List[BasePopulationMutator] = []

    def append(self, mutator: BasePopulationMutator):
        """
        Appends mutator to the composition of mutators
        """
        self.mutators.append(mutator)

    def _mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        if len(self.mutators) == 0:
            raise Exception("at least one mutator must be added")
        random.shuffle(self.mutators)
        nmc = 0
        for m in self.mutators:
            if nmc < number_of_mutation_chromosomes:
                nmc += m._mutate_population(
                    population, number_of_mutation_chromosomes - nmc
                )
