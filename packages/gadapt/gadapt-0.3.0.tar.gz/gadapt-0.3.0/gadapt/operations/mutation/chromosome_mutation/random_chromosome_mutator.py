from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.gene import Gene
import random

from gadapt.operations.mutation.chromosome_mutation.base_chromosome_mutator import (
    BaseChromosomeMutator,
)


class RandomChromosomeMutator(BaseChromosomeMutator):

    """
    Random mutation of the chromosome.
    """

    def _mutate_chromosome(self, c: Chromosome, number_of_mutation_genes: int):
        if number_of_mutation_genes == 0:
            return
        genes_to_mutate = list(c)
        random.shuffle(genes_to_mutate)
        var_num = random.randint(1, number_of_mutation_genes)
        for g in genes_to_mutate[:var_num]:
            self._set_random_value(g, c)
        return var_num

    def _set_random_value(self, g: Gene, c: Chromosome):
        g.variable_value = round(
            g.genetic_variable.make_random_value(), g.genetic_variable.decimal_places
        )
        self._gene_mutated(g, c)
