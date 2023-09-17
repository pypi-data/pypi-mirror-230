

def assign_value(result_of_system, relation_total, relation_n, workers, num_of_group):
    for i in range(num_of_group):
        for j in range(num_of_group):
            if i != j:
                relation_total[workers[i]][workers[j]] += result_of_system
                relation_n[workers[i]][workers[j]] += 1
    return relation_total, relation_n


def matrix_calculate(relation_n, relation_pre, relation_total, num_of_system):
    # Random和Epsilon放在最后统一计算，MAB是每次任务都要计算
    for i in range(num_of_system):
        for j in range(num_of_system):
            if relation_n[i][j] == 0:
                relation_pre[i][j] = round(relation_total[i][j], 3)
            else:
                relation_pre[i][j] = round(relation_total[i][j] / relation_n[i][j], 3)
    return relation_pre
