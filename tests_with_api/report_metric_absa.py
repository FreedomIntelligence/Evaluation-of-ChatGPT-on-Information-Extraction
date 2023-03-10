import os
import json
import sys
import ast
import difflib
from difflib import SequenceMatcher
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
# ALSC: 字符串硬匹配
# AOE: 字符串硬匹配  编辑距离相似度软匹配
# AESC: 字符串硬匹配
# Pair: 字符串硬匹配  编辑距离相似度软匹配
# Triplet:  字符串硬匹配  编辑距离相似度软匹配

polarity_mapping = {
    "POS": "positive",
    "NEG": "negative",
    "NEU": "neutral",
    "CON": "conflict",  # wang, 并且 14res 有三个 aspect 漏标了 polarity
}

def edit_distance(str_1, str_2):
    return SequenceMatcher(str_1, str_2).ratio()

def print_metrics(tp, fp, fn, logger, task):
    p, r, f1 = 0.0, 0.0, 0.0

    if tp + fp != 0:
        p = 1.0 * tp / (tp + fp)
    if tp + fn != 0:
        r = 1.0 * tp / (tp + fn)
    if p + r != 0.0:
        f1 = 2.0 * p * r / (p + r)
    logger.write("{} | f1: {:.4f}, p: {:.4f}, r: {:.4f} | tp: {:4d}, fp: {:4d}, fn: {:4d}\n".format(
        task.ljust(8),
        round(f1, 4),
        round(p, 4),
        round(r, 4),
        tp,
        fp,
        fn,
        )
    )

def response_string_to_list(response):
    """return 
        1) string 列表
        2） list  列表
    """
    def get_list_by_string(list_str):
        try:
            res_list = ast.literal_eval(list_str) 
        except:
            res_list = []
        finally:
            return res_list
    
    response = response.lower()
    num_left = response.count("[")

    res_list = []

    if num_left == 0:
        return res_list
    
    if num_left == 1:
        start_idx = response.find('[')
        response = response[start_idx:]
        num_right = response.count("]")
        if num_right < 1:
            return res_list
        else:
            start_idx = response.find('[')
            end_idx = response.find(']')
            span = response[start_idx: end_idx+1]
            res_list = get_list_by_string(span)
            res_list = [res.strip() for res in res_list] 
            return res_list

    # "['a', 'b'], ['c', 'd']"
    start_idx = -1
    end_idx = -1

    for i, ch in enumerate(response):
        if ch == '[':
            start_idx = i
        if ch == ']':
            end_idx = i
        # print(start_idx, end_idx)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            span = response[start_idx: end_idx+1]
            tmp_list = get_list_by_string(span)
            tmp_list = [res.strip() for res in tmp_list] 
            res_list.append(tmp_list)
            start_idx = -1
            end_idx = -1

    return res_list


def has_duplicate(tmp_list):
    """ has duplicate ?
    """
    if tmp_list == []:
        return False
    
    if type(tmp_list[0]) == str:
        if len(tmp_list) == len(set(tmp_list)):
            return False
        else:
            return True
        
    if type(tmp_list[0]) == list:
        tmp = []
        for t in tmp_list:
            if t not in tmp:
                tmp.append(t)
        if len(tmp_list) == len(tmp):
            return False
        else:
            return True
    
def get_correct_list_from_response_list(target_list, response_list):
    """
    target_list 和 response_list 均有可能包含重复的 item
    """
        
    res = []
    if not has_duplicate(response_list):
        res = [item for item in response_list if item in target_list]
    else:
        if not has_duplicate(target_list):
            # 去重
            uni_response_list = []
            for item in response_list:
                if item not in uni_response_list:
                    uni_response_list.append(item)
            res = [item for item in uni_response_list if item in target_list]
        else:
            res = []
            processed_item_list = []
            for item in response_list:
                if item not in processed_item_list:
                    processed_item_list.append(item)

                    num_item = response_list.count(item)
                    if num_item == 1:  # not duplicate
                        if item in target_list:
                            res.append(item)
                    else:  # duplicate
                        if item in target_list:
                            num_item_in_target = target_list.count(item)
                            num_item_correct = min([num_item, num_item_in_target])
                            res += [item] * num_item_correct
    
    return res


