import os
import json
from difflib import SequenceMatcher
from utils import Logger, response_string_to_list, get_correct_list_from_response_list, print_metrics
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
}


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
    

def report_metric(opts, logger):
    file_name = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.result_file)))
    logger.write(file_name)
    logger.write("\n")
    with open(file_name, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        # print("#example: {}".format(len(data)))
    
    num_asp = 0
    num_opi = 0
    num_alsc = 0
    num_aoe = 0
    num_aesc = 0
    num_pair = 0
    num_triplet = 0

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
            
            res_list = response_string_to_list(example["AE"])
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
        if "OE" in keys:
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
            
            res_list = response_string_to_list(example["OE"])
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
        if "ALSC" in keys:
            response = example["ALSC"]
            tar_num = len(example["aspects"])
            for asp in example["aspects"]:
                asp_term = asp["term"]

                if asp_term != "":
                    num_alsc += 1
                    res_polarity = response[asp_term].strip().lower()
                    res_polarity = modify_to_target_by_edit_distance(res_polarity, list(polarity_mapping.values()), logger, threshold=0.5)
    
                    if res_polarity == asp["polarity"]:
                        tp_alsc += 1
                        tar_num -= 1
                    else:
                        fp_alsc += 1
                else:
                    tar_num -= 1
            fn_alsc += tar_num
                    
        # AOE
        if "AOE" in keys:
            response = example["AOE"]
            for asp in example["aspects"]:
                asp_term = asp["term"]
                if asp_term != "":
                    target_opinions = asp["opinions"]
                    target_opinions = [item.lower() for item in target_opinions]
                    num_aoe += len(target_opinions)

                    res_opinions = response_string_to_list(response[asp_term])
                    if res_opinions != [] and type(res_opinions[0]) != str:
                        res_opinions = []
                    
                    if opts.soft_match:
                        res_opinions, num_modify = modify_to_target_by_edit_distance(res_opinions, target_opinions, logger, threshold=0.5)
                    
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
            num_aesc += len(target_list)

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

            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, target_list, logger, threshold=0.5)
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
            num_pair += len(target_list)

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

            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, target_list, logger, threshold=0.5)

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
            num_triplet += len(target_list)

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
            
            if opts.soft_match:
                res_list, num_modify = modify_to_target_by_edit_distance(res_list, target_list, logger, threshold=0.5)

            correct_list = get_correct_list_from_response_list(target_list, res_list)
            # print(target_list, res_list, correct_list)
            tp_triplet += len(correct_list)
            fp_triplet += len(res_list) - len(correct_list)
            fn_triplet += len(target_list) - len(correct_list)
        # print()
    logger.write("sentence: {}, asp: {}, opi: {}, alsc: {}, aoe: {}, aesc: {}, pair: {}, triplet: {}\n".format(len(data), num_asp, num_opi, num_alsc, num_aoe, num_aesc, num_pair, num_triplet))

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

    # target_opis = ["amazing", "great", "good"]
    # predict_list = ["like", "very good", "great"]
    # new_list, num = modify_to_target_by_edit_distance(predict_list, target_opis, logger)
    # print(new_list, num)

    # target_opis = [["food", "positive", "good"], ["support", "negative", "not like"]]
    # predict_list = [["the food", "very positive", "very good"], ["technology support", "very negative", "not like too much"]]
    # new_list, num = modify_to_target_by_edit_distance(predict_list, target_opis, logger)
    # print(new_list, num)
    
    if "wang" in opts.dataset: 
        # "CON": "conflict",  # wang, 并且 14res 有 4 个 aspect 漏标了 polarity
        polarity_mapping.update(
            {
            "CON": "conflict"
            }
        )
    # print(polarity_mapping)

    logger.write("hard match\n")
    report_metric(opts, logger)

    opts.soft_match = True
    logger.write("soft match\n")
    report_metric(opts, logger)



        
    