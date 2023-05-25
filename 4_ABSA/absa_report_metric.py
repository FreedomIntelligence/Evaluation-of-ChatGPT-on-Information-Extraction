import os
import json
import sys
from difflib import SequenceMatcher
from config import get_opts
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, response_string_to_list, get_correct_list_from_response_list, print_metrics, get_f1


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
}

# dump to files
def dump_result_to_file(fw, opts, task, tp, fp, fn):
    p, r, f1 = 0.0, 0.0, 0.0

    if tp + fp != 0:
        p = 1.0 * tp / (tp + fp)
    if tp + fn != 0:
        r = 1.0 * tp / (tp + fn)
    if p + r != 0.0:
        f1 = 2.0 * p * r / (p + r)

    if opts.soft_match:
        mode = "soft"
    else:
        mode = "hard"

    result_dict ={
        "dataset": opts.dataset,
        "result_file": opts.result_file, 
        "mode": mode,
        "task": task,
        "f1": round(f1, 5),
        "p": round(p, 5),
        "r": round(r, 5),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tp+fn": tp+fn
    }
    fw.write(json.dumps(result_dict, ensure_ascii=False) + "\n")

# soft-matching
def modify_to_target_by_edit_distance(predict_list, target_list, logger, threshold=0.5):
    """
    very good --> good
    not like too much --> not like
    """
    ## str
    if type(predict_list) == str:
        if len(target_list) == 0:
            return predict_list
        else:
            similarity_list = [SequenceMatcher(a=predict_list, b=item).ratio() for item in target_list]
            max_score = max(similarity_list)
            if max_score > threshold:
                max_index = similarity_list.index(max_score)
                target_item = target_list[max_index].lower().strip()
                if target_item != predict_list and (target_item in predict_list or predict_list in target_item):
                    return target_item
            return predict_list

    ## list  
    if len(predict_list) == 0 or len(target_list) == 0:
        return predict_list, 0
    else:
        num_modify = 0
        if isinstance(predict_list[0], str):
            new_predict_list = []
            for pred in predict_list:
                pred = pred.strip()
                similarity_list = [SequenceMatcher(a=pred, b=item).ratio() for item in target_list]
                max_score = max(similarity_list)
                if max_score > threshold:
                    max_index = similarity_list.index(max_score)
                    target_item = target_list[max_index].lower().strip()
                    if target_item != pred and (target_item in pred or pred in target_item):
                        num_modify += 1
                        new_predict_list.append(target_item)
                        # logger.write("'{}' -> '{}'\n".format(pred, target_item))
                    else:
                        new_predict_list.append(pred)
                else:
                    new_predict_list.append(pred)

            return new_predict_list, num_modify
        
        elif isinstance(predict_list[0], list):
            target_item_list = []
            for i in range(len(target_list[0])):
                tmp = []
                for item in target_list:
                    tmp.append(item[i])
                target_item_list.append(tmp)

            for pred in predict_list:
                for i in range(len(pred)):
                    pred_item = pred[i].strip()
                    similarity_list = [SequenceMatcher(a=pred_item, b=item).ratio() for item in target_item_list[i]]
                    max_score = max(similarity_list)
                    if max_score > threshold:
                        max_index = similarity_list.index(max_score)
                        target_item_max_index =  target_item_list[i][max_index].lower().strip()
                        if target_item_max_index != pred_item and (target_item_max_index in pred_item or pred_item in target_item_max_index):
                            num_modify += 1
                            pred[i] = target_item_max_index
                            # logger.write("'{}' -> '{}'\n".format(pred_item, target_item_max_index))
            return predict_list, num_modify
                    
        else:
            logger.write("[ERROR]: unsupported type.\n")      

