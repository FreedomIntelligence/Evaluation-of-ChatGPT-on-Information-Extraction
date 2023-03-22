import os
import json
from difflib import SequenceMatcher
from utils import Logger, print_metrics, get_correct_list_from_response_list
from config import get_opts_ner as get_opts

# 字符串硬匹配   编辑距离相似度软匹配

def modify_to_target_by_edit_distance(predict, target_list, logger, threshold=0.5):
    """
    soft match
    """
    pred = predict.strip()
    if len(target_list) == 0:
        return pred
    similarity_list = [SequenceMatcher(a=pred, b=item).ratio() for item in target_list]
    max_score = max(similarity_list)
    if max_score > threshold:
        max_index = similarity_list.index(max_score)
        target_item = target_list[max_index].lower().strip()
        if target_item != pred and (target_item in pred or pred in target_item):  # 允许 小幅度 span 起始位置不对
            # logger.write("'{}' -> '{}' | {}\n".format(pred, target_item, max_score))
            return target_item

    return pred


def report_metric(opts, logger):

    ## load data
    logger.write("Load file: {}\n".format(opts.result_file))
    logger.write("Load types file: {}\n".format(opts.type_file))

    with open(opts.result_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        e_types = types["entities"]
        if opts.verbose_type:
            e_types_list = [e_types[key]["verbose"].lower() for key in e_types]
        else:
            e_types_list = [e_types[key]["short"].lower() for key in e_types]

    ## per type
    hard_boundaries = dict()
    soft_boundaries = dict()
    for key in e_types_list:
        hard_boundaries[key] = {"tp": 0, "fp": 0, "fn": 0}
        soft_boundaries[key] = {"tp": 0, "fp": 0, "fn": 0}
    
    ## statistics
    num_undefined_type = 0
    num_entity = 0
    tp_ner_boundaries = 0
    fp_ner_boundaries = 0
    fn_ner_boundaries = 0
    tp_ner_strict = 0
    fp_ner_strict = 0
    fn_ner_strict = 0

    tp_ner_boundaries_soft_match = 0
    fp_ner_boundaries_soft_match = 0
    fn_ner_boundaries_soft_match = 0
    tp_ner_strict_soft_match = 0
    fp_ner_strict_soft_match = 0
    fn_ner_strict_soft_match = 0

    ## nested ner
    tp_nested = 0
    fp_nested = 0
    fn_nested = 0
    
    for example in data:
        ## target
        strict_target_list = []
        boundaries_target_list = []

        ## per type
        boundaries_target_list_dict = {}
        for key in e_types_list:
            boundaries_target_list_dict[key] = []

        for ent in example["entities"]:
            ent_name = ent["e_name"].lower()
            if opts.verbose_type:
                ent_type = e_types[ent["e_type"]]["verbose"].lower()  # 全写 
            else:
                ent_type = ent["e_type"].lower()  # 缩写

            strict_target_list.append([ent_type, ent_name])  
            boundaries_target_list.append(ent_name)

            ## per type
            boundaries_target_list_dict[ent_type].append(ent_name)
            
            num_entity += 1

        ## predict
        strict_predict_list = []
        boundaries_predict_list = []
        strict_predict_list_soft_match = []
        boundaries_predict_list_soft_match = []

        # per type
        boundaries_predict_list_dict = {}
        boundaries_predict_list_soft_match_dict = {}
        for key in e_types_list:
            boundaries_predict_list_dict[key] = []
            boundaries_predict_list_soft_match_dict[key] = []

        for ent in example["NER"]:
            ent_name = ent["e_name"].lower()
            ent_type = ent["e_type"].lower() 
            strict_predict_list.append([ent_type, ent_name])
            boundaries_predict_list.append(ent_name)

            # per type
            if ent_type not in e_types_list:
                num_undefined_type += 1
            else:
                boundaries_predict_list_dict[ent_type].append(ent_name)

            ## soft match
            ent_name = modify_to_target_by_edit_distance(ent_name, boundaries_target_list, logger, threshold=0.5)
            strict_predict_list_soft_match.append([ent_type, ent_name])
            boundaries_predict_list_soft_match.append(ent_name)

            # per type
            if ent_type in e_types_list:
                boundaries_predict_list_soft_match_dict[ent_type].append(ent_name)

        
        ## hard-match 
        strict_correct_list = get_correct_list_from_response_list(strict_target_list, strict_predict_list)
        boundaries_correct_list = get_correct_list_from_response_list(boundaries_target_list, boundaries_predict_list)
        # print(strict_correct_list, boundaries_correct_list)
        tp_ner_strict += len(strict_correct_list)
        fp_ner_strict += len(strict_predict_list) - len(strict_correct_list)
        fn_ner_strict += len(strict_target_list) - len(strict_correct_list)

        tp_ner_boundaries += len(boundaries_correct_list)
        fp_ner_boundaries += len(boundaries_predict_list) - len(boundaries_correct_list)
        fn_ner_boundaries += len(boundaries_target_list) - len(boundaries_correct_list)

        ## soft-match
        strict_correct_list_soft_match = get_correct_list_from_response_list(strict_target_list, strict_predict_list_soft_match)
        boundaries_correct_list_soft_match = get_correct_list_from_response_list(boundaries_target_list, boundaries_predict_list_soft_match)
        # print(strict_correct_list, boundaries_correct_list)
        tp_ner_strict_soft_match += len(strict_correct_list_soft_match)
        fp_ner_strict_soft_match += len(strict_predict_list_soft_match) - len(strict_correct_list_soft_match)
        fn_ner_strict_soft_match += len(strict_target_list) - len(strict_correct_list_soft_match)

        tp_ner_boundaries_soft_match += len(boundaries_correct_list_soft_match)
        fp_ner_boundaries_soft_match += len(boundaries_predict_list_soft_match) - len(boundaries_correct_list_soft_match)
        fn_ner_boundaries_soft_match += len(boundaries_target_list) - len(boundaries_correct_list_soft_match)

        ## per type
        for key in e_types_list:
            cur_correct = get_correct_list_from_response_list(boundaries_target_list_dict[key], boundaries_predict_list_dict[key])
            hard_boundaries[key]["tp"] += len(cur_correct)
            hard_boundaries[key]["fp"] += len(boundaries_predict_list_dict[key]) - len(cur_correct)
            hard_boundaries[key]["fn"] += len(boundaries_target_list_dict[key]) - len(cur_correct)

            cur_correct_soft = get_correct_list_from_response_list(boundaries_target_list_dict[key], boundaries_predict_list_soft_match_dict[key])
            soft_boundaries[key]["tp"] += len(cur_correct_soft)
            soft_boundaries[key]["fp"] += len(boundaries_predict_list_soft_match_dict[key]) - len(cur_correct_soft)
            soft_boundaries[key]["fn"] += len(boundaries_target_list_dict[key]) - len(cur_correct_soft)


       
    logger.write("#sentence: {}, #entity: {}, #undefined type: {}\n".format(len(data), num_entity, num_undefined_type))

    print_metrics(tp_ner_strict, fp_ner_strict, fn_ner_strict, logger, "NER-strict-hardMatch", align=25)
    print_metrics(tp_ner_boundaries, fp_ner_boundaries, fn_ner_boundaries, logger, "NER-boundaries-hardMatch", align=25)
    print_metrics(tp_ner_strict_soft_match, fp_ner_strict_soft_match, fn_ner_strict_soft_match, logger, "NER-strict-softMatch", align=25)
    print_metrics(tp_ner_boundaries_soft_match, fp_ner_boundaries_soft_match, fn_ner_boundaries_soft_match, logger, "NER-boundaries-softMatch", align=25)

    # per type
    align_char = max([len(key) for key in e_types_list]) + 8 
    for key in e_types_list:
        print_metrics(hard_boundaries[key]["tp"], hard_boundaries[key]["fp"], hard_boundaries[key]["fn"], logger, "\thard-" + str(key), align=align_char)
        print_metrics(soft_boundaries[key]["tp"], soft_boundaries[key]["fp"], soft_boundaries[key]["fn"], logger, "\tsoft-" + str(key), align=align_char)


if __name__ == "__main__":
    opts = get_opts()

    ## log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file)
    logger = Logger(file_name=opts.logger_file)
    # logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    report_metric(opts, logger)

