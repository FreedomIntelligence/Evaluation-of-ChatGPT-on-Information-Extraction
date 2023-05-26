import json
import os
import sys
import ast
from config import get_opts_re as get_opts
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, print_metrics, get_correct_list_from_response_list, response_string_to_list


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


# document level datasets: report metric
def doc_report_metric(opts, logger, file_name=None):
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
        e_types_dict = types["entity"]
        r_types_dict = types["relation"]
        r_types = list(r_types_dict.values())
        r_types_lower = [item.lower() for item in r_types]
    
    ## statistics
    num_undefined_type = 0
    tp_all_order = 0
    fp_all_order = 0
    fn_all_order = 0
    tp_part_order = 0
    fp_part_order = 0
    fn_part_order = 0
    
    for example in data:
        ## target
        order_target = []

        ## part entity
        part_entities = []
        for r_dic in example["relations"]:
            h = r_dic["h"]
            h_name = r_dic["h_name"]
            t = r_dic["t"]
            t_name = r_dic["t_name"]
            r = r_dic["r"]
            order_target.append([h_name.lower(), t_name.lower(), r_types_dict[r].lower()])

            if [h_name, h] not in part_entities:
                part_entities.append([h_name, h])
            if [t_name, t] not in part_entities:
                part_entities.append([t_name, t])

        part_entities = sorted(part_entities, key=lambda a: a[1])
        part_entities = [item[0] for item in part_entities]
        # 去重
        uni_part_entities = []
        uni_part_entities_lower = []
        for item in part_entities:
            if item.lower() not in uni_part_entities_lower:
                uni_part_entities_lower.append(item.lower())
                uni_part_entities.append(item)
        part_entities = uni_part_entities

        ## all entity
        unique_ent_list = []
        unique_ent_list_lower = []
        for ent in example["entities"]:
            if ent["name"].lower() not in unique_ent_list_lower:
                unique_ent_list.append(ent["name"])
                unique_ent_list_lower.append(ent["name"].lower()) 

        ## res_dict
        # rels_dict = example["RE"]
        # if len(rels_dict) == 0:
        rels_dict = rc_get_result_dict(opts, example, r_types_lower, e_types_dict)

        ## all_order_predict
        all_order_predict = []

        for subj in unique_ent_list:
            for obj in unique_ent_list:
                if subj != obj:
                    so_key = subj.lower() + " # " + obj.lower()
                    if so_key not in rels_dict:
                        continue
                    triple_list = rels_dict[so_key]
                    for triple in triple_list:
                        s_o_r = triple["r"]
                        if s_o_r in r_types_lower and s_o_r.lower() != "no relation":
                            all_order_predict.append([triple["h"].lower(), triple["t"].lower(), triple["r"].lower()])
                        if s_o_r not in r_types_lower:
                            num_undefined_type += 1
        
        # part_order_predict
        part_order_predict = []
        for subj in part_entities:
            for obj in part_entities:
                if subj != obj:
                    so_key = subj.lower() + " # " + obj.lower()
                    if so_key not in rels_dict:
                        continue
                    triple_list = rels_dict[so_key]
                    for triple in triple_list:
                        s_o_r = triple["r"]
                        if s_o_r in r_types_lower and s_o_r.lower() != "no relation":
                            part_order_predict.append([triple["h"].lower(), triple["t"].lower(), triple["r"].lower()])
                    

        all_order_correct = get_correct_list_from_response_list(order_target, all_order_predict)
        tp_all_order += len(all_order_correct)
        fp_all_order += len(all_order_predict) - len(all_order_correct)
        fn_all_order += len(order_target) - len(all_order_correct)

        part_order_correct = get_correct_list_from_response_list(order_target, part_order_predict)
        tp_part_order += len(part_order_correct)
        fp_part_order += len(part_order_predict) - len(part_order_correct)
        fn_part_order += len(order_target) - len(part_order_correct)
       
    logger.write("#sentence: {}, #undefined relation type: {}\n".format(len(data),  num_undefined_type))
    
    all_f1 = print_metrics(tp_all_order, fp_all_order, fn_all_order, logger, "all", align=5)   
    _ = print_metrics(tp_part_order, fp_part_order, fn_part_order, logger, "part", align=5)
    logger.write("\n")
    return all_f1


