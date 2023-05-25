import os
import json
import random
import ast

output_dir = "./data"


def re_data_sample(dataset, input_file, test_file, type_file, max_l=50, k=5, fold=5, diversity=4):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name_triplet = os.path.join(output_path, "new_prompt_icl_triplet.json")
    output_file_name_sample = os.path.join(output_path, "new_data_sample.json")
    output_file_name_rc = os.path.join(output_path, "new_prompt_icl_rc.json")
    test_file_name = os.path.join(output_path, test_file)
    type_file_name = os.path.join(output_path, type_file)
    
    print("Load file: {}".format(in_file_name))
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft, \
                open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        types_dict = types["relation"]
        ent_type_dict = types["entity"]

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
        # print(len(data), num_lap)

        ## 统计 test file
        test_data = [item["seq"] for item in json.load(ft)]
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)

        # print(num_test_all/len(test_data))
        
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

        # print(num/len(data_no_in_test), num_in_test)

        data_no_in_test_max_l = []
        for example in data_no_in_test:
            tokens = example["seq"].split(" ")
            if len(tokens) <= max_l and len(tokens) >= 5:
                data_no_in_test_max_l.append(example)

        print("words less \"max_l\":", len(data_no_in_test_max_l), len(data_no_in_test))

        ## no_term && with_term
        data_no_relation = []
        data_with_relation = []

        for example in data_no_in_test_max_l:
            rels = example["relations"]

            if len(rels) == 1 and types_dict[rels[0]["r"]].lower() == "no relation":
                data_no_relation.append(example)
            else:
                data_with_relation.append(example)

        print("no rel:", len(data_no_relation), len(data_with_relation))

        with open(os.path.join(output_path, "train_no_relation.json"), 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(data_no_relation, indent=4, ensure_ascii=False))
            print(len(data_no_relation))

        # multi-label pairs
        multi_label_pairs = []
        single_label_pairs = []
        for example in data_with_relation:
            pair2rel = {}
            flag = False
            for rel in example["relations"]:
                h = rel["h_name"]
                t = rel["t_name"]
                r = rel["r"]
                if (h, t) not in pair2rel:
                    pair2rel[(h, t)] = [r]
                else:
                    pair2rel[(h, t)].append(r)
            for p in pair2rel:
                if len(pair2rel[p]) > 1:
                    flag = True
                    break
            if flag:
                multi_label_pairs.append(example)
            else:
                single_label_pairs.append(example)
        print(len(multi_label_pairs), len(single_label_pairs))

        rel2example = {}
        one_rel = []
        multi_rel_one_type = []
        multi_rel_multi_type = []
        for example in single_label_pairs:
            if len(example["relations"]) == 1:
                one_rel.append(example)
                if example["relations"][0]["r"] not in rel2example:
                    rel2example[example["relations"][0]["r"]] = [example]
                else:
                    rel2example[example["relations"][0]["r"]].append(example)
            else:
                type_list = []
                for rel in example["relations"]:
                    if rel["r"] not in type_list:
                        type_list.append(rel["r"])
                if len(type_list) == 1:
                    multi_rel_one_type.append(example)
                else:
                    multi_rel_multi_type.append(example)

                if len(data_no_relation) == 0:
                    for rr in type_list:
                        if rr not in rel2example:
                            rel2example[rr] = [example]
                        else:
                            rel2example[rr].append(example)

        # print(len(one_rel), len(multi_rel_one_type), len(multi_rel_multi_type))

        ## sample
        if len(data_no_relation) == 0:
            type_list = list(rel2example.keys())
            sample_with_rel = []
            for i in range(fold):
                tmp_list = []
                res_type_list = []

                if len(type_list) < k:
                    res_type_list += type_list
                    for _ in range(k-len(type_list)):
                        res_type_list.append(random.sample(type_list, 1)[0])
                elif len(type_list) == k:
                    res_type_list += type_list
                else:
                    res_type_list += random.sample(type_list, k)

                print(len(type_list))
                print(len(res_type_list), res_type_list)
                uni_res_type_list = []
                for r_t in res_type_list:
                    if r_t not in uni_res_type_list:
                        uni_res_type_list.append(r_t)
                print(len(uni_res_type_list), uni_res_type_list)

                for type in res_type_list:
                    tmp_list.append(random.sample(rel2example[type], 1)[0])
                sample_with_rel.append(tmp_list)
        else:
            type_list = list(rel2example.keys())
            sample_no_rel = random.sample(data_no_relation, fold)
            sample_with_rel = []

            for i in range(fold):
                tmp_list = []
                res_type_list = []
                # print(len(type_list))
                if len(type_list) < k-1:
                    res_type_list += type_list
                    for _ in range(k-1-len(type_list)):
                        res_type_list.append(random.sample(type_list, 1)[0])
                elif len(type_list) == k-1:
                    res_type_list += type_list
                else:
                    res_type_list += random.sample(type_list, k-1)

                print(len(type_list))
                print(len(res_type_list), res_type_list)
                uni_res_type_list = []
                for r_t in res_type_list:
                    if r_t not in uni_res_type_list:
                        uni_res_type_list.append(r_t)
                print(len(uni_res_type_list), uni_res_type_list)

                for type in res_type_list:
                    tmp_list.append(random.sample(rel2example[type], 1)[0])
                sample_with_rel.append(tmp_list)
            
            for i in range(len(sample_with_rel)):
                sample_with_rel[i].append(sample_no_rel[i])

        with open(output_file_name_sample, "w", encoding="utf-8") as fw_sample:
            print(len(sample_with_rel))
            json.dump(sample_with_rel, fw_sample, indent=4, ensure_ascii=False)

        prompt_triplet = []
        prompt_rc = []
        for i in range(fold):
            tmp = []
            tmp_rc = []
            for example in sample_with_rel[i]:
                rel_list = []
                for rel in example["relations"]:
                    if types_dict[rel["r"]].lower() != "no relation":
                        rel_list.append([rel["h_name"], types_dict[rel["r"]], rel["t_name"]])
                    else:
                        rel_list.append([])
                triplet_str = ", ".join([json.dumps(item) for item in rel_list])
                tmp_prompt = 'Given text:\n"{}"\nAnswer:\n{}'.format(example["seq"], triplet_str)
                tmp.append(tmp_prompt)

                ## 
                ht2rels = {}
                for rel in example["relations"]:
                    h = rel["h_name"]
                    t = rel["t_name"]
                    r = types_dict[rel["r"]]
                    if (h, t) not in ht2rels:
                        ht2rels[(h, t)] = [r]
                    else:
                        ht2rels[(h, t)].append(r)

                pair_str_list = []
                answer_str_list = []
                for ent in example["entities"]:
                    for ent_1 in example["entities"]:
                        if ent != ent_1:
                            h = ent["name"]
                            h_type = ent["type"]
                            if h_type != "":
                                h_type = ent_type_dict[h_type]

                            t = ent_1["name"]
                            t_type = ent_1["type"]
                            if t_type != "":
                                t_type = ent_type_dict[t_type]
                            
                            pair_tuple = (h, h_type, t, t_type)

                            pair_str_list.append(str(pair_tuple))

                            if (h, t) not in ht2rels:
                                ht_rel = ["no relation"]
                            else:
                                ht_rel = ht2rels[(h, t)]
                            ans = '{}:{}'.format(str(pair_tuple), json.dumps(ht_rel))

                            answer_str_list.append(ans)

                pairs_str = "\n".join(pair_str_list)
                answer_str = "\n".join(answer_str_list)

                tmp_prompt_rc = 'Given text:\n"{}"\nEntity pairs:\n{}\nAnswer:\n{}'.format(example["seq"], pairs_str, answer_str)
                tmp_rc.append(tmp_prompt_rc)
        
            prompt_triplet.append("\n".join(tmp))
            prompt_rc.append("\n".join(tmp_rc))

        
        with open(output_file_name_triplet, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_triplet, indent=4, ensure_ascii=False))
        with open(output_file_name_rc, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_rc, indent=4, ensure_ascii=False))
        print("finish!!")
        print()


