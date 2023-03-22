import json, os
import random
import time
import ast
import openai
from utils import Logger, bot_run
from config import get_opts_re as get_opts


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
            res_list = [res.strip() for res in res_list] 
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
            tmp_list = [res.strip() for res in tmp_list] 
            res_list.append(tmp_list)
            start_idx = -1
            end_idx = -1

    return res_list


def ner_main(opts, bot, logger):
    start_time = time.time()

    logger.write("{}\n".format(opts.test_file))
    logger.write("{}\n".format(opts.type_file))
    ## load data
    logger.write("loading data ...\n")
    with open(opts.test_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        r_types = list(types["relation"].values())

    ## sample
    index_list = list(range(0, len(data)))
    if opts.sample:
        logger.write("Sampling examples ...\n")
        selected_idx = random.sample(index_list, opts.sample_k)
        selected_idx.sort()
    else:
        selected_idx = index_list
    # selected_idx = index_list[:30]
    ## sample end

    ## API
    with open(opts.result_file, 'a', encoding='utf-8') as fw:
        fw.seek(0)  #定位
        fw.truncate()   #清空文件
        fw.write("[\n")
        logger.write("Evaluation begining ...\n")
        i = 0
        while i < len(selected_idx):
        
            idx = selected_idx[i]
            i += 1
            logger.write("No. "+ str(i) + " | example's id: " + str(idx) + " | total examples: " + str(len(data)) + "\n")
            example = data[idx]

            prompt = 'Considering {} types of named entities including {} and {}, recognize all named entities in the given sentence. Answer in the format ["entity_type", "entity_name"] without any explanation. If no entity exists, then just answer "[]". Given sentence: "{}"'.format(len(r_types), ", ".join(r_types[:-1]), r_types[-1], example['seq'])

            response = bot_run(bot, prompt, "NER", logger, model=opts.model)
            result_list = []
            lines = response.split("\n")
            for line in lines:
                tmp_res_list = response_string_to_list(line.strip())
                if tmp_res_list != [] and type(tmp_res_list[0]) == str:  # [, ]\n[, ]
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

            example.update({
                "NER": result_list,
                "prompt": prompt,
                "response": response
            })

            fw.write(json.dumps(example, indent=4, ensure_ascii=False))  
            if i != len(selected_idx):
                fw.write("\n,\n")
            else:
                fw.write("\n")
        fw.write("]\n")
    end_time = time.time()
    logger.write("The result is saved: {}\n".format(opts.result_file))
    logger.write("Times: {:.2f}s = {:.2f}m\n".format(end_time-start_time, (end_time-start_time)/60.0))


if __name__ == "__main__":
    opts = get_opts()

    api_key_file = os.path.join("./api-keys", opts.api_key)
    openai.api_key_path = api_key_file
    bot = openai.ChatCompletion()
    
    ## log file
    logger_file = os.path.join(opts.task, opts.logger_file)
    logger = Logger(file_name=logger_file)
    logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    if opts.task == "re":
        ner_main(opts, bot, logger)

