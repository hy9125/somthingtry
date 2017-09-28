# python3

import re


def average_rainfall(input_list):
    total_sum = 0
    total_num = 1
    # Here is where your code should go
    pattern = '**(.*?)**'
    num = re.findall(pattern, input_list)
    if len(num) > 0 and type(num[1]) == int:
        if num == -999:
            print(total_sum / total_num)
        else:
            total_sum += num
            total_num += 1
    else:
        return "That's not a valid input, try again"
    # return "Your computed average as a integer" #<-- change this!

# Don't touch anything below this line.
if __name__ == "__main__":
    import sys

    # We get the arguments assuming that they are a list of *integers*
    rainfall_measurements = sys.argv[1:]

    # We print the average.
    print(average_rainfall(rainfall_measurements))