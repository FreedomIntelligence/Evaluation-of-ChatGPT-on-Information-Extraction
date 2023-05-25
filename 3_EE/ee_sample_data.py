import os
import json
import random
import ast

output_dir = "./data"


def ee_data_sample_trigger(dataset, input_file, test_file, type_file, max_l=50, k=5, fold=5):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name_trigger = os.path.join(output_path, "new_prompt_icl_trigger.json")
    output_file_name_sample = os.path.join(output_path, "new_data_sample_trigger.json")
    output_file_name_argument = os.path.join(output_path, "new_prompt_icl_argument.json")
    test_file_name = os.path.join(output_path, test_file)
    type_file_name = os.path.join(output_path, type_file)
    
    print("Load file: {}".format(in_file_name))
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft, \
                open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        evt_types_dict = types["event_types"]

        ## 去重
        uni_data = []
        seq_list = []
        num_lap = 0
        for example in data:
            if example["text"] not in seq_list:
                seq_list.append(example["text"])
                uni_data.append(example)
            else:
                num_lap += 1

        data = uni_data
        print(len(data), num_lap)

        ## 统计 test file
        test_data = [item["text"] for item in json.load(ft)]
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)

        print(num_test_all/len(test_data))
        
        ## 统计 train file
        num = 0.0
        num_in_test = 0
        data_no_in_test = []
        for example in data:  
            if example["text"] not in test_data:
                num += len(example["text"])
                data_no_in_test.append(example)
            else:
                num_in_test += 1

        print(num/len(data_no_in_test), num_in_test)

        data_no_in_test_max_l = []
        for example in data_no_in_test:
            tokens = example["text"].split(" ")
            if len(tokens) <= max_l and len(tokens) >= 10:
                data_no_in_test_max_l.append(example)

        print("words less \"max_l\":", len(data_no_in_test_max_l), len(data_no_in_test))

        ## no_term && with_term
        data_no_event = []
        data_with_event = []

        for example in data_no_in_test_max_l:
            if example["event"] != []:
                data_with_event.append(example)
            else:
                data_no_event.append(example)

        print("no rel:", len(data_no_event), len(data_with_event))

        # multi-event_mention
        multi_event_same = []
        multi_event_diff = []
        single_event = []
        evt2example = {}
        evt2example_multi_same = {}
        evt2example_multi_diff = {}
        for example in data_with_event:

            if len(example["event"]) == 1:
                single_event.append(example)
                if example["event"][0]["subtype"] not in evt2example:
                    evt2example[example["event"][0]["subtype"]] = [example]
                else:
                    evt2example[example["event"][0]["subtype"]].append(example)
            else:
                evt_list = []
                for evt in example["event"]:
                    if evt["subtype"] not in evt_list:
                        evt_list.append(evt["subtype"])
                
                if len(evt_list) == 1:
                    multi_event_same.append(example)
                    for evt_k in evt_list:
                        if evt_k not in evt2example_multi_same:
                            evt2example_multi_same[evt_k] = [example]
                        else:
                            evt2example_multi_same[evt_k].append(example)
                else:
                    multi_event_diff.append(example)
                    for evt_k in evt_list:
                        if evt_k not in evt2example_multi_diff:
                            evt2example_multi_diff[evt_k ] = [example]
                        else:
                            evt2example_multi_diff[evt_k ].append(example)

        print(len(single_event), len(multi_event_same), len(multi_event_diff))

        ## sample no entity
        sample_no_event = random.sample(data_no_event, 1*fold)
        # print(len(sample_no_event))

        sample_with_event = []
        for i in range(fold):
            exist_keys = []
            sample_data = []
            cur_keys = list(evt2example_multi_same.keys())
            # print(cur_keys)
            select_key = random.sample(cur_keys, 1)[0]
            sample_data += random.sample(evt2example_multi_same[select_key], 1)
            exist_keys.append(select_key)

            cur_keys = list(set(evt2example_multi_diff.keys()) - set(exist_keys))
            select_key = random.sample(cur_keys, 1)[0]
            
            cur_item = random.sample(evt2example_multi_diff[select_key], 1)[0]
            sample_data.append(cur_item)
            cur_item_keys = []
            for ee in cur_item["event"]:
                if ee["subtype"] not in cur_item_keys:
                    cur_item_keys.append(ee["subtype"])

            exist_keys += cur_item_keys

            cur_keys = list(set(evt2example.keys()) - set(exist_keys))
            select_keys = random.sample(cur_keys, 2)
            for select_key in select_keys:
                sample_data += random.sample(evt2example[select_key], 1)
            
            # print(len(sample_data))
            sample_with_event.append(sample_data)
        
        res_sample_data = []
        for i in range(fold):
            new_list = sample_with_event[i][2:] + sample_with_event[i][:2] + [sample_no_event[i]] 
            res_sample_data.append(new_list)

        with open(output_file_name_sample, "w", encoding="utf-8") as fw_sample:
            # print(len(res_sample_data))
            json.dump(res_sample_data, fw_sample, indent=4, ensure_ascii=False)

        prompt_trigger = []
        for i in range(fold):
            tmp = []
            evt_type_list = []
            for example in res_sample_data[i]:
                evt_list = []
                for evt in example["event"]:
                    evt_list.append([evt["trigger"], evt_types_dict[evt["subtype"].replace(":", ".")]["verbose"]])
                    if evt["subtype"] not in evt_type_list:
                        evt_type_list.append(evt["subtype"])

                if len(evt_list) != 0:
                    trigger_str = ", ".join([json.dumps(item) for item in evt_list])
                else:
                    trigger_str = "[]"
                tmp_prompt = 'Given text:\n"{}"\nAnswer:\n{}'.format(example["text"], trigger_str)
                tmp.append(tmp_prompt)
            
            print(len(evt_type_list))

        
            prompt_trigger.append("\n".join(tmp))

        # print(prompt_trigger)

        
        with open(output_file_name_trigger, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_trigger, indent=4, ensure_ascii=False))
        print("finish!!")
        print()


