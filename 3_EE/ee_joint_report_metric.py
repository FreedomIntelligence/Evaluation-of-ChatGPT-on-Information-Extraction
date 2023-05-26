import json, os
import ast
import sys
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, print_metrics, get_correct_list_from_response_list
from config import get_opts_ee as get_opts
from difflib import SequenceMatcher


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
    
    response = response.replace("]], [", "]]\n[").replace("]],[", "]]\n[").replace("]] , [", "]]\n[")
    lines = response.split("\n")
    result_trigger_list = []
    result_argument_list = []

    res_flag = True
    for line in lines:
        if line.strip() == "[]":
            continue

        line_item = [item.strip() for item in line.strip().split(":")]
        if len(line_item) != 2:
            res_flag = False
            continue
        
        ## trigger
        try:
            tmp_trigger_list = ast.literal_eval(line_item[0])
        except:
            tmp_trigger_list = []
            res_flag = False

        evt_type = ""
        if tmp_trigger_list != [] and all_type_is_str(tmp_trigger_list):
            if len(tmp_trigger_list) == 2:
                trigger_str = tmp_trigger_list[0].lower()
                evt_type = tmp_trigger_list[1].lower()
                tmp_evt = [trigger_str, evt_type]
                if tmp_evt not in result_trigger_list:
                    result_trigger_list.append(tmp_evt)
            else:
                res_flag = False
        

        ## argument
        if evt_type != "":
            argument_str = line_item[1].replace(", ...", "").replace(",...", "")
            try:
                tmp_argument_list = ast.literal_eval(argument_str)
            except:
                res_flag = False
                tmp_argument_list = []
            
            for item in tmp_argument_list:
                if type(item) == list and len(item) == 2 and all_type_is_str(item):
                    arg_role = [evt_type, item[0].lower(), item[1].lower()]
                    if arg_role not in result_argument_list:
                        result_argument_list.append(arg_role)
                else:
                    res_flag = False


    return result_trigger_list, result_argument_list, res_flag


