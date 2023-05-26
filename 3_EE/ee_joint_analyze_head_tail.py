import os
import json
import sys
from config import get_opts_ee
from ee_joint_report_metric import joint_report_metric_head_tail
cur_path = os.path.abspath("..")
sys.path.append(cur_path)
from utils import Logger


def ee_get_head_tail_type(opts):

    output_path = os.path.join(opts.input_dir, opts.task, opts.dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, opts.train_file)
    out_file_name = os.path.join(output_path, "head_tail_types.json")
    
    type_file_name = os.path.join(output_path, opts.type_file)
    
    print("Load file: {}".format(in_file_name))
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        rel_type_dict = types["event_types"]
        
        ## 统计 train file
        type2num = {}
        for example in data:  
            for event in example["event"]:
                rel_type = event["subtype"]
                if rel_type not in type2num:
                    type2num[rel_type] = 1
                else:
                    type2num[rel_type] += 1


        tail_dict = {}
        head_dict = {}
        for k, v in type2num.items():
            print(k, v)
            rel_type_dict[k]["num"] = v
            if v >= opts.threshold_head_tail:
                head_dict[k] = rel_type_dict[k]
            else:
                tail_dict[k] = rel_type_dict[k]

        print(len(head_dict), len(tail_dict))

        res_dict = {
            "head": head_dict,
            "tail": tail_dict
        }

        with open(out_file_name, 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(res_dict, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    
    opts = get_opts_ee()
    # ee_get_head_tail_type(opts)

    opts.logger_file = os.path.join(opts.task, "head-tail-report-metric-" + opts.logger_file)
    logger = Logger(file_name=opts.logger_file)

    joint_report_metric_head_tail(opts, logger)