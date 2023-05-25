import os
import json
import random

output_dir = "./data"


def ner_data_sample(dataset, input_file, test_file, output_file, type_file, max_l=50, k=5, fold=5, diversity=4):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name = os.path.join(output_path, output_file)
    test_file_name = os.path.join(output_path, test_file)
    type_file_name = os.path.join(output_path, type_file)
    
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft, \
                open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        types_list = [v["verbose"].lower() for k, v in types["entities"].items()]

        ## 去重
        uni_data = []
        seq_list = []
        num_lap = 0
        for example in data:
            if example["seq"] not in seq_list:
                seq_list.append(example["seq"])
                uni_data.append(example)
            else:
                num_lap += 1

        data = uni_data
        print(len(data), num_lap)

        ## 统计 test file
        test_data = [item["seq"] for item in json.load(ft)]
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)

        print(num_test_all/len(test_data))
        
        ## 统计 train file
        num = 0.0
        num_in_test = 0
        data_no_in_test = []
        for example in data:  
            if example["seq"] not in test_data:
                num += len(example["seq"])
                data_no_in_test.append(example)
            else:
                num_in_test += 1

        print(num/len(data_no_in_test), num_in_test)

        data_no_in_test_max_l = []
        for example in data_no_in_test:
            tokens = example["seq"].split(" ")
            if len(tokens) <= max_l and len(tokens) >= 5:
                data_no_in_test_max_l.append(example)

        print("words less \"max_l\":", len(data_no_in_test_max_l), len(data_no_in_test))

        ## no_term && with_term
        data_no_entity = []
        data_with_entity = []
        one_entity_one_type = []
        multi_entity_one_type = []
        multi_entity_multi_type = []
        type2example = {}
        type2multi_entity_example = {}

        for example in data_no_in_test_max_l:
            ents = example["entities"]
            if len(ents) > 0:
                data_with_entity.append(example)
                if len(ents) == 1:
                    one_entity_one_type.append(example)
                    e_type = ents[0]["e_type_verbose"].lower()
                    if e_type not in type2example:
                        type2example[e_type] = [example]
                    else:
                        type2example[e_type].append(example)
                else:
                    ent_type_list = []
                    for ent in ents:
                        if ent["e_type_verbose"].lower() not in ent_type_list:
                            ent_type_list.append(ent["e_type_verbose"].lower())
                    if len(ent_type_list) == 1:
                        multi_entity_one_type.append(example)
                        if ent_type_list[0] not in type2multi_entity_example:
                            type2multi_entity_example[ent_type_list[0]] = [example]
                        else:
                            type2multi_entity_example[ent_type_list[0]].append(example)
                    else:
                        if len(ent_type_list) == len(ents):
                            multi_entity_multi_type.append(example)
            else:
                data_no_entity.append(example)
        
        print(len(data_with_entity), len(data_no_entity))
        print(len(one_entity_one_type), len(multi_entity_one_type), len(multi_entity_multi_type))

        with open(os.path.join(output_path, "train_no_entity.json"), 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(data_no_entity, indent=4, ensure_ascii=False))
            print(len(data_no_entity))

        ## sample no entity
        sample_no_entity = random.sample(data_no_entity, 1*fold)
        print(len(sample_no_entity))

        ## sample multi entity multi type
        while True:
            sample_m_e_m_t = random.sample(multi_entity_multi_type, 2*fold)
            flag = False
            for i in range(fold):
                first = sample_m_e_m_t[i*2]
                first_type = []
                for example in first["entities"]:
                    if example["e_type_verbose"].lower() not in first_type:
                        first_type.append(example["e_type_verbose"].lower())

                second = sample_m_e_m_t[i*2+1]
                second_type = []
                for example in second["entities"]:
                    if example["e_type_verbose"].lower() not in second_type:
                        second_type.append(example["e_type_verbose"].lower())

                if len(set(first_type+second_type)) < diversity:
                    flag = True
            if not flag:
                break
        print(len(sample_m_e_m_t))

        exist_types_list = []
        for i in range(fold):
            first = sample_m_e_m_t[i*2]
            first_type = []
            for example in first["entities"]:
                if example["e_type_verbose"].lower() not in first_type:
                    first_type.append(example["e_type_verbose"].lower())

            second = sample_m_e_m_t[i*2+1]
            second_type = []
            for example in second["entities"]:
                if example["e_type_verbose"].lower() not in second_type:
                    second_type.append(example["e_type_verbose"].lower())

            exist_types_list.append(list(set(first_type+second_type)))

        # sample multi entity one type
        sample_m_e_o_t = []
        for i in range(fold):
            remain_types = list(set(list(type2multi_entity_example.keys())) - set(exist_types_list[i]))
            if len(remain_types) > 0: 
                select_type = random.sample(remain_types, 1)[0]
                exist_types_list[i].append(select_type)
            else:
                select_type = list(type2multi_entity_example.keys())[0]
            
            sample_m_e_o_t.append(random.sample(type2multi_entity_example[select_type], 1)[0])
        print(len(sample_m_e_o_t))

        # sample one entity 
        sample_one_entity = []
        for i in range(fold):
            remain_types = list(set(list(type2example.keys())) - set(exist_types_list[i]))
            if len(remain_types) > 0: 
                select_type = random.sample(remain_types, 1)[0]
            else:
                select_type = list(type2example.keys())[0]

            sample_one_entity.append(random.sample(type2example[select_type], 1)[0])
        print(len(sample_one_entity))

        # get prompt
        prompt_list = []
        for i in range(fold):
            tmp_prompt_list = []

            example = sample_one_entity[i]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_m_e_o_t[i]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_m_e_m_t[i*2]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_m_e_m_t[i*2+1]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_no_entity[i]
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], "[]")
            tmp_prompt_list.append(prompt)

            prompt_list.append("\n".join(tmp_prompt_list))

        with open(output_file_name, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_list, indent=4, ensure_ascii=False))
        print("finish!!")
        print()