def ee_data_sample_argument(dataset, input_file, test_file, type_file, max_l=50, k=5, fold=5):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name_sample = os.path.join(output_path, "new_data_sample_argument.json")
    output_file_name_sample_1 = os.path.join(output_path, "new_data_sample_joint.json")

    test_file_name = os.path.join(output_path, test_file)
    type_file_name = os.path.join(output_path, type_file)
    
    print("Load file: {}".format(in_file_name))
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft, \
                open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        evt_types_dict = types["event_types"]

        ## 去重
        uni_data = []
        seq_list = []
        num_lap = 0
        for example in data:
            if example["text"] not in seq_list:
                seq_list.append(example["text"])
                uni_data.append(example)
            else:
                num_lap += 1

        data = uni_data
        print(len(data), num_lap)

        ## 统计 test file
        test_data = [item["text"] for item in json.load(ft)]
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)

        print(num_test_all/len(test_data))
        
        ## 统计 train file
        num = 0.0
        num_in_test = 0
        data_no_in_test = []
        for example in data:  
            if example["text"] not in test_data:
                num += len(example["text"])
                data_no_in_test.append(example)
            else:
                num_in_test += 1

        print(num/len(data_no_in_test), num_in_test)

        data_no_in_test_max_l = []
        for example in data_no_in_test:
            tokens = example["text"].split(" ")
            if len(tokens) <= max_l and len(tokens) >= 10:
                data_no_in_test_max_l.append(example)

        print("words less \"max_l\":", len(data_no_in_test_max_l), len(data_no_in_test))

        ## no_term && with_term
        data_no_event = []
        data_with_event = []

        for example in data_no_in_test_max_l:
            if example["event"] != []:
                data_with_event.append(example)
            else:
                data_no_event.append(example)

        print("no rel:", len(data_no_event), len(data_with_event))

        with open(os.path.join(output_path, "train_no_event.json"), 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(data_no_event, indent=4, ensure_ascii=False))
            print(len(data_no_event))

        data_single_with_argument = []
        data_multi_with_argument = []
        data_no_argument = []
        no_type2example = {}
        single_type2example = {}
        multi_type2example = {}
        for example in data_with_event:
            if len(example["event"]) == 1:
                evt_type = example["event"][0]["subtype"]
                if len(example["event"][0]["arguments"]) == 0:
                    data_no_argument.append(example)
                    if evt_type not in no_type2example:
                        no_type2example[evt_type] = [example]
                    else:
                        no_type2example[evt_type].append(example)
                else:
                    data_single_with_argument.append(example)
                    if evt_type not in single_type2example:
                        single_type2example[evt_type] = [example]
                    else:
                        single_type2example[evt_type].append(example)
            else:
                evt_list = []
                for evt in example["event"]:
                    if evt["subtype"] not in evt_list:
                        evt_list.append(evt["subtype"])
                if len(evt_list) > 1:
                    flag = False
                    for idx, evt in enumerate(example["event"]):
                        if len(evt["arguments"]) > 0 and idx < 2:
                            flag = True
                            break
                    if flag:
                        data_multi_with_argument.append(example)
                        for evt in example["event"]:
                            evt_type = evt["subtype"]
                            if evt_type not in multi_type2example:
                                multi_type2example[evt_type] = [example]
                            else:
                                multi_type2example[evt_type].append(example)
        
        print(len(data_no_argument), len(data_single_with_argument), len(data_multi_with_argument))

        sample_no_event = random.sample(data_no_event, 1*fold)

        sample_with_argument = []
        for i in range(fold):
            exist_keys = []
            sample_data = []
            cur_keys = list(no_type2example.keys())
            select_key = random.sample(cur_keys, 1)[0]
            sample_data += random.sample(no_type2example[select_key], 1)
            exist_keys.append(select_key)

            cur_keys = list(multi_type2example.keys())
            # print(cur_keys)
            select_key = random.sample(cur_keys, 1)[0]
            
            flag = True
            cur_data = []
            while flag:
                flag = False
                cur_data = random.sample(multi_type2example[select_key], 1)
                for evt in cur_data[0]["event"]:
                    if evt["subtype"] in exist_keys:
                        flag = True

            sample_data += cur_data
            for evt in sample_data[-1]["event"]:
                if evt["subtype"] not in exist_keys:
                    exist_keys.append(evt["subtype"])
            # exist_keys.append(select_key)

            cur_keys = list(set(single_type2example.keys()) - set(exist_keys))
            select_keys = random.sample(cur_keys, 2)
            for select_key in select_keys:
                sample_data += random.sample(single_type2example[select_key], 1)
            exist_keys += select_keys
            
            print(len(exist_keys), exist_keys)
            sample_with_argument.append(sample_data)
        
        res_sample_data = []
        for i in range(fold):
            new_list = sample_with_argument[i][2:] + sample_with_argument[i][1:2] + sample_with_argument[i][0:1]
            res_sample_data.append(new_list)

        with open(output_file_name_sample, "w", encoding="utf-8") as fw_sample:
            # print(len(res_sample_data))
            json.dump(res_sample_data, fw_sample, indent=4, ensure_ascii=False)

        # joint
        res_sample_data = []
        for i in range(fold):
            new_list = sample_with_argument[i][2:] + sample_with_argument[i][1:2] + sample_with_argument[i][0:1] + [sample_no_event[i]]
            res_sample_data.append(new_list)

        with open(output_file_name_sample_1, "w", encoding="utf-8") as fw_sample:
            # print(len(res_sample_data))
            json.dump(res_sample_data, fw_sample, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    
    # trigger
    ee_data_sample_trigger("ee/ace05", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)
    # ee_data_sample_trigger("ee/ace05+", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)
    # ee_data_sample_trigger("ee/casie", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)
    # ee_data_sample_trigger("ee/commodity_news_EE", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)

    # argument
    ee_data_sample_argument("ee/ace05", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)
    # ee_data_sample_argument("ee/ace05+", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)
    # ee_data_sample_argument("ee/casie", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)
    # ee_data_sample_argument("ee/commodity_news_EE", "train.json", "test.json", "types.json", max_l=40, k=5, fold=5)