def get_entity_pairs(example):
    entity_pairs = []
    ent_list = []
    ent_list_lower = []
    for ent in example["entities"]:
        ent_name = ent["name"]
        if ent_name.lower() not in ent_list_lower:
            ent_list_lower.append(ent_name.lower())
            ent_list.append(ent_name)

    for subj in ent_list:
        for obj in ent_list:
            if subj != obj:
                entity_pairs.append([subj.lower(), obj.lower()])
    return entity_pairs


# 解析 response
def rc_get_result_dict(opts, example, r_types_lower, e_types_dict):
    entity_pairs = get_entity_pairs(example)
    # print(entity_pairs)
    response = example["response"]
    if opts.COT:
        response = response.replace("answer is", "answer:")
        response = response.split("answer:")[-1].strip()
    lines = response.split("\n")
    result_dict = {}

    res_flag = True

    for line in lines:
        
        line = line.strip()
        if line  == "":
            continue
        if "):" not in line:
            res_flag = False
            continue
        item_list = line.split("):")
        if len(item_list) != 2:
            res_flag = False
            continue
        es = item_list[0].strip().strip("(").strip(")").split(",")

        if len(es) not in [4, 2]:
            res_flag = False
            continue

        es = [e.strip().strip('"') for e in es]

        if len(e_types_dict) == 0:
            if [es[0].lower(), es[1].lower()] not in entity_pairs:
                res_flag = False
                continue

            ht_key = es[0].lower() + " # " + es[1].lower()
            if ht_key not in result_dict:
                result_dict[ht_key] = []

            rel_str = item_list[1].strip()

            if "[" not in rel_str and "]" not in rel_str:
                rel_str = rel_str.strip('"').strip().lower()
                if rel_str in r_types_lower:
                    tmp_tri = {
                        "h": es[0].lower(),
                        "t": es[1].lower(),
                        "r": rel_str.lower()
                    }
                    if tmp_tri not in result_dict[ht_key]:
                        result_dict[ht_key].append(tmp_tri)
            else:
                num_left = rel_str.count("[")
                num_right = rel_str.count("]")
                
                if num_left == 1 and num_right == 1:
                    start_idx = rel_str.find('[')
                    end_idx = rel_str.find(']')
                    rel_str = rel_str[start_idx: end_idx+1] 
                else:
                    res_flag = False

                rel_str = rel_str.replace(", ...", "")

                try:
                    rel_list = ast.literal_eval(rel_str.strip())
                except:
                    rel_list = []
                    res_flag = False

                for rel in rel_list: 
                    if rel.lower() in r_types_lower:
                        tmp_tri = {
                            "h": es[0].lower(),
                            "t": es[1].lower(),
                            "r": rel.lower()
                        }
                        if tmp_tri not in result_dict[ht_key]:
                            result_dict[ht_key].append(tmp_tri)

        if len(e_types_dict) != 0:
            if [es[0].lower(), es[2].lower()] not in entity_pairs:
                res_flag = False
                continue

            ht_key = es[0].lower() + " # " + es[2].lower()
            if ht_key not in result_dict:
                result_dict[ht_key] = []

            rel_str = item_list[1].strip()

            if "[" not in rel_str and "]" not in rel_str:
                rel_str = rel_str.strip('"').strip().lower()
                if rel_str in r_types_lower:
                    tmp_tri = {
                        "h": es[0].lower(),
                        "t": es[2].lower(),
                        "r": rel_str.lower()
                    }
                    if tmp_tri not in result_dict[ht_key]:
                        result_dict[ht_key].append(tmp_tri)
            else:
                num_left = rel_str.count("[")
                num_right = rel_str.count("]")
                
                if num_left == 1 and num_right == 1:
                    start_idx = rel_str.find('[')
                    end_idx = rel_str.find(']')
                    rel_str = rel_str[start_idx: end_idx+1] 
                else:
                    res_flag = False

                rel_str = rel_str.replace(", ...", "")

                try:
                    rel_list = ast.literal_eval(rel_str.strip())
                except:
                    rel_list = []
                    res_flag = False

                for rel in rel_list: 
                    if rel.lower() in r_types_lower:
                        tmp_tri = {
                            "h": es[0].lower(),
                            "t": es[2].lower(),
                            "r": rel.lower()
                        }
                        if tmp_tri not in result_dict[ht_key]:
                            result_dict[ht_key].append(tmp_tri)
    
    return result_dict, res_flag


