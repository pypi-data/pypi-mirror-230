

def print_basic(relation_real, num_of_system, num_of_group, relation_var, abilities_var, ability_of_workers):
    relation_average = sum(sum(relation_real)) / (num_of_system * num_of_system)
    abilities_average = sum(ability_of_workers) / num_of_system
    print("\033[1;30;47mBasic constants:\033[0m")
    print("   The number of workers in a group is ", num_of_group)
    print("   The number of workers in the system is ", num_of_system)
    print("   The variance of the relation is ", relation_var)
    print("   The variance of the abilities is ", abilities_var)
    print("   The average of the relation is ", relation_average)
    print("   The average of the abilities is ", abilities_average)
    print("\033[1;30;47mThe results of system:\033[0m")


def print_result(group_efficiency):
    print("   The average result of the group is ", group_efficiency)


def print_result_of_all(sum_of_result, iterations):
    print("\033[1;32mThe final result of iterations is \033[0m", sum_of_result / iterations)


def print_time(start, end):
    run_time = end - start
    print("\033[1;32mThe time cost of iterations is \033[0m", run_time)