# report metric
def joint_report_metric(opts, logger, file_name=None, dump_to_file=False):
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
        role_types = types["role_types"]
        event2roles = types["event2roles"]
        event2roles_lower = {k.lower(): [item.lower() for item in v] for k, v in event2roles.items()}
        # print(event2roles_lower)
    
    ## statistics
    num_undefined_type = 0
    trigger_tp_strict = 0
    trigger_fp_strict = 0
    trigger_fn_strict = 0
    trigger_tp_soft = 0
    trigger_fp_soft = 0
    trigger_fn_soft = 0

    num_undefined_argument = 0
    argument_tp_strict = 0
    argument_fp_strict = 0
    argument_fn_strict = 0
    argument_tp_soft = 0
    argument_fp_soft = 0
    argument_fn_soft = 0

    num_invalid =0

    for example in data:

        target_trigger = []
        target_trigger_list = []
        target_argument = []
        target_argument_list = []
        
        for event in example["event"]:
            evt_type = event_types[event["subtype"].replace(":", ".")]["verbose"]
            # roles_lower = [item.lower() for item in event2roles[evt_type]]
            trigger_str = event["trigger"]
            
            ## target
            target_trigger.append([trigger_str.lower(), evt_type.lower()])
            target_trigger_list.append(trigger_str.lower())
            
            for arg in event["arguments"]:
                argument_str = arg["text"]
                role_str = role_types[arg["role"]]["verbose"]

                target_argument.append([evt_type.lower(), argument_str.lower(), role_str.lower()])
                target_argument_list.append(argument_str.lower())


        predict_trigger_list,  predict_argument_list, res_flag = get_result_list(opts, example["response"])

        if not res_flag:
            num_invalid += 1
            # print(example["response"])

        ## predict trigger
        predict_strict_trigger = []
        for evt in predict_trigger_list:
            if evt[1].lower() in event_types_list_lower:
                predict_strict_trigger.append([evt[0].lower(), evt[1].lower()])
            else:
                num_undefined_type += 1

        strict_correct = get_correct_list_from_response_list(target_trigger, predict_strict_trigger)
        trigger_tp_strict += len(strict_correct)
        trigger_fp_strict += len(predict_strict_trigger) - len(strict_correct)
        trigger_fn_strict += len(target_trigger) - len(strict_correct)
        
        for tri in predict_strict_trigger:
            tri[0] = modify_ent_name_by_similarity(tri[0], target_trigger_list, threshold=0.5)
        
        soft_correct = get_correct_list_from_response_list(target_trigger, predict_strict_trigger)
        trigger_tp_soft += len(soft_correct)
        trigger_fp_soft += len(predict_strict_trigger) - len(soft_correct)
        trigger_fn_soft += len(target_trigger) - len(soft_correct)

        ### predict argument
        predict_strict_argument = []
        for arg in predict_argument_list:
            if arg[0].lower() in event_types_list_lower and arg[2].lower() in event2roles_lower[arg[0].lower()]:
                predict_strict_argument.append([arg[0].lower(), arg[1].lower(), arg[2].lower()])
            else:
                num_undefined_argument += 1

        strict_correct = get_correct_list_from_response_list(target_argument, predict_strict_argument)
        argument_tp_strict += len(strict_correct)
        argument_fp_strict += len(predict_strict_argument) - len(strict_correct)
        argument_fn_strict += len(target_argument) - len(strict_correct)
        
        for arg in predict_strict_argument:
            arg[1] = modify_ent_name_by_similarity(arg[1], target_argument_list, threshold=0.5)
        
        soft_correct = get_correct_list_from_response_list(target_argument, predict_strict_argument)
        argument_tp_soft += len(soft_correct)
        argument_fp_soft += len(predict_strict_argument) - len(soft_correct)
        argument_fn_soft += len(target_argument) - len(soft_correct)

       
    logger.write("#example: {}, #undefined event type: {}\n".format(len(data),  num_undefined_type))
    trigger_f1_strict = print_metrics(trigger_tp_strict, trigger_fp_strict, trigger_fn_strict, logger, "strict", align=6)
    trigger_f1_soft = print_metrics(trigger_tp_soft, trigger_fp_soft, trigger_fn_soft, logger, "soft", align=6)
    logger.write("\n")

    print(num_invalid)

    if dump_to_file:
        if opts.irrelevant:
            dump_metric_file = os.path.join(opts.result_dir, opts.task, "irrelevant-joint-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        else:
            dump_metric_file = os.path.join(opts.result_dir, opts.task, "joint-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        fw = open(dump_metric_file, "a", encoding="utf-8")

    logger.write("#example: {}, #undefined role type: {}\n".format(len(data),  num_undefined_argument))
    argument_f1_strict = print_metrics(argument_tp_strict, argument_fp_strict, argument_fn_strict, logger, "strict", align=6)
    if dump_to_file:
        dump_result_to_file(fw, opts, "hard", argument_tp_strict, argument_fp_strict, argument_fn_strict)

    argument_f1_soft = print_metrics(argument_tp_soft, argument_fp_soft, argument_fn_soft, logger, "soft", align=6)
    if dump_to_file:
        dump_result_to_file(fw, opts, "soft", argument_tp_soft, argument_fp_soft, argument_fn_soft)

    logger.write("\n")

    return argument_f1_strict


def joint_report_metric_head_tail(opts, logger, file_name=None):
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
        role_types = types["role_types"]
        event2roles = types["event2roles"]
        event2roles_lower = {k.lower(): [item.lower() for item in v] for k, v in event2roles.items()}
        # print(event2roles_lower)

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

        head_target = []
        tail_target = []
        
        for event in example["event"]:
            evt_type = event_types[event["subtype"].replace(":", ".")]["verbose"]
            # roles_lower = [item.lower() for item in event2roles[evt_type]]
            trigger_str = event["trigger"]
            
            for arg in event["arguments"]:
                argument_str = arg["text"]
                role_str = role_types[arg["role"]]["verbose"]

                if evt_type.lower() in head_list:
                    head_target.append([evt_type.lower(), argument_str.lower(), role_str.lower()])
                
                if evt_type.lower() in tail_list:
                    tail_target.append([evt_type.lower(), argument_str.lower(), role_str.lower()])


        predict_trigger_list,  predict_argument_list, res_flag = get_result_list(opts, example["response"])

        ### predict argument
        head_predict = []
        tail_predict = []
        
        for arg in predict_argument_list:
            if arg[0].lower() in event_types_list_lower and arg[2].lower() in event2roles_lower[arg[0].lower()]:
                if arg[0].lower() in head_list:
                    head_predict.append([arg[0].lower(), arg[1].lower(), arg[2].lower()])
                if arg[0].lower() in tail_list:
                    tail_predict.append([arg[0].lower(), arg[1].lower(), arg[2].lower()])
            

        head_correct = get_correct_list_from_response_list(head_target, head_predict)
        tp_head += len(head_correct)
        fp_head += len(head_predict) - len(head_correct)
        fn_head += len(head_target) - len(head_correct)

        tail_correct = get_correct_list_from_response_list(tail_target, tail_predict)
        tp_tail += len(tail_correct)
        fp_tail += len(tail_predict) - len(tail_correct)
        fn_tail += len(tail_target) - len(tail_correct)

    f1_head = print_metrics(tp_head, fp_head, fn_head, logger, "head", align=6)
    f1_tail = print_metrics(tp_tail, fp_tail, fn_tail, logger, "tail", align=6)


if __name__ == "__main__":
    opts = get_opts()

    # log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file) 
    logger = Logger(file_name=opts.logger_file)

    joint_report_metric(opts, logger, dump_to_file=True)

