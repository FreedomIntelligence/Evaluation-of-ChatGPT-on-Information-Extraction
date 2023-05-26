import os
import json
import random
import time
import openai
import sys
import threading
from absa_report_metric import report_metric_by_key
from config import get_opts
cur_path = os.getcwd()
sys.path.append(cur_path)
from utils import Logger, ReadSample, WriteSample, bot_run


def get_and_run_prompt(opts, bot, idx, total, example, prompt_dict, prompt_icl_dict, prompt_cot_dict, task="AE", aspect=None, best_prompt=1, logger=None, thread_idx=0):
    if opts.irrelevant:
        if "14lap" in opts.dataset:
            fr_no = open("./data/absa/wang/14lap/train_no_term.json", "r", encoding="utf-8")
            data_no_term = json.load(fr_no)
        if "14res" in opts.dataset:
            fr_no = open("./data/absa/wang/14res/train_no_term.json", "r", encoding="utf-8")
            data_no_term = json.load(fr_no)
        if "15res" in opts.dataset or "16res" in opts.dataset:
            fr_no = open("./data/absa/wang/15res/train_no_term.json", "r", encoding="utf-8")
            data_no_term = json.load(fr_no)
        
        irrelevant_text_list = [item["raw_words"] for item in data_no_term]

        random_text = random.sample(irrelevant_text_list, 2)

        input_text = random_text[0] + ". " + example["raw_words"] + ". " + random_text[1]
    else:
        input_text = example["raw_words"]

    prompt = ''
    if task in ["AE", "OE", "AESC", "Pair", "Triplet", "AESC_wang"]:
        if task == "AESC_wang":
            icl_cot_task = "AESC"
        else:
            icl_cot_task = task

        if opts.ICL:
            prompt = prompt_dict[task][best_prompt] + '\n' + prompt_icl_dict[icl_cot_task][opts.prompt-1] + '\nReview:\n"{}"\nAnswer:\n'.format(input_text)
        elif opts.COT:
            prompt = prompt_dict[task][best_prompt] + '\n' + prompt_cot_dict[icl_cot_task][opts.prompt-1] + '\nReview:\n"{}"\nAnswer:\n'.format(input_text)
                
        else:
            prompt = prompt_dict[task][opts.prompt-1] + '\nReview:\n"{}"\nAnswer:\n'.format(input_text)

    elif task in ["ALSC", "AOE", "ALSC_wang"]:
        if aspect is not None:
            if task == "ALSC_wang":
                icl_cot_task = "ALSC"
            else:
                icl_cot_task = task

            if opts.ICL:
                prompt = prompt_dict[task][best_prompt] + '\n' + prompt_icl_dict[icl_cot_task][opts.prompt-1] + '\nReview:\n"{}"\nAspect:\n"{}"\nAnswer:\n'.format(input_text, aspect)
            elif opts.COT:
                prompt = prompt_dict[task][best_prompt] + '\n' + prompt_cot_dict[icl_cot_task][opts.prompt-1] + '\nReview:\n"{}"\nAspect:\n"{}"\nAnswer:\n'.format(input_text, aspect)
                    
            else:
                prompt = prompt_dict[task][opts.prompt-1] + '\nReview:\n"{}"\nAspect:\n"{}"\nAnswer:\n'.format(input_text, aspect)
        else:
            logger.write("{} | no the aspect term !!!".format(task))
            exit()

    
    if opts.ICL or opts.COT:
        logger.write("Thread: {} | {} | ({}/{}) | Basic_prompt: {} | Prompt:\n{}\n".format(thread_idx, task, idx, total, best_prompt+1, prompt))
    else:
        logger.write(example["raw_words"]+"\n")
        logger.write(input_text + "\n")
        logger.write("Thread: {} | {} | ({}/{}) | Prompt:\n{}\n".format(thread_idx, task, idx, total, prompt))
    response = bot_run(bot, prompt, model=opts.model)
    if opts.ICL or opts.COT:
        logger.write("Thread: {} | {} | ({}/{}) | Basic_prompt: {} | Response:\n{}\n".format(thread_idx, task, idx, total, best_prompt+1, response))
    else:
        logger.write("Thread: {} | {} | ({}/{}) | Response:\n{}\n".format(thread_idx, task, idx, total, response))
    
    return response


