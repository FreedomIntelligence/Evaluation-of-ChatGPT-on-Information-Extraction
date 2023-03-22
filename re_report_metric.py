import json, os
from difflib import SequenceMatcher
from utils import Logger, print_metrics, get_correct_list_from_response_list
from config import get_opts_re as get_opts


def report_metric(opts, logger):

    ## load data
    logger.write("Load file: {}\n".format(opts.result_file))
    logger.write("Load types file: {}\n".format(opts.type_file))

    with open(opts.result_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        r_types_dict = types["relation"]
        r_types = list(r_types_dict.values())
    
    ## statistics
    num_undefined_type = 0
    
    tp_all_noorder = 0
    fp_all_noorder = 0
    fn_all_noorder = 0
    tp_all_order = 0
    fp_all_order = 0
    fn_all_order = 0

    tp_part_noorder = 0
    fp_part_noorder = 0
    fn_part_noorder = 0
    tp_part_order = 0
    fp_part_order = 0
    fn_part_order = 0

    
    for example in data:
        ## target
        order_target = []
        no_order_target = []

        ## part entity
        part_entities = []
        for r_dic in example["relations"]:
            h = r_dic["h"]
            h_name = r_dic["h_name"]
            t = r_dic["t"]
            t_name = r_dic["t_name"]

            if [h_name, h] not in part_entities:
                part_entities.append([h_name, h])
            if [t_name, t] not in part_entities:
                part_entities.append([t_name, t])

            r = r_dic["r"]
            if h < t:
                no_order_target.append([h_name.lower(), t_name.lower(), r_types_dict[r].lower()])
            else:
                no_order_target.append([t_name.lower(), h_name.lower(), r_types_dict[r].lower()])
            order_target.append([h_name.lower(), t_name.lower(), r_types_dict[r].lower()])
        
        rels_dict = example["RE"]
        part_entities = sorted(part_entities, key=lambda a: a[1])
        # print(part_entities)
        part_entities = [item[0] for item in part_entities]

        ## all_order_predict
        all_order_predict = []
        ent_list = example["entities"]
        unique_ent_list = []
        unique_ent_list_lower = []
        for ent in ent_list:
            if ent["name"].lower() not in unique_ent_list_lower:
                unique_ent_list.append(ent["name"])
                unique_ent_list_lower.append(ent["name"].lower())
        # print(unique_ent_list) 
        for subj in unique_ent_list:
            for obj in unique_ent_list:
                if subj != obj:
                    s_name = subj
                    o_name = obj
                    if s_name == o_name:
                        continue
                    so_key = s_name + " # " + o_name
                    if so_key not in rels_dict:
                        continue
                    s_o_dict = rels_dict[so_key]
                    s_o_r = s_o_dict["r"]
                    if s_o_r in r_types and s_o_r.lower() != "no relation":
                        all_order_predict.append([s_o_dict["h"].lower(), s_o_dict["t"].lower(), s_o_dict["r"].lower()])
        
        # part_order_predict
        part_order_predict = []
        for subj in part_entities:
            for obj in part_entities:
                if subj != obj:
                    so_key = subj + " # " + obj
                    if so_key not in rels_dict:
                        continue
                    s_o_dict = rels_dict[so_key]
                    s_o_r = s_o_dict["r"]
                    if s_o_r in r_types and s_o_r.lower() != "no relation":
                        part_order_predict.append([s_o_dict["h"].lower(), s_o_dict["t"].lower(), s_o_dict["r"].lower()])
                    if s_o_r not in r_types:
                        num_undefined_type += 1
        

        ## all_no_order_predict
        all_no_order_predict = []
        ent_list = unique_ent_list
        for i in range(len(ent_list)):
            for j in range(i+1, len(ent_list)):
                s_name = ent_list[i]
                o_name = ent_list[j]
                if s_name == o_name:
                    continue
                so_key = s_name + " # " + o_name
                if so_key not in rels_dict:
                    continue
                s_o_dict = rels_dict[so_key]
                s_o_r = s_o_dict["r"]
                if s_o_r in r_types and s_o_r.lower() != "no relation":
                    all_no_order_predict.append([s_o_dict["h"].lower(), s_o_dict["t"].lower(), s_o_dict["r"].lower()])
        
        # part_no_order_predict
        part_no_order_predict = []
        for i in range(len(part_entities)):
            for j in range(i+1, len(part_entities)):
                subj = part_entities[i]
                obj = part_entities[j]
                so_key = subj + " # " + obj
                if so_key not in rels_dict:
                    continue
                s_o_dict = rels_dict[so_key]
                s_o_r = s_o_dict["r"]
                if s_o_r in r_types and s_o_r.lower() != "no relation":
                    part_no_order_predict.append([s_o_dict["h"].lower(), s_o_dict["t"].lower(), s_o_dict["r"].lower()])

        all_order_correct = get_correct_list_from_response_list(order_target, all_order_predict)
        tp_all_order += len(all_order_correct)
        fp_all_order += len(all_order_predict) - len(all_order_correct)
        fn_all_order += len(order_target) - len(all_order_correct)

        
        all_no_order_correct = get_correct_list_from_response_list(no_order_target, all_no_order_predict)
        tp_all_noorder += len(all_no_order_correct)
        fp_all_noorder += len(all_no_order_predict) - len(all_no_order_correct)
        fn_all_noorder += len(no_order_target) - len(all_no_order_correct)

        part_order_correct = get_correct_list_from_response_list(order_target, part_order_predict)
        tp_part_order += len(part_order_correct)
        fp_part_order += len(part_order_predict) - len(part_order_correct)
        fn_part_order += len(order_target) - len(part_order_correct)

        part_no_order_correct = get_correct_list_from_response_list(no_order_target, part_no_order_predict)
        tp_part_noorder += len(part_no_order_correct)
        fp_part_noorder += len(part_no_order_predict) - len(part_no_order_correct)
        fn_part_noorder += len(no_order_target) - len(part_no_order_correct)
        # print(order_target)
        # print(all_order_predict)
        # print(part_order_predict)
        # print(no_order_target)
        # print(all_no_order_predict)
        # print(part_no_order_predict)

       
    logger.write("#sentence: {}, #undefined relation type: {}\n".format(len(data),  num_undefined_type))

    print_metrics(tp_all_order, fp_all_order, fn_all_order, logger, "all-order", align=14)
    print_metrics(tp_all_noorder, fp_all_noorder, fn_all_noorder, logger, "all-no-order", align=14)
    print_metrics(tp_part_order, fp_part_order, fn_part_order, logger, "part-order", align=14)
    print_metrics(tp_part_noorder, fp_part_noorder, fn_part_noorder, logger, "part-no-order", align=14)


if __name__ == "__main__":
    opts = get_opts()

    ## log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file) 
    logger = Logger(file_name=opts.logger_file)
    # logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    report_metric(opts, logger)

