import time as tm
import os
from termcolor import colored
import numpy as np
os.system('color')
counter = None


class ProgressBar(object):
    def __init__(self, time0):
        self.__time0__ = time0

    def printProgressBar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """

        percent = colored(("{0:." + str(decimals) + "f}").format(100 * (iteration / np.float64(total))), 'red')
        filledLength = int(length * iteration // total)
        percent_sign = colored('%', 'red')
        bar = fill * filledLength + '-' * (length - filledLength)
        time_elapsed = ' ' + str(int(tm.time() - self.__time0__)) + ' sec'
        print(f'\r{prefix} |{bar}| {percent}{percent_sign}{time_elapsed} {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()
