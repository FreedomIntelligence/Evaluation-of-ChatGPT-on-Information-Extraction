import json
import sys, os
import random
import time
import ast
import openai
import threading
from config import get_opts_ner as get_opts
from ner_report_metric import report_metric_by_file, get_result_list
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, bot_run, ReadSample, WriteSample


def get_prompt_list(e_types):
    prompt_list = []

    # 1
    prompt = 'Considering {} types of named entities including {} and {}, recognize all named entities in the given sentence.\nAnswer in the format ["entity_type", "entity_name"] without any explanation. If no entity exists, then just answer "[]".'.format(len(e_types), ", ".join(e_types[:-1]), e_types[-1])
    prompt_list.append(prompt)

    # 2
    e_types_tmp = [item.strip('"') for item in e_types]
    prompt = 'Given the list of entity types {}, read the given sentence and find out all words/phrases that indicate the above types of named entities.\nAnswer in the format ["entity_type", "entity_name"] without any explanation. If no entity exists, then just answer "[]".'.format(json.dumps(e_types_tmp))
    prompt_list.append(prompt)

    # 3
    prompt = 'Read the given sentence carefully, identify all named entities of type {} or {}.\nAnswer in the format ["entity_type", "entity_name"] without any explanation. If no entity exists, then just answer "[]".'.format(", ".join(e_types[:-1]), e_types[-1])
    prompt_list.append(prompt)

    # 4
    prompt = 'Analyze the given sentence and extract all word spans that refer to specific named entities of type {} or {}.\nAnswer in the format ["entity_type", "entity_name"] without any explanation. If no entity exists, then just answer "[]".'.format(", ".join(e_types[:-1]), e_types[-1])
    prompt_list.append(prompt)

    # 5
    prompt = 'What named entities are mentioned in the given sentence? Only return named entities of type {} or {}.\nAnswer in the format ["entity_type", "entity_name"] without any explanation. If no entity exists, then just answer "[]".'.format(", ".join(e_types[:-1]), e_types[-1])
    prompt_list.append(prompt)

    return prompt_list


def get_icl_cot_prompt_list(opts):
    prompt_icl_list, prompt_cot_list = {}, {}
    if opts.ICL:
        prompt_icl_file = os.path.join(opts.input_dir, opts.task, opts.dataset, opts.icl_prompt)
        prompt_icl_list = json.load(open(prompt_icl_file, "r", encoding="utf-8"))
    elif opts.COT:
        prompt_cot_file = os.path.join(opts.input_dir, opts.task, opts.dataset, opts.cot_prompt)
        prompt_cot_list = json.load(open(prompt_cot_file, "r", encoding="utf-8"))

    return prompt_icl_list, prompt_cot_list


def ner_get_prompt(opts, example, prompt_list, prompt_icl_list, prompt_cot_list):
    if opts.irrelevant:
        file_name = os.path.join(opts.input_dir, opts.task, opts.dataset, "train_no_entity.json")
        fr_no = open(file_name, "r", encoding="utf-8")
        data_no_term = json.load(fr_no)
        irrelevant_text_list = [item["seq"] for item in data_no_term]
        random_text = random.sample(irrelevant_text_list, 2)

        input_text = random_text[0] + " " + example["seq"] + " " + random_text[1]
    else:
        input_text = example["seq"]

    if opts.ICL:
        prompt = prompt_list[opts.best_prompt] + "\n" + prompt_icl_list[opts.prompt-1] + '\nSentence:\n"{}"\nAnswer:\n'.format(input_text)
    elif opts.COT:
        prompt = prompt_list[opts.best_prompt] + "\n" + prompt_cot_list[opts.prompt-1] + '\nSentence:\n"{}"\nAnswer:\n'.format(input_text)
    else:
        prompt = prompt_list[opts.prompt-1] + '\nGiven sentence:\n"{}"'.format(input_text)

    return prompt


def get_best_prompt(opts, logger):
    file_name_list = ["ner_result_" + str(i) + ".json" for i in range(1, 6)]

    f1_list = [report_metric_by_file(opts, file, logger, mode="strict", match="hard") for file in file_name_list]
    best_prompt = f1_list.index(max(f1_list))

    return best_prompt


