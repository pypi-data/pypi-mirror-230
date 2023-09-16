import math
import numpy as np
import init_rand as rm


def postprocess(relation_pre, workers, group_efficiency, times_total, num_of_group):
    contribution_of_ones = np.zeros(num_of_group)
    for i in range(num_of_group):
        contribution_of_ones[i] = sum(relation_pre[workers[i]])
    group_efficiency = group_efficiency / times_total
    return group_efficiency


def mcs_init(num_of_group, num_of_system):
    relation_total = np.zeros([num_of_system, num_of_system])
    relation_n = np.zeros([num_of_system, num_of_system])
    relation_pre = np.ones([num_of_system, num_of_system])
    workers = rm.int_list(0, num_of_system - 1, num_of_group)
    person_efficiency = np.ones(num_of_system)  # 工人个体效能估计值，用于贪心算法，找到高效能工人的编号
    person_co = sum(relation_pre)
    group_efficiency = 0.0
    min_index = np.zeros(num_of_group)  # 群组里效能的倒序，用于找到低效能工人的位置并替换
    return relation_total, relation_n, relation_pre, workers, person_efficiency, person_co, group_efficiency, min_index


def normalization(x, num_of_system):  # 归一化函数
    for i in range(num_of_system):
        if max(x) - min(x) == 0:
            x = x
        else:
            x[i] = (x[i] - min(x)) / (max(x) - min(x))
    return x


def reselection_judge(workers, num_choice, i, num_of_group):
    reselection_flag = 0
    for j in range(num_of_group):
        if workers[j] == num_choice[i]:
            reselection_flag = 1
        else:
            reselection_flag = 0
    return reselection_flag


def epsilon_make(times):
    if times == 0:
        epsilon = 1
    else:
        epsilon = 1 / math.sqrt(times)
    return epsilon
