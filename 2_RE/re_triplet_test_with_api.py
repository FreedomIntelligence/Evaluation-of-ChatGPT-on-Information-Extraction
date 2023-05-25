import json
import os
import sys
import random
import time
import openai
import threading
from config import get_opts_re as get_opts
from re_triplet_report_metric import triplet_report_metric
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, bot_run, ReadSample, WriteSample


def get_prompt_list(r_types, e_types):
    na_item = r_types[-1]
    r_types = list(set(r_types[:-1]))
    prompt_list = []

    if len(e_types) != 0:
        prompt = 'Extract all relational fact triples from the given text, which consist of subject entity, object entity and the relation between two entities. The subject/object entity can be of the following types {}. The relation between entities can be of the following types {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(e_types), json.dumps(r_types))
        prompt_list.append(prompt)

        prompt = 'From the list of relations: {}, first find out all relations expressed by the given text, then identify the subject and object entities for each expressed relation. The subject/object entity can be of the following types {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types), json.dumps(e_types))
        prompt_list.append(prompt)

        prompt = 'Given the list of relations: {}, judge whether each relation is expressed by the given text, return all expressed relations along with their corresponding subject and object entities. The subject/object entity can be of the following types {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types), json.dumps(e_types))
        prompt_list.append(prompt)

        prompt = 'Given the list of entity types: {}, recognize all named entities from the given text, then judge whether any subject-object entity pair express the relation in the predefined list. The list of predefined relations is {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(e_types), json.dumps(r_types))
        prompt_list.append(prompt)

        e_types = ['"' + item + '"' for item in e_types]
        prompt = 'Considering entity types of {} and {}, find out all named entities in the given text, then return all subject-object entity pairs that express predefined relations. The list of predefined relations is {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(", ".join(e_types[:-1]), e_types[-1], json.dumps(r_types))
        prompt_list.append(prompt)
    else:
        prompt = 'Extract all relational fact triples from the given text, which consist of subject entity, object entity and the relation between two entities. The relation between entities can be of the following types {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types))
        prompt_list.append(prompt)

        prompt = 'From the list of relations: {}, first find out all relations expressed by the given text, then identify the subject and object entities for each expressed relation.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types))
        prompt_list.append(prompt)

        prompt = 'Given the list of relations: {}, judge whether each relation is expressed by the given text, return all expressed relations along with their corresponding subject and object entities.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types))
        prompt_list.append(prompt)

        prompt = 'Recognize all named entities from the given text, then judge whether any subject-object entity pair express the relation in the predefined list. The list of predefined relations is {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types))
        prompt_list.append(prompt)

        e_types = ['"' + item + '"' for item in e_types]
        prompt = 'Find out all named entities in the given text, then return all subject-object entity pairs that express predefined relations. The list of predefined relations is {}.\nAnswer in the format \'["subject_entity", "relation", "object_entity"]\' without any explanation. If no relation exists, then just answer "[]".'.format(json.dumps(r_types))
        prompt_list.append(prompt)

    return prompt_list


def get_icl_cot_prompt_list(opts):
    prompt_icl_list, prompt_cot_list = {}, {}
    if opts.ICL:
        prompt_icl_file = os.path.join(opts.input_dir, opts.task, opts.dataset, opts.icl_prompt)
        prompt_icl_list = json.load(open(prompt_icl_file, "r", encoding="utf-8"))
        prompt_cot_list = {}
    elif opts.COT:
        prompt_cot_file = os.path.join(opts.input_dir, opts.task, opts.dataset, opts.cot_prompt)
        prompt_cot_list = json.load(open(prompt_cot_file, "r", encoding="utf-8"))
        prompt_icl_list = {}
    return prompt_icl_list, prompt_cot_list


