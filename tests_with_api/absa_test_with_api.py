import argparse, os
import json
import random
import time
import openai


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default="absa")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="wang/14lap")
    parser.add_argument('--test_file', type=str, default="test_convert.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=50)
    opts = parser.parse_args()
    return opts


def bot_run(prompt, task_name):
    print(task_name + "|[Prompt]:", prompt)
    para = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }
    response = bot.create(**para).choices[0].message
    response = response["content"].strip()
    print("#Response#: ", response)
    time.sleep(1)
    return response

# Aspect Term Extraction (AE)
def AE_task(bot, example):
    prompt = "Recognize all aspect terms in the following review with the format ['aspect_1', 'aspect_2', ...]: {}".format(example["raw_words"])
    return bot_run(prompt, "AE")

# Opinion Term Extraction (OE)
def OE_task(bot, example):
    prompt = "Recognize all opinion terms in the following review with the format ['opinion_1', 'opinion_2', ...]: {}".format(example["raw_words"])
    return bot_run(prompt, "OE")

# Aspect-level Sentiment Classification (ALSC)
def ALSC_task(bot, example):
    res = dict()
    for asp in example["aspects"]:
        asp_term = " ".join(asp["term"])
        if asp_term == "":
            continue
        prompt = "Recognize the sentiment polarity for aspect term '{}' in the following review with the format ['aspect', 'sentiment']: {}".format(asp_term, example["raw_words"])
        res[asp_term] = bot_run(prompt, "ALSC")
    return res

# Aspect-oriented Opinion Extraction (AOE)
def AOE_task(bot, example):
    res = dict()
    for asp in example["aspects"]:
        asp_term = " ".join(asp["term"])
        if asp_term == "":
            continue
        prompt = "Recognize the opinion term for aspect term '{}' in the following review with the format ['opinion_1', 'opinion_2', ...]: {}".format(asp_term, example["raw_words"])
        res[asp_term] = bot_run(prompt, "AOE")
    return res

# Aspect Term Extraction and Sentiment Classification (AESC)
def AESC_task(bot, example):
    prompt = "Recognize all aspect terms with their corresponding sentiment polarity in the following review with the format ['aspect', 'sentiment_polarity']: {}".format(example["raw_words"])
    return bot_run(prompt, "AESC")

# Pair Extraction (Pair)
def Pair_task(bot, example):
    prompt = "Recognize all aspect terms with their corresponding opinion terms in the following review with the format ['aspect', 'opinion']: {}".format(example["raw_words"])
    return bot_run(prompt, "Pair")

# Triplet Extraction (Triplet)
def Triplet_task(bot, example):
    prompt = "Recognize all aspect terms with their corresponding opinion terms and sentiment polarity in the following review with the format ['aspect', 'sentiment', 'opinion']: {}".format(example["raw_words"])
    return bot_run(prompt, "Triplet")


def absa_main(opts, bot):
    
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    input_dir = os.path.join(opts.input_dir, os.path.join(os.path.join(opts.task, opts.dataset), opts.test_file))
    print("loading data ...")
    with open(input_dir, 'r', encoding='utf-8') as fr:
        data = json.load(fr)

    print("Sampling examples ...")
    index_list = list(range(len(data)))
    selected_idx = random.sample(index_list, opts.sample_k)
    selected_idx.sort()

    with open(os.path.join(result_dir, opts.test_file.split('.')[0] + "_result.json"), 'a', encoding='utf-8') as fw:
        fw.seek(0)  #定位
        fw.truncate()   #清空文件
        print("Evaluation begining ...")
        i = 0
        for idx in selected_idx:
            i += 1
            print(i, " | ", idx)
            example = data[idx]
            result_dict = dict()
            result_dict.update(example)
            result_dict.pop("task")
            result_dict.pop("words")

            if example["task"] == "AE-OE":
                aspects = AE_task(bot, example)
                opinions = OE_task(bot, example)
                aspect_sentiment = ALSC_task(bot, example)
                pair_aspect_sentiment = AESC_task(bot, example)
                result_dict.update({"AE": aspects})
                result_dict.update({"OE": opinions})
                result_dict.update({"ALSC": aspect_sentiment})
                result_dict.update({"AESC": pair_aspect_sentiment})

            elif example["task"] == "AOE":
                opinion_of_aspect = AOE_task(bot, example)
                result_dict.update({"AOE": opinion_of_aspect})

            elif example["task"] == "AEOESC":
                # aspects = AE_task(bot, example)
                # opinions = OE_task(bot, example)
                # aspect_sentiment = ALSC_task(bot, example)
                # opinion_of_aspect = AOE_task(bot, example)
                pair_aspect_sentiment = AESC_task(bot, example)
                pair_aspect_opinion = Pair_task(bot, example)
                triplet = Triplet_task(bot, example)

                # result_dict.update({"AE": aspects})
                # result_dict.update({"OE": opinions})
                # result_dict.update({"ALSC": aspect_sentiment})
                # result_dict.update({"AOE": opinion_of_aspect})
                result_dict.update({"AESC": pair_aspect_sentiment})
                result_dict.update({"Pair": pair_aspect_opinion})
                result_dict.update({"Triplet": triplet})
            else:
                print("[Error]: unknown subtask", example["task"])

            fw.write(json.dumps(result_dict, indent=4, ensure_ascii=False))  
            fw.write("\n\n")


if __name__ == "__main__":
    opts = get_opts()

    openai.api_key_path = "./api-keys/api-key.txt"

    bot = openai.ChatCompletion()

    if opts.task == "absa":
        absa_main(opts, bot)

