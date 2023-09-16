import numpy as np
import calculate as cal
import output as out
import functions as func
import work
import time
from input import num_of_group
from input import iterations
from input import times_of_random
from input import times_of_epsilon
from input import times_of_mab

# NewMAB需要对工人进行两个方面的评价：个人表现+团队贡献。其中，个人表现是工人的固有属性，是要预先定义的；团队贡献是平台估计得到的。
# 只生成一个群组进行仿真，使用Random、Epsilon-Greedy、MAB算法进行比较
# 由于MAB算法由调节因子调节，所以前部应该略大于Epsilon-Greedy算法，后面全面提升
# 预计结果为Random < Epsilon-Greedy < MAB

relation_total, relation_n, relation_pre, workers, person_efficiency, person_co, group_efficiency, min_index \
    = func.mcs_init()
result_of_system = 0


out.print_basic()
start_time = time.time()
for i in range(iterations):
    relation_total, relation_n, relation_pre, workers, person_efficiency, person_co, group_efficiency, min_index \
        = func.mcs_init()

    # Random
    for j in range(times_of_random):
        epsilon = 0
        result_temp = work.system_work_random(workers)
        group_efficiency += result_temp
        relation_total, relation_n = cal.assign_value(result_temp, relation_total, relation_n, workers)
    relation_pre = cal.matrix_calculate(relation_n, relation_pre, relation_total)

    # Epsilon-Greedy
    for k in range(times_of_epsilon):
        epsilon = func.epsilon_make(k)
        result_temp = work.system_work_epsilon(workers, min_index, person_efficiency, epsilon)
        group_efficiency += result_temp[0]
        relation_total, relation_n = cal.assign_value(result_temp[0], relation_total, relation_n, workers)
        min_index = np.argsort(result_temp[1])  # 个人表现从小到大的编号
        for m in range(num_of_group):  # 更新person_efficiency
            person_efficiency[workers[m]] = result_temp[1][m]
            person_efficiency = sorted(person_efficiency, reverse=True)
    relation_pre = cal.matrix_calculate(relation_n, relation_pre, relation_total)

    # New MAB
    for n in range(times_of_mab):
        epsilon = 0.3
        result_temp = work.system_work_mab(workers, min_index, person_efficiency, person_co, n, epsilon)
        group_efficiency += result_temp[0]
        relation_total, relation_n = cal.assign_value(result_temp[0], relation_total, relation_n, workers)
        min_index = np.argsort(result_temp[1])  # 个人表现从小到大的编号

        # 这里relation_pre应该每次循环都更新，然后person_co才能更新
        relation_pre = cal.matrix_calculate(relation_n, relation_pre, relation_total)
        for m in range(num_of_group):
            person_efficiency[workers[m]] = result_temp[1][m]  # 更新person_efficiency
            person_efficiency = sorted(person_efficiency, reverse=True)
            person_co = sum(relation_pre)  # 更新person_co
            person_co = sorted(person_co, reverse=True)

    # Postprocessing
    times_total = times_of_epsilon + times_of_random + times_of_mab
    group_efficiency = func.postprocess(relation_pre, workers, group_efficiency, times_total)
    result_of_system += group_efficiency
    out.print_result(group_efficiency)

end_time = time.time()
out.print_result_of_all(result_of_system)
out.print_time(start_time, end_time)