def doc_re_data_sample(dataset, input_file, test_file, type_file, max_l=50, k=5, fold=5):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name_triplet = os.path.join(output_path, "new_prompt_icl_triplet.json")
    output_file_name_sample = os.path.join(output_path, "new_data_sample.json")
    output_file_name_rc = os.path.join(output_path, "new_prompt_icl_rc.json")
    test_file_name = os.path.join(output_path, test_file)
    type_file_name = os.path.join(output_path, type_file)
    
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft, \
                open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        types_dict = types["relation"]
        ent_type_dict = types["entity"]

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
        # print(len(data), num_lap)

        ## 统计 test file
        test_data = [item["seq"] for item in json.load(ft)]
        max_len = max([len(item.split(" ")) for item in test_data])
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)
        # print(max_len)
        # print(num_test_all/len(test_data))
        
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

        # print(num/len(data_no_in_test), num_in_test)

        data_no_in_test_max_l = []
        for example in data_no_in_test:
            tokens = example["seq"].split(" ")
            if len(tokens) <= max_l and len(tokens) >= 5:
                data_no_in_test_max_l.append(example)

        print("words less \"max_l\":", len(data_no_in_test_max_l), len(data_no_in_test))

        ## no_term && with_term
        data_no_relation = []
        data_with_relation = []

        for example in data_no_in_test_max_l:
            rels = example["relations"]

            if len(rels) == 1 and types_dict[rels[0]["r"]].lower() == "no relation":
                data_no_relation.append(example)
            else:
                data_with_relation.append(example)

        # print(len(data_no_relation), len(data_with_relation))

        # multi-label pairs
        multi_label_pairs = []
        single_label_pairs = []
        for example in data_with_relation:
            pair2rel = {}
            flag = False
            for rel in example["relations"]:
                h = rel["h_name"]
                t = rel["t_name"]
                r = rel["r"]
                if (h, t) not in pair2rel:
                    pair2rel[(h, t)] = [r]
                else:
                    pair2rel[(h, t)].append(r)
            for p in pair2rel:
                if len(pair2rel[p]) > 1:
                    flag = True
                    break
            if flag:
                multi_label_pairs.append(example)
            else:
                single_label_pairs.append(example)
        print(len(multi_label_pairs), len(single_label_pairs))
        
        if "docred" in dataset or "dwie" in dataset:
            print(len(multi_label_pairs))
            data_sample = random.sample(multi_label_pairs, k*fold)
        else:
            data_multi_triplet = []
            for example in data_with_relation:
                num_triplet = 0
                for rel in example["relations"]:
                    if types_dict[rel["r"]].lower() != "no relation":
                        num_triplet += 1

                if num_triplet > 1:
                    data_multi_triplet.append(example)
            print(len(data_with_relation), len(data_multi_triplet))
            data_sample = random.sample(data_multi_triplet, k*fold)

        with open(output_file_name_sample, "w", encoding="utf-8") as fw_sample:
            print(len(data_sample))
            json.dump(data_sample, fw_sample, indent=4, ensure_ascii=False)

        prompt_triplet = []
        prompt_rc = []
        for i in range(fold):
            tmp = []
            tmp_rc = []
            for example in data_sample[i*k: (i+1)*k]:
                rel_list = []
                for rel in example["relations"]:
                    if types_dict[rel["r"]].lower() != "no relation":
                        rel_list.append([rel["h_name"], types_dict[rel["r"]], rel["t_name"]])
                triplet_str = ", ".join([json.dumps(item) for item in rel_list])
                tmp_prompt = 'Given text:\n"{}"\nAnswer:\n{}'.format(example["seq"], triplet_str)
                tmp.append(tmp_prompt)

                ## 
                ht2rels = {}
                for rel in example["relations"]:
                    h = rel["h_name"]
                    t = rel["t_name"]
                    r = types_dict[rel["r"]]
                    if (h, t) not in ht2rels:
                        ht2rels[(h, t)] = [r]
                    else:
                        ht2rels[(h, t)].append(r)

                pair_str_list = []
                answer_str_list = []
                for ent in example["entities"]:
                    for ent_1 in example["entities"]:
                        if ent != ent_1:
                            h = ent["name"]
                            h_type = ent["type"]
                            if h_type != "":
                                h_type = ent_type_dict[h_type]

                            t = ent_1["name"]
                            t_type = ent_1["type"]
                            if t_type != "":
                                t_type = ent_type_dict[t_type]
                            
                            pair_tuple = (h, h_type, t, t_type)

                            pair_str_list.append(str(pair_tuple))

                            if (h, t) not in ht2rels:
                                ht_rel = ["no relation"]
                            else:
                                ht_rel = ht2rels[(h, t)]
                            ans = '{}:{}'.format(str(pair_tuple), json.dumps(ht_rel))

                            answer_str_list.append(ans)

                pairs_str = "\n".join(pair_str_list)
                answer_str = "\n".join(answer_str_list)

                tmp_prompt_rc = 'Given text:\n"{}"\nEntity pairs:\n{}\nAnswer:\n{}'.format(example["seq"], pairs_str, answer_str)
                tmp_rc.append(tmp_prompt_rc)
        
            prompt_triplet.append("\n".join(tmp))
            prompt_rc.append("\n".join(tmp_rc))

        
        with open(output_file_name_triplet, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_triplet, indent=4, ensure_ascii=False))
        with open(output_file_name_rc, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_rc, indent=4, ensure_ascii=False))
        print("finish!!")
        print()


