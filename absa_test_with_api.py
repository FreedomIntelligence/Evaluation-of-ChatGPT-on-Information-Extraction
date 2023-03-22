import os
import json
import random
import time
import openai
import backoff
from utils import Logger
from config import get_opts


@backoff.on_exception(backoff.expo, \
                      (openai.error.RateLimitError, 
                       openai.error.APIConnectionError, 
                       openai.error.APIError))
def bot_create(bot, para):
    return bot.create(**para).choices[0].message

def bot_run(bot, prompt, task_name, logger, model="gpt-3.5-turbo-0301"):
    logger.write(task_name + "|[Prompt]: " + prompt + "\n")
    para = {
        "model": model,
        "temperature": 0.0,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }
    # response = bot.create(**para).choices[0].message
    response = bot_create(bot, para)
    response = response["content"].strip()
    logger.write("#Response#: " + response + "\n")
    # time.sleep(1)
    return response

# Aspect Term Extraction (AE)
def AE_task(opts, bot, example, logger):
    prompt = 'Recognize all aspect terms in the review "{}". Answer in the format ["aspect_1", "aspect_2", ...] without any explanation. If no aspect term exists, then only answer "[]".'.format(example["raw_words"])
    return bot_run(bot, prompt, "AE", logger, model=opts.model)

# Opinion Term Extraction (OE)
def OE_task(opts, bot, example, logger):
    prompt = 'Recognize all opinion terms in the review "{}". Answer in the format ["opinion_1", "opinion_2", ...] without any explanation. If no opinion term exists, then only answer "[]".'.format(example["raw_words"])
    return bot_run(bot, prompt, "OE", logger, model=opts.model)

# Aspect-level Sentiment Classification (ALSC)
def ALSC_task(opts, bot, example, logger):
    res = dict()
    for asp in example["aspects"]:
        asp_term = asp["term"]
        if asp_term == "":
            continue
        
        prompt = 'Recognize the sentiment polarity for the aspect term "{}" in the review "{}". Answer from the options ["positive", "negative", "neutral"] without any explanation.'.format(asp_term, example["raw_words"])
        res[asp_term] = bot_run(bot, prompt, "ALSC", logger, model=opts.model)
    return res

def ALSC_task_for_wang(opts, bot, example, logger):
    res = dict()
    for asp in example["aspects"]:
        asp_term = asp["term"]
        if asp_term == "":
            continue
        
        prompt = 'Recognize the sentiment polarity for the aspect term "{}" in the review "{}". Answer from the options ["positive", "negative", "neutral", "conflict"] without any explanation.'.format(asp_term, example["raw_words"])
        res[asp_term] = bot_run(bot, prompt, "ALSC", logger, model=opts.model)
    return res

# Aspect-oriented Opinion Extraction (AOE)
def AOE_task(opts, bot, example, logger):
    res = dict()
    for asp in example["aspects"]:
        asp_term = asp["term"]
        if asp_term == "":
            continue
        prompt = 'Recognize the opinion terms for the aspect term "{}" in the review "{}". Answer in the format ["opinion_1", "opinion_2", ...] without any explanation. If no opinion term exists, then only answer "[]".'.format(asp_term, example["raw_words"])
        res[asp_term] = bot_run(bot, prompt, "AOE", logger, model=opts.model)
    return res

# Aspect Term Extraction and Sentiment Classification (AESC)
def AESC_task(opts, bot, example, logger):
    prompt = 'Recognize all aspect terms with their corresponding sentiment polarity in the review "{}". Answer in the format ["aspect", "sentiment"] without any explanation. If no aspect term exists, then only answer "[]".'.format(example["raw_words"])
    return bot_run(bot, prompt, "AESC", logger, model=opts.model)

# Pair Extraction (Pair)
def Pair_task(opts, bot, example, logger):
    prompt = 'Recognize all aspect terms with their corresponding opinion terms in the review "{}". Answer in the format ["aspect", "opinion"] without any explanation. If no aspect term exists, then only answer "[]".'.format(example["raw_words"])
    return bot_run(bot, prompt, "Pair", logger, model=opts.model)