def re_triplet_get_prompt(opts, example, prompt_list, prompt_icl_list, prompt_cot_list):

    tokens = example['seq'].split(" ")
    if len(tokens) > 1024:
        seq_str = " ".join(tokens[:1024])
    else:
        seq_str = example['seq']

    if opts.irrelevant:
        file_name = os.path.join(opts.input_dir, opts.task, opts.dataset, "train_no_relation.json")
        fr_no = open(file_name, "r", encoding="utf-8")
        data_no_term = json.load(fr_no)
        
        irrelevant_text_list = [item["seq"] for item in data_no_term]

        random_text = random.sample(irrelevant_text_list, 2)

        input_text = random_text[0] + " " + seq_str+ " " + random_text[1]
    else:
        input_text = seq_str

    if opts.ICL:
        prompt = prompt_list[opts.best_prompt] + "\n" + prompt_icl_list[opts.prompt-1] + '\nGiven text:\n"{}"\nAnswer:\n'.format(input_text)
    elif opts.COT:
        prompt = prompt_list[opts.best_prompt] + "\n" + prompt_cot_list[opts.prompt-1] + '\nGiven text:\n"{}"\nAnswer:\n'.format(input_text)
    else:
        prompt = prompt_list[opts.prompt-1] + '\nGiven text:\n"{}"'.format(input_text)
    return prompt


def get_best_prompt(opts, logger):
    file_name_list = ["re_triplet_result_" + str(i) + ".json" for i in range(1, 6)]

    f1_list = [triplet_report_metric(opts, logger, file_name=file) for file in file_name_list]

    best_prompt = f1_list.index(max(f1_list))
    return best_prompt


def re_triplet_main(opts, bot, logger):
    start_time = time.time()

    logger.write("{}\n".format(opts.test_file))
    logger.write("{}\n".format(opts.type_file))
    ## load data
    logger.write("loading data ...\n")
    with open(opts.test_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        r_types = list(types["relation"].values())
        e_types = list(types["entity"].values())

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

    prompt_list = get_prompt_list(r_types, e_types)
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

            print(example["seq"])

            prompt = re_triplet_get_prompt(opts, example, prompt_list, prompt_icl_list, prompt_cot_list)
            logger.write("RE-Triplet | " + str(i) + "/" + str(len(data)) + " | Prompt:\n" + prompt + "\n")

            response = bot_run(bot, prompt, model=opts.model)
            logger.write("RE-Triplet | " + str(i) + "/" + str(len(data)) + " | Response:\n" + response + "\n")

            # result_dict = get_result_dict(response)
            result_dict = {}

            example.update({
                "RE": result_dict,
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

            prompt = re_triplet_get_prompt(opts, example, prompt_list, prompt_icl_list, prompt_cot_list)

            logger.write("Thread: " + str(thread_id) + " | RE-Triplet | " + str(cur_idx) + "/" + str(total) + " | Prompt:\n" + prompt + "\n")
            response = bot_run(bot, prompt, model=opts.model)
            logger.write("Thread: " + str(thread_id) + " | RE-Triplet | " + str(cur_idx) + "/" + str(total) + " | Response:\n" + response + "\n")

            # result_dict = get_result_dict(response)
            result_dict = {}

            example.update({
                "RE": result_dict,
                "prompt": prompt,
                "response": response
            })
            if opts.ICL or opts.COT:
                example["best_prompt"] = opts.best_prompt + 1

            write_sample.write(example)

        else:
            break


def re_triplet_main_multi_thread(opts, bot, logger, num_thread=10):
    start_time = time.time()

    logger.write("{}\n".format(opts.test_file))
    logger.write("{}\n".format(opts.type_file))
    ## load data
    logger.write("loading data ...\n")
    with open(opts.test_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        r_types = list(types["relation"].values())
        e_types = list(types["entity"].values())

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

    prompt_list = get_prompt_list(r_types, e_types)
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
    with open(opts.result_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(new_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    opts = get_opts()

    api_key_file = os.path.join("./api-keys", opts.api_key)
    openai.api_key_path = api_key_file
    bot = openai.ChatCompletion()
    
    ## log file
    logger_file = os.path.join(opts.task, opts.logger_file)
    logger = Logger(file_name=logger_file)
    # logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    if opts.task == "re":
        if opts.multi_thread:
            re_triplet_main_multi_thread(opts, bot, logger, num_thread=opts.num_thread)
        else:
            re_triplet_main(opts, bot, logger)