def get_rc_icl(dataset, input_file, type_file, output_file):
    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name = os.path.join(output_path, output_file)
    type_file_name = os.path.join(output_path, type_file)
    
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        types_dict = types["relation"]
        r_types_list = list(types_dict.values())
        e_types_dict = types["entity"]

        prompt_rc = []
        for example_list in data:
            tmp_rc = []
            uni_rel = []
            for example in example_list:
                pair_str_list = []
                answer_str_list = []
                ht2rels = {}
                for r_dic in example["relations"]:
                    # if types_dict[r_dic["r"]].lower() != "no relation":
                    h_name = r_dic["h_name"]
                    t_name = r_dic["t_name"]

                    r = types_dict[r_dic["r"]]
                    if (h_name, t_name) not in ht2rels:
                        ht2rels[(h_name, t_name)] = [r]
                    else:
                        ht2rels[(h_name, t_name)].append(r)
                    if r not in uni_rel:
                        uni_rel.append(r)

                for r_dic in example["relations"]:
                    # if types_dict[r_dic["r"]].lower() != "no relation":
                    h = r_dic["h"]
                    h_name = r_dic["h_name"]
                    h_type = example["entities"][h]["type"]
                    if h_type != "":
                        h_type = e_types_dict[h_type]
                    t = r_dic["t"]
                    t_name = r_dic["t_name"]
                    t_type = example["entities"][t]["type"]
                    if t_type != "":
                        t_type = e_types_dict[t_type]

                    if len(e_types_dict) != 0:
                        pair_str_list.append('("{}", "{}", "{}", "{}")'.format(h_name, h_type, t_name, t_type))
                        pair_str_list.append('("{}", "{}", "{}", "{}")'.format(t_name, t_type, h_name, h_type))
                        
                        answer_str_list.append('("{}", "{}", "{}", "{}"): {}'.format(h_name, h_type, t_name, t_type, json.dumps(ht2rels[(h_name, t_name)])))
                        answer_str_list.append('("{}", "{}", "{}", "{}"): {}'.format(t_name, t_type, h_name, h_type, json.dumps([r_types_list[-1]])))
                    else:
                        pair_str_list.append('("{}", "{}")'.format(h_name, t_name))
                        pair_str_list.append('("{}", "{}")'.format(t_name, h_name))
                        
                        answer_str_list.append('("{}", "{}"): {}'.format(h_name, t_name, json.dumps(ht2rels[(h_name, t_name)])))
                        answer_str_list.append('("{}", "{}"): {}'.format(t_name, h_name, json.dumps([r_types_list[-1]])))


                if len(e_types_dict) != 0:
                    pair_str_list = sorted(pair_str_list, key=lambda a: ast.literal_eval(a)[0] + "#" + ast.literal_eval(a)[2])
                    answer_str_list = sorted(answer_str_list, key=lambda a: ast.literal_eval(a.split("):")[0]+")")[0] + "#" + ast.literal_eval(a.split("):")[0]+")")[2])
                else:
                    pair_str_list = sorted(pair_str_list, key=lambda a: ast.literal_eval(a)[0] + "#" + ast.literal_eval(a)[1])
                    answer_str_list = sorted(answer_str_list, key=lambda a: ast.literal_eval(a.split("):")[0]+")")[0] + "#" + ast.literal_eval(a.split("):")[0]+")")[1])

                pairs_str = "\n".join(pair_str_list)
                answer_str = "\n".join(answer_str_list)

                tmp_prompt_rc = 'Given text:\n"{}"\nEntity pairs:\n{}\nAnswer:\n{}'.format(example["seq"], pairs_str, answer_str)
                tmp_rc.append(tmp_prompt_rc)
            print(len(uni_rel))
            prompt_rc.append("\n".join(tmp_rc))

        # for pp in prompt_rc:
        #     print(pp)
        #     print()

        with open(output_file_name, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_rc, indent=4, ensure_ascii=False))
        print("finish!!")