def report_metric(opts, logger):
    file_name = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.report_metric_file)))

    with open(file_name, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        print("#example: {}".format(len(data)))
    
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
                asp_str = asp["term"]
                if asp_str != "" and asp_str not in asp_list:
                    asp_list.append(asp_str)
            # 转小写
            asp_list = [item.lower() for item in asp_list]
            
            res_list = response_string_to_list(example["AE"])
            if res_list != [] and type(res_list[0]) != str:
                res_list = []

            correct_list = get_correct_list_from_response_list(asp_list, res_list)
            # print(correct_list)
            tp_ae += len(correct_list)
            fp_ae += len(res_list) - len(correct_list)
            fn_ae += len(asp_list) - len(correct_list)
        # OE    
        if "OE" in keys:
            opi_list = []
            for opi in example["opinions"]:
                opi_str = opi["term"]
                if opi_str != "" and opi_str not in opi_list:
                    opi_list.append(opi_str)
            
            opi_list = [item.lower() for item in opi_list]
            
            res_list = response_string_to_list(example["OE"])
            if res_list != [] and type(res_list[0]) != str:
                res_list = []

            correct_list = get_correct_list_from_response_list(opi_list, res_list)
            # print(correct_list)
            tp_oe += len(correct_list)
            fp_oe += len(res_list) - len(correct_list)
            fn_oe += len(opi_list) - len(correct_list)
        # ALSC
        if "ALSC" in keys:
            response = example["ALSC"]
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    res_polarity = response[asp_term].strip().lower()
                    if res_polarity not in polarity_mapping.values():
                        fn_alsc += 1
                    else:
                        if res_polarity == asp["polarity"]:
                            tp_alsc += 1
                        else:
                            fp_alsc += 1
        # AOE
        if "AOE" in keys:
            response = example["AOE"]
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    target_opinions = asp["opinions"]
                    target_opinions = [item.lower() for item in target_opinions]

                    res_opinions = response_string_to_list(response[asp_term])
                    if res_opinions != [] and type(res_opinions[0]) != str:
                        res_opinions = []
                    
                    correct_list = get_correct_list_from_response_list(target_opinions, res_opinions)
                    # print(correct_list)
                    tp_aoe += len(correct_list)
                    fp_aoe += len(res_opinions) - len(correct_list)
                    fn_aoe += len(target_opinions) - len(correct_list)
        # AESC
        if "AESC" in keys:
            target_list = []
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    target_polarity = asp["polarity"]
                    target_list.append([asp_term.lower(), target_polarity])

            response = example["AESC"]
            res_list = []
            tmp_list = response.split('\n')
            for tmp in tmp_list:
                # print(type(tmp), tmp)
                tmp_res_list = response_string_to_list(tmp.strip())
                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
                    if len(tmp_res_list) == 2:
                        res_list.append(tmp_res_list)
                if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
                    for tmp in tmp_res_list:
                        if len(tmp) == 2:
                            res_list.append(tmp)
            # print(target_list, "###" ,res_list)
            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(correct_list)
            tp_aesc += len(correct_list)
            fp_aesc += len(res_list) - len(correct_list)
            fn_aesc += len(target_list) - len(correct_list)
        # Pair
        if "Pair" in keys:
            target_list = []
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":  
                    # 转小写
                    pair_list = asp["pairs"]
                    for pair in pair_list:
                        pair = [item.lower() for item in pair]
                        target_list.append(pair)

            response = example["Pair"]
            res_list = []
            tmp_list = response.split('\n')
            for tmp in tmp_list:
                # print(type(tmp), tmp)
                tmp_res_list = response_string_to_list(tmp.strip())
                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]

                    if len(tmp_res_list) == 2:
                        res_list.append(tmp_res_list)
                    if len(tmp_res_list) > 2:
                        a = tmp_res_list[0]
                        for i in range(1, len(tmp_res_list)):
                            res_list.append([a, tmp_res_list[i]])
                if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
                    for tmp in tmp_res_list:
                        if len(tmp) == 2:
                            res_list.append(tmp)
                        if len(tmp) > 2:
                            a = tmp[0]
                            for i in range(1, len(tmp)):
                                res_list.append([a, tmp[i]])

            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(target_list, res_list, correct_list)
            tp_pair += len(correct_list)
            fp_pair += len(res_list) - len(correct_list)
            fn_pair += len(target_list) - len(correct_list)
        # Triplet
        if "Triplet" in keys:
            target_list = []
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    # 转小写
                    tri_list = asp["triplets"]
                    for tri in tri_list:
                        tri = [item.lower() for item in tri]
                        target_list.append(tri)

            response = example["Triplet"]
            res_list = []
            tmp_list = response.split('\n')
            for tmp in tmp_list:
                # print(example["raw_words"], tmp.strip())
                tmp_res_list = response_string_to_list(tmp.strip())
                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
                    if len(tmp_res_list) == 3:
                        res_list.append(tmp_res_list)
                if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
                    for tmp in tmp_res_list:
                        if len(tmp) == 3:
                            res_list.append(tmp)

            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(target_list, res_list, correct_list)
            tp_triplet += len(correct_list)
            fp_triplet += len(res_list) - len(correct_list)
            fn_triplet += len(target_list) - len(correct_list)
        # print()

    if "AE" in keys: 
        print_metrics(tp_ae, fp_ae, fn_ae, logger, "AE")
    if "OE" in keys:
        print_metrics(tp_oe, fp_oe, fn_oe, logger, "OE")
    if "ALSC" in keys:
        print_metrics(tp_alsc, fp_alsc, fn_alsc, logger, "ALSC")
    if "AOE" in keys:
        print_metrics(tp_aoe, fp_aoe, fn_aoe, logger, "AOE")
    if "AESC" in keys:
        print_metrics(tp_aesc, fp_aesc, fn_aesc, logger, "AESC")
    if "Pair" in keys:
        print_metrics(tp_pair, fp_pair, fn_pair, logger, "Pair")
    if "Triplet" in keys:
        print_metrics(tp_triplet, fp_triplet, fn_triplet, logger, "Triplet")


if __name__ == "__main__":
    opts = get_opts()

    logger_file = "report-metric-" + opts.task + "-" + "-".join(opts.dataset.split("/")) + ".log"
    logger = Logger(file_name=logger_file)

    report_metric(opts, logger)



        
    