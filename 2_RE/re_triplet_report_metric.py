import json
import os
import sys
import ast
from config import get_opts_re as get_opts
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
    target_item = ent_name
    similarity_list = [SequenceMatcher(a=ent_name, b=item).ratio() for item in target_list]
    max_score = max(similarity_list)
    if max_score > threshold:
        max_index = similarity_list.index(max_score)
        target_item = target_list[max_index].lower().strip()
    return target_item


# 解析 response
def triplet_get_result_list(response):
    
    def all_type_is_str(tmp_res_list):
        flag = True
        for item in tmp_res_list:
            if type(item) != str:
                flag = False
        return flag
    
    response = response.replace("], [", "]\n[")
    lines = response.split("\n")
    result_list = []

    for line in lines:
        res_flag = True
        line = line.strip()
        # print(line)
        try:
            tmp_res_list = ast.literal_eval(line.strip())
        except:
            tmp_res_list = []
            res_flag = False

        if tmp_res_list != [] and all_type_is_str(tmp_res_list):
            if len(tmp_res_list) == 3:
                h = tmp_res_list[0]
                r = tmp_res_list[1]
                t = tmp_res_list[2]
                tmp_tri = {"h": h, "t": t, "r": r}
                if tmp_tri not in result_list:
                    result_list.append(tmp_tri)
            else:
                res_flag = False
                        
        if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
            for tmp in tmp_res_list:
                if all_type_is_str(tmp):
                    if len(tmp) == 3:
                        h = tmp[0]
                        r = tmp[1]
                        t = tmp[2]
                        tmp_tri = {"h": h, "t": t, "r": r}
                        if tmp_tri not in result_list:
                            result_list.append(tmp_tri)
                    else:
                        res_flag = False

    return result_list, res_flag