## multi thread process
def thread_process(thread_id, opts, bot, read_sample, write_sample, prompt_dict, prompt_icl_dict, prompt_cot_dict, task, best_prompt, logger):
    while True:
        status, example = read_sample.get_item()
        if status:
            result_dict = dict()
            result_dict.update(example)
            result_dict.pop("task")
            idx = read_sample.cur_index
            total = len(read_sample.data_idx)
            if opts.ICL or opts.COT:
                result_dict["basic_prompt"] = best_prompt + 1

            if task in ["AE", "OE", "AESC", "AESC_wang", "Pair", "Triplet"]:
                response = get_and_run_prompt(opts, bot, idx, total, example, prompt_dict, prompt_icl_dict, prompt_cot_dict, task=task, aspect=None, best_prompt=best_prompt, logger=logger, thread_idx=thread_id)
                result_dict[task] = response

            if task in ["ALSC", "AOE", "ALSC_wang"]:
                res = dict()
                for asp in example["aspects"]:
                    asp_term = asp["term"]
                    if asp_term == "":
                        continue
                    res[asp_term] = get_and_run_prompt(opts, bot, idx, total, example, prompt_dict, prompt_icl_dict, prompt_cot_dict, task=task, aspect=asp_term, best_prompt=best_prompt, logger=logger, thread_idx=thread_id)

                result_dict[task] = res

            write_sample.write(result_dict)

        else:
            break


def run_task(opts, bot, data, selected_idx, prompt_dict, prompt_icl_dict, prompt_cot_dict, task="AE", logger=None):
    result_dir = os.path.join(opts.result_dir, opts.task, opts.dataset)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    result_file = os.path.join(result_dir, task + "-" + opts.result_file)
    
    if opts.multi_thread:
        read_sample = ReadSample(data, selected_idx)
        write_sample = WriteSample(result_file, 'a')
        threads_list = []

        for t_id in range(opts.num_thread):
            worker = threading.Thread(target=thread_process, args=(t_id+1, opts, bot, read_sample, write_sample, prompt_dict, prompt_icl_dict, prompt_cot_dict, task, opts.best_prompt, logger))
            worker.start()
            threads_list.append(worker)
        
        for th in threads_list:
            th.join()

        with open(result_file, "r", encoding="utf-8") as f:
            new_data = [json.loads(item) for item in f.readlines()] 
            print(len(new_data), len(data))
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(new_data, indent=4, ensure_ascii=False))

    else:
        data = [data[idx] for idx in selected_idx]
        with open(result_file, 'a', encoding='utf-8') as fw:
            fw.seek(0)  #定位
            fw.truncate()   #清空文件
            fw.write("[\n")

            for idx, example in enumerate(data):
                result_dict = dict()
                result_dict.update(example)
                result_dict.pop("task")
                if opts.ICL or opts.COT:
                    result_dict["basic_prompt"] = opts.best_prompt + 1

                if task in ["AE", "OE", "AESC", "AESC_wang", "Pair", "Triplet"]:
                    response = get_and_run_prompt(opts, bot, idx, len(data), example, prompt_dict, prompt_icl_dict, prompt_cot_dict, task=task, aspect=None, best_prompt=opts.best_prompt, logger=logger)
                    result_dict[task] = response

                if task in ["ALSC", "AOE", "ALSC_wang"]:
                    res = dict()
                    for asp in example["aspects"]:
                        asp_term = asp["term"]
                        if asp_term == "":
                            continue
                        res[asp_term] = get_and_run_prompt(opts, bot, idx, len(data), example, prompt_dict, prompt_icl_dict, prompt_cot_dict, task=task, aspect=asp_term, best_prompt=opts.best_prompt, logger=logger)

                    result_dict[task] = res

                fw.write(json.dumps(result_dict, indent=4, ensure_ascii=False))  
                if idx != len(data):
                    fw.write("\n,\n")
                else:
                    fw.write("\n")
            fw.write("]\n")
                