# repoty metric
def re_rc_report_metric(opts, logger, file_name=None, dump_to_file=False):
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
        e_types_dict = types["entity"]
        r_types_dict = types["relation"]
        r_types = list(r_types_dict.values())
        r_types_lower = [item.lower() for item in r_types]
    
    ## statistics
    num_undefined_type = 0
    tp_all_noorder = 0
    fp_all_noorder = 0
    fn_all_noorder = 0
    tp_all_order = 0
    fp_all_order = 0
    fn_all_order = 0

    num_invalid = 0
    num_entities = 0
    num_entity_unchanged = 0
    num_entity_changed = 0

    for example in data[:]:
        ## target
        order_target = []
        no_order_target = []

        uni_target_list = []  # dwie, nyt-multi 有重复
        for r_dic in example["relations"]:
            if r_dic not in uni_target_list:
                uni_target_list.append(r_dic)

        for r_dic in uni_target_list:
            h_name = r_dic["h_name"].lower()
            t_name = r_dic["t_name"].lower()
            r = r_types_dict[r_dic["r"]].lower()
            if r != "no relation" and [h_name, t_name, r] not in no_order_target:
                order_target.append([h_name, t_name, r])
                order_target.append([t_name, h_name, "no relation"])
                no_order_target.append([h_name, t_name, r])
                num_entities += 1

        ## res_dict
        rels_dict, res_flag = rc_get_result_dict(opts, example, r_types_lower, e_types_dict)
        if len(rels_dict) == 0 and example["response"].strip() != '[]':
            res_flag = False

        ## all_order_predict
        all_order_predict = []
        for r_dic in example["relations"]:
            h_name = r_dic["h_name"]
            t_name = r_dic["t_name"]
            
            so_key = h_name.lower() + " # " + t_name.lower()
            if so_key not in rels_dict:
                continue
            triple_list = rels_dict[so_key]

            s_o_r_set = set()
            for triple in triple_list:
                s_o_r = triple["r"]
                if s_o_r in r_types_lower and s_o_r.lower() != "no relation":
                    s_o_r_set.add(s_o_r)
            
            o_s_r_set = set()
            so_key_reverse = t_name.lower() + " # " + h_name.lower()
            if so_key_reverse not in rels_dict:
                continue
            triple_list = rels_dict[so_key_reverse]
            for triple in triple_list:
                s_o_r = triple["r"]
                if s_o_r in r_types_lower and s_o_r.lower() != "no relation":
                    o_s_r_set.add(s_o_r)

            if s_o_r_set == o_s_r_set:# or len(o_s_r_set) != 0:
                num_entity_unchanged += 1
                
            if len(o_s_r_set) == 0:
                num_entity_changed += 1

        
        ## all_no_order_predict
        all_no_order_predict = []
        for r_dic in example["relations"]:
            h_name = r_dic["h_name"]
            t_name = r_dic["t_name"]
            so_key = h_name.lower() + " # " + t_name.lower()
            if so_key not in rels_dict:
                res_flag = False
                # print("unknown")
                continue
            triple_list = rels_dict[so_key]
            for triple in triple_list:
                s_o_r = triple["r"]
                if s_o_r in r_types_lower and s_o_r.lower() != "no relation":
                    all_no_order_predict.append([triple["h"].lower(), triple["t"].lower(), triple["r"].lower()])
                if s_o_r not in r_types_lower:
                    num_undefined_type += 1

        if not res_flag:
            num_invalid += 1
            # print(example["response"])

        # print(no_order_target, all_order_predict)
        all_order_correct = get_correct_list_from_response_list(no_order_target, all_order_predict)
        tp_all_order += len(all_order_correct)
        fp_all_order += len(all_order_predict) - len(all_order_correct)
        fn_all_order += len(no_order_target) - len(all_order_correct)

        all_no_order_correct = get_correct_list_from_response_list(no_order_target, all_no_order_predict)
        tp_all_noorder += len(all_no_order_correct)
        fp_all_noorder += len(all_no_order_predict) - len(all_no_order_correct)
        fn_all_noorder += len(no_order_target) - len(all_no_order_correct)
       
    logger.write("#sentence: {}, #undefined relation type: {}\n".format(len(data),  num_undefined_type))

    print(num_invalid)
    print(num_entities, num_entity_changed, num_entities-num_entity_changed)

    if dump_to_file:
        if opts.irrelevant:
            dump_metric_file = os.path.join(opts.result_dir, opts.task, "irrelevant-re-rc-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        else:
            dump_metric_file = os.path.join(opts.result_dir, opts.task, "re-rc-metric-" + "-".join(opts.dataset.split("/")) + ".json")
        fw = open(dump_metric_file, "a", encoding="utf-8")

    # f1_order = print_metrics(tp_all_order, fp_all_order, fn_all_order, logger, "order", align=8)

    f1_no_order = print_metrics(tp_all_noorder, fp_all_noorder, fn_all_noorder, logger, "no-order", align=8)
    logger.write("\n")
    if dump_to_file:
        dump_result_to_file(fw, opts, "no_order", tp_all_noorder, fp_all_noorder, fn_all_noorder)
    return f1_no_order


# report metric for head/type types
def re_rc_report_metric_head_tail(opts, logger, file_name=None):
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
        e_types_dict = types["entity"]
        r_types_dict = types["relation"]
        r_types = list(r_types_dict.values())
        r_types_lower = [item.lower() for item in r_types]

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

    for example in data[:]:
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

        rels_dict, res_flag = rc_get_result_dict(opts, example, r_types_lower, e_types_dict)

        head_predict = []
        tail_predict = []
        
        for r_dic in example["relations"]:
            h_name = r_dic["h_name"]
            t_name = r_dic["t_name"]
            so_key = h_name.lower() + " # " + t_name.lower()
            if so_key not in rels_dict:
                continue
            triple_list = rels_dict[so_key]
            for triple in triple_list:
                s_o_r = triple["r"]
                if s_o_r in head_list and s_o_r.lower() != "no relation":
                    head_predict.append([triple["h"].lower(), triple["t"].lower(), triple["r"].lower()])
                if s_o_r in tail_list and s_o_r.lower() != "no relation":
                    tail_predict.append([triple["h"].lower(), triple["t"].lower(), triple["r"].lower()])      

        head_correct = get_correct_list_from_response_list(head_target, head_predict)
        tp_all_head += len(head_correct)
        fp_all_head += len(head_predict) - len(head_correct)
        fn_all_head += len(head_target) - len(head_correct)

        tail_correct = get_correct_list_from_response_list(tail_target, tail_predict)
        tp_all_tail += len(tail_correct)
        fp_all_tail += len(tail_predict) - len(tail_correct)
        fn_all_tail += len(tail_target) - len(tail_correct)

    f1_head = print_metrics(tp_all_head, fp_all_head, fn_all_head, logger, "head", align=8)
    f1_head = print_metrics(tp_all_tail, fp_all_tail, fn_all_tail, logger, "tail", align=8)
    


if __name__ == "__main__":
    opts = get_opts()

    # log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file) 
    logger = Logger(file_name=opts.logger_file)

    re_rc_report_metric(opts, logger, dump_to_file=True)
