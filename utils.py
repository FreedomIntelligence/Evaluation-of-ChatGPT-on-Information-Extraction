import json
import os, sys
import openai
import backoff
import ast

def read_json(file_name):
    dict_list = []
    with open(file_name) as f:
        dict_str = ""
        for line in f:
            if line.strip() != "":
                dict_str += line.strip()
            else:
                cur_dict = json.loads(dict_str)
                dict_list.append(cur_dict)
                dict_str = ""

    return dict_list

## Logger
class Logger(object):
    def __init__(self, file_name = 'chatgpt_eval.log', stream = sys.stdout) -> None:
        self.terminal = stream
        log_dir = "./logs"
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self.log = open(os.path.join(log_dir, file_name), "a", encoding='utf-8')
        self.flush()

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.log.seek(0)	# 定位
        self.log.truncate()

## connect OpenAI API
@backoff.on_exception(backoff.expo, \
                      (openai.error.RateLimitError, 
                       openai.error.APIConnectionError, 
                       openai.error.APIError))
def bot_create(bot, para):
    return bot.create(**para).choices[0].message

def bot_run(bot, prompt, task_name, logger, model="gpt-3.5-turbo"):
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
    response = response["content"].strip().strip("\n")
    logger.write("#Response#: " + response + "\n")
    # time.sleep(1)
    return response

## Eval
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
    
    response = response.lower()
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


def has_duplicate(tmp_list):
    """ has duplicate ?
    """
    if tmp_list == []:
        return False
    
    if type(tmp_list[0]) == str:
        if len(tmp_list) == len(set(tmp_list)):
            return False
        else:
            return True
        
    if type(tmp_list[0]) == list:
        tmp = []
        for t in tmp_list:
            if t not in tmp:
                tmp.append(t)
        if len(tmp_list) == len(tmp):
            return False
        else:
            return True
    
def get_correct_list_from_response_list(target_list, response_list):
    """
    target_list 和 response_list 均有可能包含重复的 item
    """
        
    res = []
    if not has_duplicate(response_list):
        res = [item for item in response_list if item in target_list]
    else:
        if not has_duplicate(target_list):
            # 去重
            uni_response_list = []
            for item in response_list:
                if item not in uni_response_list:
                    uni_response_list.append(item)
            res = [item for item in uni_response_list if item in target_list]
        else:
            res = []
            processed_item_list = []
            for item in response_list:
                if item not in processed_item_list:
                    processed_item_list.append(item)

                    num_item = response_list.count(item)
                    if num_item == 1:  # not duplicate
                        if item in target_list:
                            res.append(item)
                    else:  # duplicate
                        if item in target_list:
                            num_item_in_target = target_list.count(item)
                            num_item_correct = min([num_item, num_item_in_target])
                            res += [item] * num_item_correct
    
    return res

def print_metrics(tp, fp, fn, logger, task, align=8):
    p, r, f1 = 0.0, 0.0, 0.0

    if tp + fp != 0:
        p = 1.0 * tp / (tp + fp)
    if tp + fn != 0:
        r = 1.0 * tp / (tp + fn)
    if p + r != 0.0:
        f1 = 2.0 * p * r / (p + r)
    logger.write("{} | p: {:.4f}, r: {:.4f}, f1: {:.4f} | tp: {:4d}, fp: {:4d}, fn: {:4d}, tp+fn: {:4d}\n".format(
        task.ljust(align),
        round(p, 4),
        round(r, 4),
        round(f1, 4),
        tp,
        fp,
        fn,
        tp+fn,
        )
    )



if __name__ == "__main__":

    file_name = "./result/absa/pengb/14lap/test_convert_result.json"
    dict_list = read_json(file_name)
    with open("./result/absa/pengb/14lap/test_convert_result_dict.json", "w", encoding='utf-8')as fw:
        fw.write(json.dumps(dict_list, indent=4, ensure_ascii=False))
    # print(json.dumps(dict_list, indent=4, ensure_ascii=False))





    