def ner_data_nested_sample(dataset, input_file, test_file, output_file, type_file, max_l=50, k=5, fold=5, diversity=4):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name = os.path.join(output_path, output_file)
    test_file_name = os.path.join(output_path, test_file)
    type_file_name = os.path.join(output_path, type_file)
    
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft, \
                open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        types_list = [v["verbose"].lower() for k, v in types["entities"].items()]

        ## 去重
        uni_data = []
        seq_list = []
        num_lap = 0
        for example in data:
            if example["seq"] not in seq_list:
                seq_list.append(example["seq"])
                uni_data.append(example)
            else:
                num_lap += 1

        data = uni_data
        print(len(data), num_lap)

        ## 统计 test file
        test_data = [item["seq"] for item in json.load(ft)]
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)

        print(num_test_all/len(test_data))
        
        ## 统计 train file
        num = 0.0
        num_in_test = 0
        data_no_in_test = []
        for example in data:  
            if example["seq"] not in test_data:
                num += len(example["seq"])
                data_no_in_test.append(example)
            else:
                num_in_test += 1

        print(num/len(data_no_in_test), num_in_test)

        data_no_in_test_max_l = []
        for example in data_no_in_test:
            tokens = example["seq"].split(" ")
            if len(tokens) <= max_l and len(tokens) >= 5:
                data_no_in_test_max_l.append(example)

        print("words less \"max_l\":", len(data_no_in_test_max_l), len(data_no_in_test))

        ## no_term && with_term
        data_no_entity = []
        data_flat_entity = []
        data_nested_entity = []
        data_with_entity = []

        for example in data_no_in_test_max_l:
            ents = example["entities"]
            if len(ents) > 0:
                data_with_entity.append(example)
                if example["mode"] == "nested":
                    if len(example["entities"]) <= 5:
                        data_nested_entity.append(example)
                else:
                    data_flat_entity.append(example)
                
            else:
                data_no_entity.append(example)
        
        print(len(data_with_entity), len(data_no_entity))
        print(len(data_nested_entity), len(data_flat_entity))

        with open(os.path.join(output_path, "train_no_entity.json"), 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(data_no_entity, indent=4, ensure_ascii=False))
            print(len(data_no_entity))

        data_nested_one_type = []
        nested_one_type_2_example = {}
        data_nested_multi_type = []

        for example in data_nested_entity:
            ent_type_list = []
            for ent in example["entities"]:
                if ent["e_type_verbose"].lower() not in ent_type_list:
                    ent_type_list.append(ent["e_type_verbose"].lower())
            if len(ent_type_list) > 1:
                data_nested_multi_type.append(example)
            else:
                if ent_type_list[0] not in nested_one_type_2_example:
                    nested_one_type_2_example[ent_type_list[0]] = [example]
                else:
                    nested_one_type_2_example[ent_type_list[0]].append(example)
                data_nested_one_type.append(example)

        print(len(data_nested_one_type), len(data_nested_multi_type))

        data_flat_multi_type = []
        data_flat_one_type = []
        flat_type_2_multi_type_example = {}
        flat_type_2_one_type_example = {}
        for example in data_flat_entity:
            ent_type_list = []
            for ent in example["entities"]:
                if ent["e_type_verbose"].lower() not in ent_type_list:
                    ent_type_list.append(ent["e_type_verbose"].lower())
            if len(ent_type_list) > 1:
                data_flat_multi_type.append(example)
                for t in ent_type_list:
                    if t not in flat_type_2_multi_type_example:
                        flat_type_2_multi_type_example[t] = [example]
                    else:
                        flat_type_2_multi_type_example[t].append(example)
            else:
                data_flat_one_type.append(example)
                if ent_type_list[0] not in flat_type_2_one_type_example:
                    flat_type_2_one_type_example[ent_type_list[0]] = [example]
                else:
                    flat_type_2_one_type_example[ent_type_list[0]].append(example)

        print(len(data_flat_one_type), len(data_flat_multi_type))

        ## sample no entity
        sample_no_entity = random.sample(data_no_entity, 1*fold)
        print(len(sample_no_entity))

        ## sample nested multi_type
        sample_nested_multi = random.sample(data_nested_multi_type, 1*fold)
        exists_types = []
        for i in range(fold):
            tmp_type_list = []
            for ent in sample_nested_multi[i]["entities"]:
                if ent["e_type_verbose"].lower() not in tmp_type_list:
                    tmp_type_list.append(ent["e_type_verbose"].lower())
            exists_types.append(tmp_type_list)
        print(len(sample_nested_multi))

        ## sample nested one type
        sample_nested_one = []
        for i in range(fold):
            remain_types = list(set(list(nested_one_type_2_example.keys())) - set(exists_types[i]))
            if len(remain_types) > 0:
                select_type = random.sample(remain_types, 1)[0]
                exists_types[i].append(select_type)
            else:
                select_type = list(nested_one_type_2_example.keys())[0]
            
            sample_nested_one.append(
               random.sample(nested_one_type_2_example[select_type], 1)[0]
            )
        print(len(sample_nested_one))

        # sample flat multi_type
        sample_flat_multi = []
        for i in range(fold):
            remain_types = list(set(list(flat_type_2_multi_type_example.keys())) - set(exists_types[i]))
            if len(remain_types) > 0:
                select_type = random.sample(remain_types, 1)[0]
                exists_types[i].append(select_type)
            else:
                select_type = list(flat_type_2_multi_type_example.keys())[0]
            
            sample_flat_multi.append(
               random.sample(flat_type_2_multi_type_example[select_type], 1)[0]
            )
        print(len(sample_flat_multi))

        ## sample flat one_type
        sample_flat_one = []
        for i in range(fold):
            remain_types = list(set(list(flat_type_2_one_type_example.keys())) - set(exists_types[i]))
            if len(remain_types) > 0:
                select_type = random.sample(remain_types, 1)[0]
                exists_types[i].append(select_type)
            else:
                select_type = list(flat_type_2_one_type_example.keys())[0]
            
            sample_flat_one.append(
               random.sample(flat_type_2_one_type_example[select_type], 1)[0]
            )
        print(len(sample_flat_one))

        # get prompt
        prompt_list = []
        for i in range(fold):
            tmp_prompt_list = []

            example = sample_flat_one[i]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_flat_multi[i]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_nested_one[i]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_nested_multi[i]
            ent_list = []
            for ent in example["entities"]:
                ent_list.append([ent["e_type_verbose"].lower(), ent["e_name"]])
            ent_str = ", ".join([json.dumps(item) for item in ent_list])
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], ent_str)
            tmp_prompt_list.append(prompt)

            example = sample_no_entity[i]
            prompt = 'Sentence:\n"{}"\nAnswer:\n{}'.format(example["seq"], "[]")
            tmp_prompt_list.append(prompt)

            prompt_list.append("\n".join(tmp_prompt_list))

        with open(output_file_name, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_list, indent=4, ensure_ascii=False))
        print("finish!!")
        print()


if __name__ == "__main__":
    
    ner_data_sample("ner/conll03", "ner_train.json", "ner_test.json", "new_prompt_icl.json", "types.json", max_l=30, k=5, fold=5, diversity=3)
    ner_data_sample("ner/fewnerd", "ner_train.json", "ner_test_3k.json", "new_prompt_icl.json", "types.json", max_l=30, k=5, fold=5, diversity=6)

    ner_data_nested_sample("ner/ace2004", "ner_train.json", "ner_test.json", "new_prompt_icl.json", "types.json", max_l=30, k=5, fold=5, diversity=3)
    ner_data_nested_sample("ner/ace2005", "ner_train.json", "ner_test.json", "new_prompt_icl.json", "types.json", max_l=30, k=5, fold=5, diversity=3)
    ner_data_nested_sample("ner/genia", "ner_train.json", "ner_test.json", "new_prompt_icl.json", "types.json", max_l=30, k=5, fold=5, diversity=3)
    