# report metric
def triplet_report_metric(opts, logger, file_name=None, dump_to_file=False):
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
        r_types_dict = types["relation"]
        r_types_list = list(r_types_dict.values())
        r_types_list = [item.lower() for item in r_types_list]
    
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
        target_ent_list = []

        uni_target_list = []  # dwie, nyt-multi 有重复
        for r_dic in example["relations"]:
            if r_dic not in uni_target_list:
                uni_target_list.append(r_dic)

        for r_dic in uni_target_list:        
            h_name = r_dic["h_name"]
            t_name = r_dic["t_name"]
            r = r_types_dict[r_dic["r"]].lower()
            tmp_tri = [h_name.lower(), t_name.lower(), r]

            if r != "no relation" and tmp_tri not in target:
                target.append(tmp_tri)
        
        for ent in example["entities"]:
            target_ent_list.append(ent["name"].lower())

        ## res_dict
        response = example["response"]
        if opts.COT:
            response = response.replace("answer is", "answer:")
            response = response.split("answer:")[-1].strip()
        rels_list, res_flag = triplet_get_result_list(example["response"])

        if len(rels_list) == 0 and example["response"].strip() != '[]':
            res_flag = False

        ## predict
        predict_strict = []
        for rel in rels_list:
            if rel['r'].lower() in r_types_list and rel['r'].lower() != "no relation":
                predict_strict.append([rel["h"].lower(), rel["t"].lower(), rel["r"].lower()])
            else:
                num_undefined_type += 1
                # res_flag = False
        
        if not res_flag:
            num_invalid += 1
            # print(example["response"].replace("\n", ", "))

        strict_correct = get_correct_list_from_response_list(target, predict_strict)
        tp_strict += len(strict_correct)
        fp_strict += len(predict_strict) - len(strict_correct)
        fn_strict += len(target) - len(strict_correct)

        ##
        for tri in predict_strict:
            tri[0] = modify_ent_name_by_similarity(tri[0], target_ent_list, threshold=0.5)
            tri[1] = modify_ent_name_by_similarity(tri[1], target_ent_list, threshold=0.5)
        
        soft_correct = get_correct_list_from_response_list(target, predict_strict)
        tp_soft += len(soft_correct)
        fp_soft += len(predict_strict) - len(soft_correct)
        fn_soft += len(target) - len(soft_correct)

       
    logger.write("#sentence: {}, #undefined relation type: {}\n".format(len(data),  num_undefined_type))
    
    if dump_to_file:
        if opts.irrelevant:
            dump_metric_file = os.path.join(opts.result_dir, opts.task, "irrelevant-triplet-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        else:
            dump_metric_file = os.path.join(opts.result_dir, opts.task, "triplet-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        fw = open(dump_metric_file, "a", encoding="utf-8")

    print(num_invalid)
    f1_strict = print_metrics(tp_strict, fp_strict, fn_strict, logger, "strict", align=6)
    if dump_to_file:
        dump_result_to_file(fw, opts, "hard", tp_strict, fp_strict, fn_strict)

    f1_soft = print_metrics(tp_soft, fp_soft, fn_soft, logger, "soft", align=6)
    if dump_to_file:
        dump_result_to_file(fw, opts, "soft", tp_soft, fp_soft, fn_soft)
    logger.write("\n")
    return f1_strict


# report metric for head/tail types
def triplet_report_metric_head_tail(opts, logger, file_name=None):
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
        r_types_dict = types["relation"]
        r_types_list = list(r_types_dict.values())
        r_types_list = [item.lower() for item in r_types_list]
    
    with open(os.path.join(opts.input_dir, opts.task, opts.dataset, "head_tail_types.json"), "r", encoding="utf-8") as fr_ht:
        th_dict = json.load(fr_ht)
        head_list = [th_dict["head"][item].lower() for item in th_dict["head"].keys()]
        tail_list = [th_dict["tail"][item].lower() for item in th_dict["tail"].keys()]

    ## statistics
    tp_all_head = 0
    fp_all_head = 0
    fn_all_head = 0
    tp_all_tail = 0
    fp_all_tail = 0
    fn_all_tail = 0

    for example in data:
        ## target
        head_target = []
        tail_target = []

        uni_target_list = []  # dwie, nyt-multi 有重复
        for r_dic in example["relations"]:
            if r_dic not in uni_target_list:
                uni_target_list.append(r_dic)

        for r_dic in uni_target_list:        
            h_name = r_dic["h_name"].lower()
            t_name = r_dic["t_name"].lower()
            r = r_types_dict[r_dic["r"]].lower()

            if r != "no relation" and r in head_list:
                head_target.append([h_name, t_name, r])

            if r != "no relation" and r in tail_list:
                tail_target.append([h_name, t_name, r])
        

        ## res_dict
        response = example["response"]
        if opts.COT:
            response = response.replace("answer is", "answer:")
            response = response.split("answer:")[-1].strip()
        rels_list, res_flag = triplet_get_result_list(example["response"])


        ## predict
        head_predict = []
        tail_predict = []

        for rel in rels_list:
            if rel['r'].lower() in head_list and rel['r'].lower() != "no relation":
                head_predict.append([rel["h"].lower(), rel["t"].lower(), rel["r"].lower()])
            if rel['r'].lower() in tail_list and rel['r'].lower() != "no relation":
                tail_predict.append([rel["h"].lower(), rel["t"].lower(), rel["r"].lower()])
        

        head_correct = get_correct_list_from_response_list(head_target, head_predict)
        tp_all_head += len(head_correct)
        fp_all_head += len(head_predict) - len(head_correct)
        fn_all_head += len(head_target) - len(head_correct)

        tail_correct = get_correct_list_from_response_list(tail_target, tail_predict)
        tp_all_tail += len(tail_correct)
        fp_all_tail += len(tail_predict) - len(tail_correct)
        fn_all_tail += len(tail_target) - len(tail_correct)

    f1_head = print_metrics(tp_all_head, fp_all_head, fn_all_head, logger, "head", align=6)
    f1_tail = print_metrics(tp_all_tail, fp_all_tail, fn_all_tail, logger, "tail", align=6)


if __name__ == "__main__":
    opts = get_opts()

    # log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file) 
    logger = Logger(file_name=opts.logger_file)

    triplet_report_metric(opts, logger, dump_to_file=True)

