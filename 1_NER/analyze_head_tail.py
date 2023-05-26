import os
import json
import sys
from config import get_opts_ner
from ner_report_metric import report_metric_head_tail
cur_path = os.path.abspath("..")
sys.path.append(cur_path)
from utils import Logger


def ner_get_head_tail_type(opts):

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
        ent_type_dict = types["entities"]
        
        ## 统计 train file
        for example in data:  
            for ent in example["entities"]:
                e_type = ent["e_type"]

                if "num" not in ent_type_dict[e_type]:
                    ent_type_dict[e_type]["num"] = 1
                else:
                    ent_type_dict[e_type]["num"] += 1

        tail_dict = {}
        head_dict = {}
        for k, v in ent_type_dict.items():
            # print(k, v["verbose"], v["num"])
            if v["num"] >= opts.threshold_head_tail:
                head_dict[k] = v
            else:
                tail_dict[k] = v

        print(len(head_dict), len(tail_dict))

        res_dict = {
            "head": head_dict,
            "tail": tail_dict
        }

        with open(out_file_name, 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(res_dict, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    
    opts = get_opts_ner()
    # ner_get_head_tail_type(opts)

    opts.logger_file = os.path.join(opts.task, "head-tail-report-metric-" + opts.logger_file)
    logger = Logger(file_name=opts.logger_file)

    report_metric_head_tail(opts, logger)