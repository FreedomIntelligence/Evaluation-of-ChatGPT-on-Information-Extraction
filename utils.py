import json
import os, sys

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


class Logger(object):
    def __init__(self, file_name = 'chatgpt_eval.log', stream = sys.stdout) -> None:
        self.terminal = stream
        log_dir = "./logs"
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self.log = open(os.path.join(log_dir, file_name), "a")
        self.flush()

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.log.seek(0)	# 定位
        self.log.truncate()


if __name__ == "__main__":

    file_name = "./result/absa/pengb/14lap/test_convert_result.json"
    dict_list = read_json(file_name)
    with open("./result/absa/pengb/14lap/test_convert_result_dict.json", "w", encoding='utf-8')as fw:
        fw.write(json.dumps(dict_list, indent=4, ensure_ascii=False))
    # print(json.dumps(dict_list, indent=4, ensure_ascii=False))





    