# Triplet Extraction (Triplet)
def Triplet_task(opts, bot, example, logger):
    prompt = 'Recognize all aspect terms with their corresponding opinion terms and sentiment polarity in the review "{}". Answer in the format ["aspect", "sentiment", "opinion"] without any explanation. If no aspect term exists, then only answer "[]".'.format(example["raw_words"])
    return bot_run(bot, prompt, "Triplet", logger, model=opts.model)


def absa_main(opts, bot, logger):
    start_time = time.time()
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    input_dir = os.path.join(opts.input_dir, os.path.join(os.path.join(opts.task, opts.dataset), opts.test_file))
    logger.write("loading data ...\n")
    with open(input_dir, 'r', encoding='utf-8') as fr:
        data = json.load(fr)

    index_list = list(range(len(data)))
    if opts.sample:
        logger.write("Sampling examples ...\n")
        selected_idx = random.sample(index_list, opts.sample_k)
        selected_idx.sort()
        print(selected_idx)
    else:
        selected_idx = index_list

    with open(os.path.join(result_dir, opts.result_file), 'a', encoding='utf-8') as fw:
        fw.seek(0)  #定位
        fw.truncate()   #清空文件
        fw.write("[\n")
        logger.write("Evaluation begining ...\n")
        i = 0
        while i < len(selected_idx):
        # for idx in selected_idx:
            idx = selected_idx[i]
            i += 1
            logger.write("No. "+ str(i) + " | example's id: " + str(idx) + " | total examples: " + str(len(data)) + "\n")
            example = data[idx]
            result_dict = dict()
            result_dict.update(example)
            result_dict.pop("task")

            if example["task"] == "AE-OE":
                aspects = AE_task(opts, bot, example, logger)
                opinions = OE_task(opts, bot, example, logger)
                aspect_sentiment = ALSC_task_for_wang(opts, bot, example, logger)
                pair_aspect_sentiment = AESC_task(opts, bot, example, logger)
                logger.write("\n")
                result_dict.update({"AE": aspects})
                result_dict.update({"OE": opinions})
                result_dict.update({"ALSC": aspect_sentiment})
                result_dict.update({"AESC": pair_aspect_sentiment})

            elif example["task"] == "AOE":
                opinion_of_aspect = AOE_task(opts, bot, example, logger)
                logger.write("\n")
                result_dict.update({"AOE": opinion_of_aspect})

            elif example["task"] == "AEOESC":
                aspects = AE_task(opts, bot, example, logger)
                opinions = OE_task(opts, bot, example, logger)
                aspect_sentiment = ALSC_task(opts, bot, example, logger)
                opinion_of_aspect = AOE_task(opts, bot, example, logger)
                pair_aspect_sentiment = AESC_task(opts, bot, example, logger)
                pair_aspect_opinion = Pair_task(opts, bot, example, logger)
                triplet = Triplet_task(opts, bot, example, logger)
                logger.write("\n")

                result_dict.update({"AE": aspects})
                result_dict.update({"OE": opinions})
                result_dict.update({"ALSC": aspect_sentiment})
                result_dict.update({"AOE": opinion_of_aspect})
                result_dict.update({"AESC": pair_aspect_sentiment})
                result_dict.update({"Pair": pair_aspect_opinion})
                result_dict.update({"Triplet": triplet})
            else:
                logger.write("[Error]: unknown subtask " + example["task"] + "\n")

            fw.write(json.dumps(result_dict, indent=4, ensure_ascii=False))  
            if i != len(selected_idx):
                fw.write("\n,\n")
            else:
                fw.write("\n")
        fw.write("]\n")
    end_time = time.time()
    logger.write("Times: {:.2f}s = {:.2f}m\n".format(end_time-start_time, (end_time-start_time)/60.0))


if __name__ == "__main__":
    opts = get_opts()

    api_key_file = os.path.join("./api-keys", opts.api_key)
    openai.api_key_path = api_key_file

    bot = openai.ChatCompletion()
    
    logger_file = opts.task + "-" + "-".join(opts.dataset.split("/")) + "-test.log"
    logger = Logger(file_name=logger_file)
    logger.write(api_key_file)
    logger.write("\n")
    # print(api_key_file)

    if opts.task == "absa":
        absa_main(opts, bot, logger)

