import os
import json
import sys
import ast
from config import get_opts_ner as get_opts
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, print_metrics, get_correct_list_from_response_list


## 解析 response
def response_string_to_list(response):
    """return 
        1) string 列表
        2) list  列表
    """
    def get_list_by_string(list_str):
        try:
            res_list = ast.literal_eval(list_str) 
        except:
            res_list = []
        finally:
            return res_list
    
    # response = response.lower()
    response = response.replace("(", "[").replace(")", "]")
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
            res_list = [str(res).strip() for res in res_list] 
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
            tmp_list = [str(res).strip() for res in tmp_list] 
            res_list.append(tmp_list)
            start_idx = -1
            end_idx = -1

    return res_list


def get_result_list(response):
    result_list = []
    lines = response.split("\n")
    num_error_lines = 0
    for line in lines:
        flag = True
        tmp_res_list = response_string_to_list(line.strip())
        if tmp_res_list == [] and line.strip() != '[]':
            flag = False

        if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
            if len(tmp_res_list) == 1:
                flag = False
            if len(tmp_res_list) == 2:
                entity = dict()
                entity["e_name"] = tmp_res_list[1].strip()
                entity["e_type"] = tmp_res_list[0].strip()
                result_list.append(entity)
            if len(tmp_res_list) > 2:  # [LOC, a, b, ...]
                cur_e_type = tmp_res_list[0]
                for i_idx in range(1, len(tmp_res_list)):
                    entity = dict()
                    entity["e_name"] = tmp_res_list[i_idx].strip()
                    entity["e_type"] = cur_e_type
                    result_list.append(entity)

        if tmp_res_list != [] and type(tmp_res_list[0]) == list:  # [, ], [, ]
            for tmp in tmp_res_list:
                if len(tmp) < 2:
                    flag = False
                if len(tmp) == 2:
                    entity = dict()
                    entity["e_name"] = tmp[1].strip()
                    entity["e_type"] = tmp[0].strip()
                    result_list.append(entity)
                if len(tmp) > 2:  # [LOC, a, b, ...]
                    cur_e_type = tmp[0]
                    for i_idx in range(1, len(tmp)):
                        entity = dict()
                        entity["e_name"] = tmp[i_idx].strip()
                        entity["e_type"] = cur_e_type
                        result_list.append(entity)
        if not flag:
            num_error_lines += 1

    return result_list, num_error_lines


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

    
    ## statistics
    num_entity = 0
    num_invalid = 0

    tp_ner_strict = 0
    fp_ner_strict = 0
    fn_ner_strict = 0

    num_missing_spans = 0
    num_unmentioned_spans = 0
    num_unannotated_spans = 0
    num_incorrect_span_offsets = 0
    num_undefined_types = 0
    num_incorrect_types = 0
    num_other = 0
    
    
    for example in data:
        ## target
        strict_target_list = []
        ent_name_list = []
        ent_name_2_type = {}
        for ent in example["entities"]:
            ent_name = ent["e_name"].lower()
            if opts.verbose_type:
                ent_type = e_types[ent["e_type"]]["verbose"].lower()  # 全写 
            else:
                ent_type = ent["e_type"].lower()  # 缩写

            ent_name_list.append(ent_name)
            ent_name_2_type[ent_name] = ent_type

            strict_target_list.append([ent_type, ent_name])
            num_entity += 1

        
        response = example["response"]
        example["NER"], num_error_lines = get_result_list(response)
        num_other += num_error_lines
        res_flag = True
    
        if response.strip().strip('"').strip() != '[]' and example["NER"] == []:
            res_flag = False

        ## predict
        strict_predict_list = []

        for ent in example["NER"]:
            ent_name = ent["e_name"].lower()
            ent_type = ent["e_type"].lower() 
            strict_predict_list.append([ent_type, ent_name])
            if ent_type not in e_types_list:
                num_undefined_types += 1

            if ent_name not in example["seq"].lower():
                num_unmentioned_spans += 1
            
            else:

                flag = False
                for tar_ent in ent_name_list:
                    if tar_ent == ent_name:
                        flag = True
                        ent_name_list.remove(tar_ent)
                        if ent_type != ent_name_2_type[tar_ent]:
                            num_incorrect_types += 1

                    elif tar_ent in ent_name or ent_name in tar_ent:
                        num_incorrect_span_offsets += 1
                        ent_name_list.remove(tar_ent)
                        flag = True


                if not flag:
                    num_unannotated_spans += 1
            
        if len(ent_name_list) > 0:
            num_missing_spans += 1

        if not res_flag:
            num_invalid += 1
        
        ## hard-match 
        strict_correct_list = get_correct_list_from_response_list(strict_target_list, strict_predict_list)
        tp_ner_strict += len(strict_correct_list)
        fp_ner_strict += len(strict_predict_list) - len(strict_correct_list)
        fn_ner_strict += len(strict_target_list) - len(strict_correct_list)


    print(num_invalid) 
    logger.write("#sentence: {}, #entity: {}\n".format(len(data), num_entity))
    print(num_missing_spans, num_unmentioned_spans, num_unannotated_spans, num_incorrect_span_offsets, num_undefined_types, num_incorrect_types, num_other)

    print_metrics(tp_ner_strict, fp_ner_strict, fn_ner_strict, logger, "NER-strict-hardMatch", align=25)


if __name__ == "__main__":
    opts = get_opts()

    ## log file
    opts.logger_file = os.path.join(opts.task, "report-metric-" + opts.logger_file)
    logger = Logger(file_name=opts.logger_file)
    # logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    report_metric(opts, logger)
    

