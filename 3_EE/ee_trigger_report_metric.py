import json, os
import ast
import sys
from config import get_opts_ee as get_opts
from difflib import SequenceMatcher
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, print_metrics, get_correct_list_from_response_list


# dump metric to files
def dump_result_to_file(fw, opts, mode, tp, fp, fn):
    p, r, f1 = 0.0, 0.0, 0.0

    if tp + fp != 0:
        p = 1.0 * tp / (tp + fp)
    if tp + fn != 0:
        r = 1.0 * tp / (tp + fn)
    if p + r != 0.0:
        f1 = 2.0 * p * r / (p + r)

    result_dict ={
        "dataset": opts.dataset,
        "result_file": opts.result_file, 
        "mode": mode,
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
def modify_ent_name_by_similarity(ent_name, target_list, threshold=0.5):
    if len(target_list) == 0:
        return ent_name
    target_item = ent_name
    similarity_list = [SequenceMatcher(a=ent_name, b=item).ratio() for item in target_list]
    max_score = max(similarity_list)
    if max_score > threshold:
        max_index = similarity_list.index(max_score)
        target_item = target_list[max_index].lower().strip()
    return target_item


# 解析 response
def get_result_list(opts, response):
    
    def all_type_is_str(tmp_res_list):
        flag = True
        for item in tmp_res_list:
            if type(item) != str:
                flag = False
        return flag
    
    if opts.COT:
        response = response.replace("answer is", "answer:")
        response = response.split("answer:")[-1].strip()
    
    response = response.replace("], [", "]\n[")
    lines = response.split("\n")
    result_list = []

    res_flag = True

    for line in lines:
        line = line.strip()
        # print(line)
        try:
            tmp_res_list = ast.literal_eval(line.strip())
        except:
            res_flag = False
            tmp_res_list = []

        if tmp_res_list != [] and all_type_is_str(tmp_res_list):
            if len(tmp_res_list) == 2:
                e_type = tmp_res_list[1]
                e_trigger = tmp_res_list[0]
                tmp_e = [e_type, e_trigger]
                if tmp_e not in result_list:
                    result_list.append(tmp_e)
            else:
                res_flag = False
                        
        if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
            for tmp in tmp_res_list:
                if all_type_is_str(tmp):
                    if len(tmp) == 2:
                        e_type = tmp[1]
                        e_trigger = tmp[0]
                        tmp_e = [e_type, e_trigger]
                        if tmp_e not in result_list:
                            result_list.append(tmp_e)
                    else:
                        res_flag = False

    return result_list, res_flag


# report metric
def trigger_report_metric(opts, logger, file_name=None, dump_to_file=False):
    if file_name is not None:
        file_name = os.path.join(opts.result_dir, opts.task, opts.dataset, file_name)
    else:
        file_name = opts.result_file

    ## load data
    logger.write("Load file: {}\n".format(file_name))
    logger.write("Load types file: {}\n".format(opts.type_file))

    with open(file_name, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        event_types = types["event_types"]
        event_types_list = [event_types[key]["verbose"] for key in event_types]
        event_types_list_lower = [item.lower() for item in event_types_list]
    
    ## statistics
    num_undefined_type = 0
    tp_strict = 0
    fp_strict = 0
    fn_strict = 0
    tp_soft = 0
    fp_soft = 0
    fn_soft = 0

    num_invalid = 0

    for example in data:
        ## target
        target = []
        target_trigger_list = []
        for mention in example["event"]:
            e_type = mention["subtype"].replace(":", ".")
            e_trigger = mention["trigger"]
            target.append([event_types[e_type]["verbose"].lower(), e_trigger.lower()])
            target_trigger_list.append(e_trigger.lower())

        trigger_list, res_flag = get_result_list(opts, example["response"])

        if not res_flag:
            num_invalid += 1
            # print(example["response"].replace("\n", ", "))

        ## predict
        predict_strict = []
        for eve in trigger_list:
            if eve[0].lower() in event_types_list_lower:
                predict_strict.append([eve[0].lower(), eve[1].lower()])
            else:
                num_undefined_type += 1

        # print(target, predict_strict)

        strict_correct = get_correct_list_from_response_list(target, predict_strict)
        tp_strict += len(strict_correct)
        fp_strict += len(predict_strict) - len(strict_correct)
        fn_strict += len(target) - len(strict_correct)
        # print("strict", strict_correct)
        ##
        for tri in predict_strict:
            tri[1] = modify_ent_name_by_similarity(tri[1], target_trigger_list, threshold=0.5)
        
        soft_correct = get_correct_list_from_response_list(target, predict_strict)
        tp_soft += len(soft_correct)
        fp_soft += len(predict_strict) - len(soft_correct)
        fn_soft += len(target) - len(soft_correct)
        # print("soft", soft_correct)

       
    logger.write("#example: {}, #undefined event type: {}\n".format(len(data),  num_undefined_type))
    # print(num_invalid)

    if dump_to_file:
        dump_metric_file = os.path.join(opts.result_dir, opts.task, "trigger-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        fw = open(dump_metric_file, "a", encoding="utf-8")

    f1_strict = print_metrics(tp_strict, fp_strict, fn_strict, logger, "strict", align=6)
    if dump_to_file:
        dump_result_to_file(fw, opts, "hard", tp_strict, fp_strict, fn_strict)

    f1_soft = print_metrics(tp_soft, fp_soft, fn_soft, logger, "soft", align=6)
    if dump_to_file:
        dump_result_to_file(fw, opts, "soft", tp_soft, tp_soft, tp_soft)
    logger.write("\n")
    return f1_strict


# report metric for head/tail types
def trigger_report_metric_head_tail(opts, logger, file_name=None):
    if file_name is not None:
        file_name = os.path.join(opts.result_dir, opts.task, opts.dataset, file_name)
    else:
        file_name = opts.result_file

    ## load data
    logger.write("Load file: {}\n".format(file_name))
    logger.write("Load types file: {}\n".format(opts.type_file))

    with open(file_name, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        event_types = types["event_types"]
        event_types_list = [event_types[key]["verbose"] for key in event_types]
        event_types_list_lower = [item.lower() for item in event_types_list]

    with open(os.path.join(opts.input_dir, opts.task, opts.dataset, "head_tail_types.json"), "r", encoding="utf-8") as fr_ht:
        th_dict = json.load(fr_ht)
        head_list = [th_dict["head"][item]["verbose"].lower() for item in th_dict["head"].keys()]
        tail_list = [th_dict["tail"][item]["verbose"].lower() for item in th_dict["tail"].keys()]
    
    ## statistics
    tp_head = 0
    fp_head = 0
    fn_head = 0
    tp_tail = 0
    fp_tail = 0
    fn_tail = 0

    for example in data:
        ## target
        head_target = []
        tail_target = []
        for mention in example["event"]:
            e_type = mention["subtype"].replace(":", ".")
            e_type = event_types[e_type]["verbose"].lower()
            e_trigger = mention["trigger"].lower()
            if e_type in head_list:
                head_target.append([e_type, e_trigger])
            if e_type in tail_list:
                tail_target.append([e_type, e_trigger])

        trigger_list, res_flag = get_result_list(opts, example["response"])


        ## predict
        head_predict = []
        tail_predict = []
        for eve in trigger_list:
            if eve[0].lower() in head_list:
                head_predict.append([eve[0].lower(), eve[1].lower()])
            if eve[0].lower() in tail_list:
                tail_predict.append([eve[0].lower(), eve[1].lower()])


        head_correct = get_correct_list_from_response_list(head_target, head_predict)
        tp_head += len(head_correct)
        fp_head += len(head_predict) - len(head_correct)
        fn_head += len(head_target) - len(head_correct)

        tail_correct = get_correct_list_from_response_list(tail_target, tail_predict)
        tp_tail += len(tail_correct)
        fp_tail += len(tail_predict) - len(tail_correct)
        fn_tail += len(tail_target) - len(tail_correct)
        
    f1_head = print_metrics(tp_head, fp_head, fn_head, logger, "head", align=6)
    f1_tail = print_metrics(tp_tail, fp_tail, fn_tail, logger, "soft", align=6)


if __name__ == "__main__":
    opts = get_opts()

    # log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file) 
    logger = Logger(file_name=opts.logger_file)
    # logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    trigger_report_metric(opts, logger, dump_to_file=True)

