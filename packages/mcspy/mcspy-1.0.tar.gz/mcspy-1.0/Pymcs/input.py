num_of_system = int(input("Input the number of workers in the system: "))
num_of_group = int(input("Input the number of workers in a group: "))
print("(r: Random, e: Epsilon-Greedy, m: MAB)")
mode = input("The mode of system: ")
if mode == 'r':
    iterations = int(input("Iterations: "))
    times_of_random = int(input("The turns of random: "))
    times_of_epsilon = 0
    times_of_mab = 0
elif mode == 'e':
    iterations = int(input("Iterations: "))
    times_of_random = 0
    times_of_epsilon = int(input("The turns of E-greedy: "))
    times_of_mab = 0
elif mode == 'm':
    iterations = int(input("Iterations: "))
    times_of_random = 0
    times_of_epsilon = 0
    times_of_mab = int(input("The turns of MAB: "))