def ner_main(opts, bot, logger):
    start_time = time.time()

    logger.write("{}\n".format(opts.test_file))
    logger.write("{}\n".format(opts.type_file))
    ## load data
    logger.write("loading data ...\n")
    with open(opts.test_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        e_types = ['"' + types["entities"][item]["short"] + '"' for item in types["entities"]]
        if opts.verbose_type:
            e_types = ['"' + types["entities"][item]["verbose"] + '"' for item in types["entities"]]

    ## sample
    index_list = list(range(0, len(data)))
    if opts.sample:
        logger.write("Sampling examples ...\n")
        selected_idx = random.sample(index_list, opts.sample_k)
        selected_idx.sort()
        print(selected_idx)
    else:
        selected_idx = index_list
    ## sample end

    prompt_list = get_prompt_list(e_types)
    prompt_icl_list, prompt_cot_list = get_icl_cot_prompt_list(opts)

    if opts.ICL or opts.COT:
        opts.best_prompt = get_best_prompt(opts, logger)

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

            prompt = ner_get_prompt(opts, example, prompt_list, prompt_icl_list, prompt_cot_list)
            print(example["seq"])

            logger.write("NER | " + str(i) + "/" + str(len(data)) + " | Prompt:\n" + prompt + "\n")
            response = bot_run(bot, prompt, model=opts.model)
            logger.write("NER | " + str(i) + "/" + str(len(data)) + " | Response:\n" + response + "\n")

            result_list = []
            example.update({
                "NER": result_list,
                "prompt": prompt,
                "response": response
            })
            if opts.ICL or opts.COT:
                example["best_prompt"] = opts.best_prompt + 1

            fw.write(json.dumps(example, indent=4, ensure_ascii=False))  
            if i != len(selected_idx):
                fw.write("\n,\n")
            else:
                fw.write("\n")
        fw.write("]\n")
    end_time = time.time()
    logger.write("The result is saved: {}\n".format(opts.result_file))
    logger.write("Times: {:.2f}s = {:.2f}m\n".format(end_time-start_time, (end_time-start_time)/60.0))


## multi thread process
def thread_process(thread_id, opts, bot, read_sample, write_sample, prompt_list, prompt_icl_list, prompt_cot_list, logger):
    while True:
        status, example = read_sample.get_item()
        if status:
            cur_idx = read_sample.cur_index
            total = len(read_sample.data_idx)

            prompt = ner_get_prompt(opts, example, prompt_list, prompt_icl_list, prompt_cot_list)

            logger.write("Thread: " + str(thread_id) + " | NER | " + str(cur_idx) + "/" + str(total) + " | Prompt:\n" + prompt + "\n")
            response = bot_run(bot, prompt, model=opts.model)
            logger.write("Thread: " + str(thread_id) + " | NER | " + str(cur_idx) + "/" + str(total) + " | Response:\n" + response + "\n")

            result_list = []
            example.update({
                "NER": result_list,
                "prompt": prompt,
                "response": response,
            })
            if opts.ICL or opts.COT:
                example["best_prompt"] = opts.best_prompt + 1

            write_sample.write(example)

        else:
            break


def ner_main_multi_thread(opts, bot, logger, num_thread=10):
    start_time = time.time()

    logger.write("{}\n".format(opts.test_file))
    logger.write("{}\n".format(opts.type_file))
    ## load data
    logger.write("loading data ...\n")
    with open(opts.test_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        e_types = ['"' + types["entities"][item]["short"] + '"' for item in types["entities"]]
        if opts.verbose_type:
            e_types = ['"' + types["entities"][item]["verbose"] + '"' for item in types["entities"]]

    ## sample
    index_list = list(range(0, len(data)))
    if opts.sample:
        logger.write("Sampling examples ...\n")
        selected_idx = random.sample(index_list, opts.sample_k)
        selected_idx.sort()
        print(selected_idx)
    else:
        selected_idx = index_list
    ## sample end

    prompt_list = get_prompt_list(e_types)
    prompt_icl_list, prompt_cot_list = get_icl_cot_prompt_list(opts)
    if opts.ICL or opts.COT:
        opts.best_prompt = get_best_prompt(opts, logger)

    logger.write("Evaluation begining ...\n")
    read_sample = ReadSample(data, selected_idx)
    write_sample = WriteSample(opts.result_file, 'a')

    threads_list = []

    for t_id in range(num_thread):
        worker = threading.Thread(target=thread_process, args=(t_id+1, opts, bot, read_sample, write_sample, prompt_list, prompt_icl_list, prompt_cot_list, logger))
        worker.start()
        threads_list.append(worker)
    
    for th in threads_list:
        th.join()

    end_time = time.time()
    logger.write("Times: {:.2f}s = {:.2f}m\n".format(end_time-start_time, (end_time-start_time)/60.0)) 
    with open(opts.result_file, "r", encoding="utf-8") as f:
        new_data = [json.loads(item) for item in f.readlines()] 
        logger.write(str(len(new_data)) + " " + str(len(data)) + "\n")
        # print(len(new_data), len(data))
    with open(opts.result_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(new_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    opts = get_opts()

    api_key_file = os.path.join("./api-keys", opts.api_key)
    openai.api_key_path = api_key_file
    bot = openai.ChatCompletion()
    
    ## log file
    logger_file = os.path.join(opts.task, opts.logger_file)
    print(logger_file)
    logger = Logger(file_name=logger_file)
    logger.write(json.dumps(opts.__dict__, indent=4) + "\n")
    logger.write(api_key_file + "\n")

    if opts.task == "ner":
        if opts.multi_thread:
            ner_main_multi_thread(opts, bot, logger, num_thread=opts.num_thread)
        else:
            ner_main(opts, bot, logger)