# report metric by task
def report_metric_by_key(opts, key, result_file, logger, dump_to_file=False):
    file_name = os.path.join(opts.result_dir, opts.task, opts.dataset, result_file)
    logger.write(file_name)
    logger.write("\n")
    with open(file_name, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
    
    num_asp = 0
    num_opi = 0
    num_alsc = 0
    num_aoe = 0
    num_aesc = 0
    num_pair = 0
    num_triplet = 0
    num_invalid = 0

    if "AE" == key:
        tp_ae = 0
        fp_ae = 0
        fn_ae = 0
    if "OE" == key:
        tp_oe = 0
        fp_oe = 0
        fn_oe = 0
    if "ALSC" == key or "ALSC_wang" == key:
        tp_alsc = 0
        fp_alsc = 0
        fn_alsc = 0
    if "AOE" == key:
        tp_aoe = 0
        fp_aoe = 0
        fn_aoe = 0
    if "AESC" == key or "AESC_wang" == key:
        tp_aesc = 0
        fp_aesc = 0
        fn_aesc = 0
    if "Pair" == key:
        tp_pair = 0
        fp_pair = 0
        fn_pair = 0
    if "Triplet" == key:
        tp_triplet = 0
        fp_triplet = 0
        fn_triplet = 0

    for example in data:
        # AE
        if "AE" == key:
            asp_list = []
            asp_span_list = []  # asp_str 有可能重复，但是 asp_span 不重复
            for asp in example["aspects"]:
                asp_str = asp["term"]
                if asp_str != "":
                    asp_span = str(asp["span"][0]) + "#" + str(asp["span"][1])
                    if asp_span not in asp_span_list:
                        asp_span_list.append(asp_span)
                        asp_list.append(asp_str)
            # 转小写
            asp_list = [item.lower() for item in asp_list]
            num_asp += len(asp_list)
            response = example["AE"]
            if "cot" in result_file:
                response = response.replace("answer is", "answer:")
                response = response.split("answer:")[-1].strip()
            res_list, flag = response_string_to_list(response)
            if not flag:
                num_invalid += 1
            if res_list != [] and type(res_list[0]) != str:
                res_list = []
            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, asp_list, logger, threshold=0.5)
                # logger.write("number of modify: {}\n".format(num_modify))
            correct_list = get_correct_list_from_response_list(asp_list, res_list)
            # print(correct_list)
            tp_ae += len(correct_list)
            fp_ae += len(res_list) - len(correct_list)
            fn_ae += len(asp_list) - len(correct_list)
        # OE    
        if "OE" == key:
            opi_list = []
            opi_span_list = []  # opi_str 有可能重复， 但是 opi_span 不重复
            for opi in example["opinions"]:
                opi_str = opi["term"]
                if opi_str != "":
                    opi_span = str(opi["span"][0]) + "#" + str(opi["span"][1])
                    if opi_span not in opi_span_list:
                        opi_span_list.append(opi_span)
                        opi_list.append(opi_str)
            
            opi_list = [item.lower() for item in opi_list]
            num_opi += len(opi_list)
            response = example["OE"]
            if "cot" in result_file:
                response = response.replace("answer is", "answer:")
                response = response.split("answer:")[-1].strip()
            res_list, flag = response_string_to_list(response)
            if not flag:
                num_invalid += 1
            if res_list != [] and type(res_list[0]) != str:
                res_list = []
            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, opi_list, logger, threshold=0.5)

            correct_list = get_correct_list_from_response_list(opi_list, res_list)
            # print(correct_list)
            tp_oe += len(correct_list)
            fp_oe += len(res_list) - len(correct_list)
            fn_oe += len(opi_list) - len(correct_list)
        # ALSC
        if "ALSC" == key or "ALSC_wang" == key:
            res_flag = True
            if "ALSC" == key:
                response = example["ALSC"]
            elif "ALSC_wang" == key:
                response = example["ALSC_wang"]
            tar_num = len(example["aspects"])
            for asp in example["aspects"]:
                asp_term = asp["term"]

                if asp_term != "":
                    num_alsc += 1
                    cur_response = response[asp_term]
                    # print(cur_response)
                    if "cot" in result_file:
                        if "The sentiment polarity is" in cur_response and "answer:" not in cur_response:
                            cur_response = cur_response.split(" ")[4]
                        else:
                            cur_response = cur_response.replace("answer is", "answer:")
                            cur_response = cur_response.split("answer:")[-1].strip()
                        # print(cur_response)
                    res_polarity = cur_response.strip().lower()
                    if opts.soft_match:
                        res_polarity = modify_to_target_by_edit_distance(res_polarity, list(polarity_mapping.values()), logger, threshold=0.5)

                    if res_polarity not in ["positive", "negative", "neutral", "conflict"]:
                        res_flag = False
                        # print(cur_response)
    
                    if res_polarity == asp["polarity"]:
                        tp_alsc += 1
                        tar_num -= 1
                    else:
                        fp_alsc += 1
                else:
                    tar_num -= 1

            if not res_flag:
                num_invalid += 1
            fn_alsc += tar_num
                    
        # AOE
        if "AOE" == key:
            res_flag = True
            response = example["AOE"]
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    target_opinions = asp["opinions"]
                    target_opinions = [item.lower() for item in target_opinions]
                    num_aoe += len(target_opinions)

                    cur_response = response[asp_term]
                    if "cot" in result_file:
                        cur_response = cur_response.replace("answer is", "answer:")
                        cur_response = cur_response.split("answer:")[-1].strip()
                    res_opinions, flag = response_string_to_list(cur_response)
                    if not flag:
                        res_flag = False
                    if res_opinions != [] and type(res_opinions[0]) != str:
                        res_opinions = []
                    
                    if opts.soft_match:
                        res_opinions, num_modify = modify_to_target_by_edit_distance(res_opinions, target_opinions, logger, threshold=0.5)
                    
                    correct_list = get_correct_list_from_response_list(target_opinions, res_opinions)
                    # print(correct_list)
                    tp_aoe += len(correct_list)
                    fp_aoe += len(res_opinions) - len(correct_list)
                    fn_aoe += len(target_opinions) - len(correct_list)
            if not res_flag:
                num_invalid += 1
        # AESC
        if "AESC" == key or "AESC_wang" == key:
            target_list = []
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    target_polarity = asp["polarity"]
                    target_list.append([asp_term.lower(), target_polarity])
            num_aesc += len(target_list)

            if "AESC" == key:
                response = example["AESC"]
            elif "AESC_wang" == key:
                response = example["AESC_wang"]
            
            if "cot" in result_file:
                response = response.replace("answer is", "answer:")
                response = response.split("answer:")[-1].strip()

            res_list = []
            tmp_list = response.split('\n')
            res_flag = True
            for tmp in tmp_list:
                # print(type(tmp), tmp)
                tmp_res_list, flag = response_string_to_list(tmp.strip())
                if not flag:
                    res_flag = False

                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
                    if len(tmp_res_list) == 2:
                        res_list.append(tmp_res_list)
                    else:
                        res_flag = False
                if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
                    for tmp in tmp_res_list:
                        if len(tmp) == 2:
                            res_list.append(tmp)
                        else:
                            res_flag = False
            # print(target_list, "###" ,res_list)

            if not res_flag:
                num_invalid += 1
                # print(tmp_list)

            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, target_list, logger, threshold=0.5)
            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(correct_list)
            tp_aesc += len(correct_list)
            fp_aesc += len(res_list) - len(correct_list)
            fn_aesc += len(target_list) - len(correct_list)
        # Pair
        if "Pair" == key:
            target_list = []
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":  
                    # 转小写
                    pair_list = asp["pairs"]
                    for pair in pair_list:
                        pair = [item.lower() for item in pair]
                        target_list.append(pair)
            num_pair += len(target_list)

            response = example["Pair"]
            if "cot" in result_file:
                response = response.replace("answer is", "answer:")
                response = response.split("answer:")[-1].strip()

            res_list = []
            tmp_list = response.split('\n')
            res_flag = True
            for tmp in tmp_list:
                # print(type(tmp), tmp)
                tmp_res_list, flag = response_string_to_list(tmp.strip())
                if not flag:
                    res_flag = False
                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
                    if len(tmp_res_list) == 2:
                        res_list.append(tmp_res_list)
                    if len(tmp_res_list) > 2:
                        a = tmp_res_list[0]
                        for i in range(1, len(tmp_res_list)):
                            res_list.append([a, tmp_res_list[i]])
                    if len(tmp_res_list) == 1:
                        res_flag = False
                if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
                    for tmp in tmp_res_list:
                        if len(tmp) == 1:
                            res_flag = False
                        if len(tmp) == 2:
                            res_list.append(tmp)
                        if len(tmp) > 2:
                            a = tmp[0]
                            for i in range(1, len(tmp)):
                                res_list.append([a, tmp[i]])
            
            if not res_flag:
                num_invalid += 1
                # print(tmp_list)

            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, target_list, logger, threshold=0.5)

            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(target_list, res_list, correct_list)
            tp_pair += len(correct_list)
            fp_pair += len(res_list) - len(correct_list)
            fn_pair += len(target_list) - len(correct_list)
        # Triplet
        if "Triplet" == key:
            target_list = []
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    # 转小写
                    tri_list = asp["triplets"]
                    for tri in tri_list:
                        tri = [item.lower() for item in tri]
                        target_list.append(tri)
            num_triplet += len(target_list)

            response = example["Triplet"]
            if "cot" in result_file:
                response = response.replace("answer is", "answer:")
                response = response.split("answer:")[-1].strip()

            res_list = []
            tmp_list = response.split('\n')
            res_flag = True
            for tmp in tmp_list:
                # print(example["raw_words"], tmp.strip())
                tmp_res_list, flag = response_string_to_list(tmp.strip())
                if not flag:
                    res_flag = False
                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
                    if len(tmp_res_list) == 3:
                        res_list.append(tmp_res_list)
                    else:
                        res_flag = False
                if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
                    for tmp in tmp_res_list:
                        if len(tmp) == 3:
                            res_list.append(tmp)
                        else:
                            res_flag = False
                            
            
            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, target_list, logger, threshold=0.5)
            
            if not res_flag:
                num_invalid += 1
                # print(tmp_list)

            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(target_list, res_list, correct_list)
            tp_triplet += len(correct_list)
            fp_triplet += len(res_list) - len(correct_list)
            fn_triplet += len(target_list) - len(correct_list)
        # print()
    logger.write("sentence: {}, asp: {}, opi: {}, alsc: {}, aoe: {}, aesc: {}, pair: {}, triplet: {}\n".format(len(data), num_asp, num_opi, num_alsc, num_aoe, num_aesc, num_pair, num_triplet))

    if dump_to_file:
        dump_metric_file = os.path.join(os.path.join(opts.result_dir, opts.task), "metric-" + "-".join(opts.dataset.split("/")) + ".json")
        fw = open(dump_metric_file, "a", encoding="utf-8")

    print(num_invalid)

    if "AE" == key: 
        print_metrics(tp_ae, fp_ae, fn_ae, logger, "AE")
        if dump_to_file:
            dump_result_to_file(fw, opts, "AE", tp_ae, fp_ae, fn_ae)
        return get_f1(tp_ae, fp_ae, fn_ae)

    if "OE" == key:
        print_metrics(tp_oe, fp_oe, fn_oe, logger, "OE")
        if dump_to_file:
            dump_result_to_file(fw, opts, "OE", tp_oe, fp_oe, fn_oe)
        return get_f1(tp_oe, fp_oe, fn_oe)
        
    if "ALSC" == key or "ALSC_wang" == key:
        print_metrics(tp_alsc, fp_alsc, fn_alsc, logger, "ALSC")
        if dump_to_file:
            dump_result_to_file(fw, opts, "ALSC", tp_alsc, fp_alsc, fn_alsc)
        return get_f1(tp_alsc, fp_alsc, fn_alsc)
        
    if "AOE" == key:
        print_metrics(tp_aoe, fp_aoe, fn_aoe, logger, "AOE")
        if dump_to_file:
            dump_result_to_file(fw, opts, "AOE", tp_aoe, fp_aoe, fn_aoe)
        return get_f1(tp_aoe, fp_aoe, fn_aoe)
        
    if "AESC" == key or "AESC_wang" == key:
        print_metrics(tp_aesc, fp_aesc, fn_aesc, logger, "AESC")
        if dump_to_file:
            dump_result_to_file(fw, opts, "AESC", tp_aesc, fp_aesc, fn_aesc)
        return get_f1(tp_aesc, fp_aesc, fn_aesc)
        
    if "Pair" == key:
        print_metrics(tp_pair, fp_pair, fn_pair, logger, "Pair")
        if dump_to_file:
            dump_result_to_file(fw, opts, "Pair", tp_pair, fp_pair, fn_pair)
        return get_f1(tp_pair, fp_pair, fn_pair)
        
    if "Triplet" == key:
        print_metrics(tp_triplet, fp_triplet, fn_triplet, logger, "Triplet")
        if dump_to_file:
            dump_result_to_file(fw, opts, "Triplet", tp_triplet, fp_triplet, fn_triplet)
        return get_f1(tp_triplet, fp_triplet, fn_triplet)


def get_metric(opts, logger):

    task_list = ["AE", "OE", "ALSC", "AOE", "AESC", "Pair", "Triplet"] # 
    
    if "wang" in opts.dataset:
        task_list = ["AE", "OE", "ALSC_wang", "AESC_wang"]  # 
    if "fan" in opts.dataset: 
        task_list = ["AOE"]

    for task in task_list:
        file_name = task + "-" + opts.result_file
        report_metric_by_key(opts, task, file_name, logger, dump_to_file=True)
        opts.soft_match = True
        report_metric_by_key(opts, task, file_name, logger, dump_to_file=True)
        opts.soft_match = False



if __name__ == "__main__":
    opts = get_opts()

    logger_file = "report-metric-" + opts.task + "-" + "-".join(opts.dataset.split("/")) + "-" + str(opts.prompt) +".txt"
    logger_file = os.path.join(opts.task, logger_file)
    logger = Logger(file_name=logger_file)
    
    if "wang" in opts.dataset: 
        # "CON": "conflict",  # wang, 并且 14res 有 4 个 aspect 漏标了 polarity
        polarity_mapping.update(
            {
            "CON": "conflict"
            }
        )

    get_metric(opts, logger)

