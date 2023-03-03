import os
import json
import sys
o_path = os.getcwd()
sys.path.append(o_path)
from utils import Logger
from config import get_opts


def compute_micro_f1(data, task="AE"):
    keys = list(data[0].keys())
    if task in keys:
        tp = 0
        fp = 0
        fn = 0

        for example in data:
            response = example[task].strip()

def report_metric(opts, result_file_name):
    file_name = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, result_file_name)))

    with open(file_name, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
    
    keys = list(data[0].keys())
    if "AE" in keys:
        tp_ae = 0
        fp_ae = 0
        fn_ae = 0



    for example in data:
        # AE
        if "AE" in keys:
            pass



if __name__ == "__main__":
    opts = get_opts()