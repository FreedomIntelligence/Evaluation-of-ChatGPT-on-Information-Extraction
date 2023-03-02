import json

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


if __name__ == "__main__":

    file_name = "./result/absa/wang/14lap/test_convert_result.json"
    dict_list = read_json(file_name)
    print(json.dumps(dict_list, indent=4, ensure_ascii=False))





    