import os
import json
import sys
o_path = os.getcwd()
sys.path.append(o_path)
from utils import Logger
from config import get_opts

# 倾向于更多、更长的识别相应 term
# ABSA <a, s, o>
# aspects: 边界固定，适合字符串硬匹配 （起始位置，字符串内容完全一致）
# sentiment: 种类固定，positive、negative、neutral， 适合字符串硬匹配 
# opinion: 边界较模糊 例如 not like，do not like 表示相同opinion
#           1) 字符串硬匹配   2）编辑距离 相似度
#
# AE: 字符串硬匹配
# OE: 字符串硬匹配   编辑距离相似度软匹配
# ALSC: 
# AOE:
# AESC:
# Pair:
# Triplet:


def report_metric(opts, logger):
    file_name = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.report_metric_file)))

    with open(file_name, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
    
    keys = list(data[0].keys())
    if "AE" in keys:
        tp_ae = 0
        fp_ae = 0
        fn_ae = 0
    if "OE" in keys:
        tp_oe = 0
        fp_oe = 0
        fn_oe = 0
    if "ALSC" in keys:
        tp_alsc = 0
        fp_alsc = 0
        fn_alsc = 0
    if "AOE" in keys:
        tp_aoe = 0
        fp_aoe = 0
        fn_aoe = 0
    if "AESC" in keys:
        tp_aesc = 0
        fp_aesc = 0
        fn_aesc = 0
    if "Pair" in keys:
        tp_pair = 0
        fp_pair = 0
        fn_pair = 0
    if "Triplet" in keys:
        tp_triplet = 0
        fp_triplet = 0
        fn_triplet = 0

    for example in data:
        # AE
        if "AE" in keys:
            asp_list = []
            for asp in example["aspects"]:
                asp_str = " ".join(asp["term"])
                if asp_str != "" and asp_str not in asp_list:
                    asp_list.append(asp_str)
            
            response = example["AE"].strip().strip('[').strip(']')
            res = response.split(',')
            res = [r.strip().strip('\'').strip() for r in res]
            print(res)

            for r in res:
                pass





if __name__ == "__main__":
    opts = get_opts()

    logger_file = "report-metric-" +opts.task + "-" + "-".join(opts.dataset.split("/")) + ".log"
    logger = Logger(file_name=logger_file)

    report_metric(opts, logger)



        
    