def doc_get_rc_icl(dataset, input_file, type_file, output_file, k=5, fold=5):
    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_path, input_file)
    output_file_name = os.path.join(output_path, output_file)
    type_file_name = os.path.join(output_path, type_file)
    
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(type_file_name, "r", encoding="utf-8") as fr_type:
        data = json.load(f)
        types = json.load(fr_type)
        types_dict = types["relation"]
        r_types_list = list(types_dict.values())
        e_types_dict = types["entity"]

        prompt_rc = []
        for i in range(fold):
            tmp_rc = []
            for example in data[i*k: (i+1)*k]:
                pair_str_list = []
                answer_str_list = []
                ht2rels = {}
                uni_rel = []
                num_triplet = 0
                rel2triplet = {}
                for r_dic in example["relations"]:
                    if types_dict[r_dic["r"]].lower() != "no relation":
                        h_name = r_dic["h_name"]
                        t_name = r_dic["t_name"]

                        r = types_dict[r_dic["r"]]
                        if (h_name, t_name) not in ht2rels:
                            ht2rels[(h_name, t_name)] = [r]
                        else:
                            ht2rels[(h_name, t_name)].append(r)
                        
                        if r not in uni_rel:
                            uni_rel.append(r)
                        num_triplet += 1

                        if r not in rel2triplet:
                            rel2triplet[r] = [[h_name, t_name, r]]
                        else:
                            rel2triplet[r].append([h_name, t_name, r])

                # if "docred" in dataset or "dwie" in dataset:
                #     k_list = list(rel2triplet.keys())
                #     if len(k_list) >= 5:
                #         k_list = random.sample(k_list, 5)
                    

                # else:
                for r_dic in example["relations"]:
                    if types_dict[r_dic["r"]].lower() != "no relation":
                        h = r_dic["h"]
                        h_name = r_dic["h_name"]
                        h_type = example["entities"][h]["type"]
                        if h_type != "":
                            h_type = e_types_dict[h_type]
                        t = r_dic["t"]
                        t_name = r_dic["t_name"]
                        t_type = example["entities"][t]["type"]
                        if t_type != "":
                            t_type = e_types_dict[t_type]

                        if len(e_types_dict) != 0:
                            pair_str_list.append('("{}", "{}", "{}", "{}")'.format(h_name, h_type, t_name, t_type))
                            pair_str_list.append('("{}", "{}", "{}", "{}")'.format(t_name, t_type, h_name, h_type))
                            
                            answer_str_list.append('("{}", "{}", "{}", "{}"): {}'.format(h_name, h_type, t_name, t_type, json.dumps(ht2rels[(h_name, t_name)])))
                            answer_str_list.append('("{}", "{}", "{}", "{}"): {}'.format(t_name, t_type, h_name, h_type, json.dumps([r_types_list[-1]])))
                        else:
                            pair_str_list.append('("{}", "{}")'.format(h_name, t_name))
                            pair_str_list.append('("{}", "{}")'.format(t_name, h_name))
                            
                            answer_str_list.append('("{}", "{}"): {}'.format(h_name, t_name, json.dumps(ht2rels[(h_name, t_name)])))
                            answer_str_list.append('("{}", "{}"): {}'.format(t_name, h_name, json.dumps([r_types_list[-1]])))

                if len(e_types_dict) != 0:
                    pair_str_list = sorted(pair_str_list, key=lambda a: ast.literal_eval(a)[0] + "#" + ast.literal_eval(a)[2])
                    answer_str_list = sorted(answer_str_list, key=lambda a: ast.literal_eval(a.split("):")[0]+")")[0] + "#" + ast.literal_eval(a.split("):")[0]+")")[2])
                else:
                    pair_str_list = sorted(pair_str_list, key=lambda a: ast.literal_eval(a)[0] + "#" + ast.literal_eval(a)[1])
                    answer_str_list = sorted(answer_str_list, key=lambda a: ast.literal_eval(a.split("):")[0]+")")[0] + "#" + ast.literal_eval(a.split("):")[0]+")")[1])

                pairs_str = "\n".join(pair_str_list)
                answer_str = "\n".join(answer_str_list)

                tmp_prompt_rc = 'Given text:\n"{}"\nEntity pairs:\n{}\nAnswer:\n{}'.format(example["seq"], pairs_str, answer_str)
                tmp_rc.append(tmp_prompt_rc)
            print(len(uni_rel), num_triplet)
            prompt_rc.append("\n".join(tmp_rc))

        # for pp in prompt_rc:
        #     print(pp)
        #     print()

        with open(output_file_name, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(prompt_rc, indent=4, ensure_ascii=False))
        print("finish!!")


