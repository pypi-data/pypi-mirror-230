import numpy as np
from numpy import random


# relation_real
def produce_constant(num_of_system):
    relation_real = random.random(size=(num_of_system, num_of_system))
    for i in range(num_of_system):
        relation_real[i] = np.round(relation_real[i], 3)
    relation_var = float(np.var(relation_real))

    # ability_of_workers
    ability_of_workers = abs(np.random.randn(num_of_system))

    for i in range(num_of_system):
        ability_of_workers[i] = np.round(ability_of_workers[i], 3)
    abilities_var = float(np.var(ability_of_workers))

    return relation_real, relation_var, ability_of_workers, abilities_var
