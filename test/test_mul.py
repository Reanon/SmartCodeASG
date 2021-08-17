# -*-coding:utf-8-*-
import math
import datetime
import multiprocessing as mp


def train_on_parameter(name, param):
    result = 0
    for num in param:
        result += math.sqrt(num * math.tanh(num) / math.log2(num) / math.log10(num))
    return {name: result}


if __name__ == '__main__':

    start_t = datetime.datetime.now()

    num_cores = int(mp.cpu_count())
    print("本地计算机有: " + str(num_cores) + " 核心")
    pool = mp.Pool(num_cores)
    param_dict = {'task1': list(range(10, 30000000)),
                  'task2': list(range(30000000, 60000000)),
                  'task3': list(range(60000000, 90000000)),
                  'task4': list(range(90000000, 120000000)),
                  'task5': list(range(120000000, 150000000)),
                  'task6': list(range(150000000, 180000000)),
                  'task7': list(range(180000000, 210000000)),
                  'task8': list(range(210000000, 240000000))}
    results = [pool.apply_async(train_on_parameter, args=(name, param)) for name, param in param_dict.items()]
    results = [p.get() for p in results]

    end_t = datetime.datetime.now()
    elapsed_sec = (end_t - start_t).total_seconds()
    print("多进程计算 共消耗: " + "{:.2f}".format(elapsed_sec) + " 秒")