if __name__ == "__main__":
    
    re_data_sample("re/sent/conll04", "train.json", "test.json", "types.json", max_l=25, k=5, fold=5, diversity=3)
    re_data_sample("re/sent/nyt-multi", "train.json", "test_3k.json", "types.json", max_l=25, k=5, fold=5, diversity=3)
    re_data_sample("re/sent/tacred", "train.json", "test_3k.json", "types.json", max_l=25, k=5, fold=5, diversity=3)
    re_data_sample("re/sent/re-tacred", "train.json", "test_3k.json", "types.json", max_l=25, k=5, fold=5, diversity=3)
    re_data_sample("re/sent/semeval2010", "train.json", "test.json", "types.json", max_l=25, k=5, fold=5, diversity=3)
    re_data_sample("re/sent/cpr", "train.json", "test_3k.json", "types.json", max_l=25, k=5, fold=5, diversity=3)
    re_data_sample("re/sent/pgr", "train.json", "test.json", "types.json", max_l=25, k=5, fold=5, diversity=3)

    doc_re_data_sample("re/doc/docred", "train.json", "dev.json", "types.json", max_l=150, k=1, fold=5)
    doc_re_data_sample("re/doc/re-docred", "train.json", "test.json", "types.json", max_l=150, k=1, fold=5)
    doc_re_data_sample("re/doc/dwie", "train.json", "test.json", "types.json", max_l=300, k=1, fold=5)
    doc_re_data_sample("re/doc/cdr", "train.json", "test.json", "types.json", max_l=150, k=1, fold=5)
    doc_re_data_sample("re/doc/gda", "train.json", "test.json", "types.json", max_l=150, k=1, fold=5)

    # get_rc_icl("re/sent/conll04", "data_sample.json", "types.json", "prompt_icl_rc.json")
    # get_rc_icl("re/sent/nyt-multi", "data_sample.json", "types.json", "prompt_icl_rc.json")
    # get_rc_icl("re/sent/tacred", "data_sample.json", "types.json", "prompt_icl_rc.json")
    # get_rc_icl("re/sent/re-tacred", "data_sample.json", "types.json", "prompt_icl_rc.json")
    # get_rc_icl("re/sent/semeval2010", "data_sample.json", "types.json", "prompt_icl_rc.json")
    # get_rc_icl("re/sent/cpr", "data_sample.json", "types.json", "prompt_icl_rc.json")
    # get_rc_icl("re/sent/pgr", "data_sample.json", "types.json", "prompt_icl_rc.json")

    # doc_get_rc_icl("re/doc/docred", "data_sample.json", "types.json", "prompt_icl_rc_1.json", k=1, fold=5)
    # doc_get_rc_icl("re/doc/re-docred", "data_sample.json", "types.json", "prompt_icl_rc_1.json", k=1, fold=5)
    # doc_get_rc_icl("re/doc/dwie", "data_sample.json", "types.json", "prompt_icl_rc_1.json", k=1, fold=5)
    # doc_get_rc_icl("re/doc/cdr", "data_sample.json", "types.json", "prompt_icl_rc_1.json", k=1, fold=5)
    # doc_get_rc_icl("re/doc/gda", "data_sample.json", "types.json", "prompt_icl_rc_1.json", k=1, fold=5)

    print("")
