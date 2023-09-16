import numpy as np
import random
import math
import functions as func


class worker:
    def __init__(self, num, ability_of_workers):
        # self.num = num
        self.mu = ability_of_workers[num]
        # self.mu = 1
        self.sigma = 0.01

    def person_work(self):
        worker_result = np.random.normal(self.mu, self.sigma, 1)
        return worker_result


def group_work(workers, relation_real, num_of_group, ability_of_workers):
    group_result = 0
    person_result = np.zeros(num_of_group)

    for i in range(num_of_group):
        person_result[i] = worker(workers[i], ability_of_workers).person_work()
        for j in range(num_of_group):
            if i != j:
                group_result += person_result[i] * (relation_real[workers[i]][workers[j]])
    group_result = group_result / (num_of_group * (num_of_group - 1))
    return group_result, person_result


def result_solve(num_choice, pos_choice, workers, reselection_flag, num_of_group, relation_real, ability_of_workers):
    if reselection_flag == 1:
        result = group_work(workers, relation_real, num_of_group, ability_of_workers)
    else:
        for k in range(int(num_of_group * 0.2)):
            workers[int(pos_choice[k])] = int(num_choice[k])
        result = group_work(workers, relation_real, num_of_group, ability_of_workers)
    return result


def system_work_random(workers, num_of_group, num_of_system, relation_real, ability_of_workers):
    pos_choice = np.zeros(num_of_system)
    num_choice = np.zeros(num_of_system)
    reselection_flag = 0

    for i in range(int(num_of_group * 0.2)):
        pos_choice[i] = random.randint(0, (num_of_group - 1))
        num_choice[i] = random.randint(0, (num_of_system - 1))
        reselection_flag = func.reselection_judge(workers, num_choice, i, num_of_group)
    result = result_solve(num_choice, pos_choice, workers, reselection_flag, num_of_group, relation_real, ability_of_workers)
    return result[0]


def system_work_epsilon(workers, min_index, person_efficiency, epsilon, num_of_system, num_of_group, relation_real, ability_of_workers):
    pos_choice = np.zeros(num_of_system)
    num_choice = np.zeros(num_of_system)
    reselection_flag = 0

    for i in range(int(num_of_group * 0.2)):
        pos_choice[i] = min_index[i]
        if random.random() < epsilon:
            num_choice[i] = random.randint(0, (num_of_system - 1))
        else:
            num_choice[i] = person_efficiency[i]
        reselection_flag = func.reselection_judge(workers, num_choice, i, num_of_group)
    result = result_solve(num_choice, pos_choice, workers, reselection_flag, num_of_group, relation_real, ability_of_workers)
    return result


def system_work_mab(workers, min_index, person_efficiency, person_co, times, epsilon, num_of_system, num_of_group, relation_real, ability_of_workers):
    pos_choice = np.zeros(num_of_system)
    num_choice = np.zeros(num_of_system)
    regulatory_factor = float(1 / (1 + math.exp(-times)))  # 调节因子，当times的原点位置不加以修正的时候，达到了更好的效果
    reselection_flag = 0

    # 对person_efficiency和person_co进行归一化，并组合出一个“综合能力”用于贪心算法的选择
    person_co_n = func.normalization(person_co, num_of_system)
    person_co_n = np.array(person_co_n)
    person_efficiency_n = func.normalization(person_efficiency, num_of_system)
    person_efficiency_n = np.array(person_efficiency_n)
    person_comprehensive = (person_co_n * regulatory_factor) + (person_efficiency_n * (1 - regulatory_factor))
    person_comprehensive = sorted(person_comprehensive, reverse=True)

    for i in range(int(num_of_group * 0.5)):
        pos_choice[i] = min_index[i]    # 剔除通过个人能力，选取通过综合能力
        if random.random() < epsilon:
            num_choice[i] = random.randint(0, (num_of_system - 1))
        else:
            num_choice[i] = person_comprehensive[i]
        reselection_flag = func.reselection_judge(workers, num_choice, i, num_of_group)
    result = result_solve(num_choice, pos_choice, workers, reselection_flag, num_of_group, relation_real, ability_of_workers)
    return result