def get_best_prompt(opts, task, logger):
    file_name_list = [task + "-test_zero_" + str(i) + ".json" for i in range(1, 6)]

    f1_list = [report_metric_by_key(opts, task, file, logger) for file in file_name_list]

    best_prompt = f1_list.index(max(f1_list))
    return best_prompt


def absa_main(opts, bot, logger):
    start_time = time.time()
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    input_dir = os.path.join(opts.input_dir, os.path.join(os.path.join(opts.task, opts.dataset), opts.test_file))
    logger.write("loading data ...\n")
    with open(input_dir, 'r', encoding='utf-8') as fr:
        data = json.load(fr)

    if opts.ICL:
        prompt_icl_file = os.path.join(opts.input_dir, opts.task, opts.dataset, opts.icl_prompt)
        prompt_icl_dict = json.load(open(prompt_icl_file, "r", encoding="utf-8"))
        prompt_cot_dict = {}
    elif opts.COT:
        if "14lap" in opts.dataset:
            cot_dataset = "pengb/14lap"
        elif "14res" in opts.dataset:
            cot_dataset = "pengb/14res"
        elif "15res" in opts.dataset:
            cot_dataset = "pengb/15res"
        elif "16res" in opts.dataset:
            cot_dataset = "pengb/16res"

        prompt_cot_file = os.path.join(opts.input_dir, opts.task, cot_dataset, opts.cot_prompt)
        prompt_cot_dict = json.load(open(prompt_cot_file, "r", encoding="utf-8"))
        prompt_icl_dict = {}
            
    else:
        prompt_icl_dict = {}
        prompt_cot_dict = {}

    prompt_basic_file = os.path.join(opts.prompt_dir, opts.basic_prompt)
    prompt_dict = json.load(open(prompt_basic_file, "r", encoding="utf-8"))


    index_list = list(range(len(data)))
    if opts.sample:
        logger.write("Sampling examples ...\n")
        selected_idx = random.sample(index_list, opts.sample_k)
        selected_idx.sort()
        # print(selected_idx)
    else:
        selected_idx = index_list

    first_example = data[selected_idx[0]]
    if opts.irrelevant:
        if first_example["task"] == "AE-OE":
            task_list = ["AE", "OE", "ALSC_wang"]  
        elif first_example["task"] == "AOE":
            task_list = ["AOE"]
        elif first_example["task"] == "AEOESC":
            if "pengb" in opts.dataset:
                task_list = ["Triplet"] #
            else:
                task_list = ["AESC", "Pair"] #
    else:

        if first_example["task"] == "AE-OE":
            task_list = ["AE", "OE", "ALSC_wang", "AESC_wang"]  
        elif first_example["task"] == "AOE":
            task_list = ["AOE"]
        elif first_example["task"] == "AEOESC":
            task_list = ["AE", "OE", "ALSC", "AOE", "AESC", "Pair", "Triplet"] # 

    for task in task_list:
        if opts.ICL or opts.COT:
            opts.best_prompt = get_best_prompt(opts, task, logger)

        run_task(opts, bot, data, selected_idx, prompt_dict, prompt_icl_dict, prompt_cot_dict, task=task, logger=logger)
        
    end_time = time.time()
    logger.write("Times: {:.2f}s = {:.2f}m\n".format(end_time-start_time, (end_time-start_time)/60.0))


if __name__ == "__main__":
    opts = get_opts()

    api_key_file = os.path.join("./api-keys", opts.api_key)
    openai.api_key_path = api_key_file

    bot = openai.ChatCompletion()
    
    logger_file = opts.task + "-" + "-".join(opts.dataset.split("/")) + "-" + str(opts.prompt) + "-test.txt"
    if opts.ICL:
        logger_file = "ICL-" + logger_file
    if opts.COT:
        logger_file = "COT-" + logger_file
            

    logger_file = os.path.join(opts.task, logger_file)
    logger = Logger(file_name=logger_file)
    logger.write(api_key_file)
    logger.write("\n")

    if opts.task == "absa":    
        absa_main(opts, bot, logger)
