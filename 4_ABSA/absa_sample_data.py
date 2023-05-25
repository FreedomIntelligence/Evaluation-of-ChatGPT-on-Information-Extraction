import os
import json
import random


output_dir = "./data"


def get_prompt_ae_oe(text, example, key="ae"):
    if key == "ae":
        key = "aspects"
    elif key == "oe":
        key = "opinions"

    asp_list = []
    asp_span_list = []  # asp_str 有可能重复，但是 asp_span 不重复
    
    for asp in example[key]:
        asp_str = asp["term"]
        if asp_str != "":
            asp_span = str(asp["span"][0]) + "#" + str(asp["span"][1])
            if asp_span not in asp_span_list:
                asp_span_list.append(asp_span)
                asp_list.append(asp_str)
        else:
            prompt = 'Review:\n"{}"\nAnswer:\n{}'.format(text, "[]")
    prompt = 'Review:\n"{}"\nAnswer:\n{}'.format(text, json.dumps(asp_list))
    return prompt


def get_prompt_alsc_aoe(text, example, key="alsc"):
    target_dict = {}
    prompt_list = []
    for asp in example["aspects"]:
        asp_term = asp["term"]
        if asp_term != "":
            if key == "alsc":
                target_s = asp["polarity"]
                target_dict[asp_term] = target_s
                prompt = 'Review:\n"{}"\nAspect:\n"{}"\nAnswer:\n"{}"\n'.format(text, asp_term, target_s)
                prompt_list.append(prompt.strip("\n"))
            if key == "aoe":
                # print(asp)
                target_opinions = asp["opinions"]
                target_dict[asp_term] = target_opinions
                prompt = 'Review:\n"{}"\nAspect:\n"{}"\nAnswer:\n{}\n'.format(text, asp_term, json.dumps(target_opinions))
                prompt_list.append(prompt.strip("\n"))
        else:
            if key == "alsc":
                prompt = 'Review:\n"{}"\nAspect:\n"{}"\nAnswer:\n"{}"\n'.format(text, "no aspect", "")
                prompt_list.append(prompt.strip("\n"))
            if key == "aoe":
                prompt = 'Review:\n"{}"\nAspect:\n"{}"\nAnswer:\n{}\n'.format(text, "no aspect", json.dumps([]))
                prompt_list.append(prompt.strip("\n"))

    return prompt_list[:3]


def get_prompt_aesc_pair_triplet(text, example, key="aesc"):
    prompt = 'Review:\n"{}"\n'.format(text)
    target_list = []
    for asp in example["aspects"]:
        asp_term = asp["term"]
        if asp_term != "":
            if key == "aesc":
                asp_polar = asp["polarity"]
                target_list.append([asp_term, asp_polar])
            if key == "pair":
                target_list += asp["pairs"]
            if key == "triplet":
                target_list += asp["triplets"]
        else:
            target_list = []

    if target_list != []:
        target_str = ", ".join([json.dumps(item) for item in target_list])
    else:
        target_str = json.dumps(target_list)

    if key == "aesc":
        prompt += 'Answer:\n{}'.format(target_str)
    if key == "pair":
        prompt += 'Answer:\n{}'.format(target_str)
    if key == "triplet":
        prompt += 'Answer:\n{}'.format(target_str)
    return prompt


def absa_data_sample(dataset, input_file, test_file, output_file, max_l=50, k=5, fold=5):

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(output_dir, os.path.join(dataset, input_file))
    test_file_name = os.path.join(output_dir, os.path.join(dataset, test_file))
    
    with open(in_file_name, 'r', encoding='utf-8') as f,\
            open(test_file_name, "r", encoding="utf-8") as ft:
        data = json.load(f)

        ## 去重
        uni_data = []
        num_lap = 0
        for example in data:
            if example not in uni_data:
                uni_data.append(example)
            else:
                num_lap += 1

        data = uni_data

        ## 统计 test file
        test_data = [item["raw_words"] for item in json.load(ft)]
        num_test_all = 0.0
        for test_d in test_data:
            num_test_all += len(test_d)
        
    ## 统计 train file
    num = 0.0
    num_in_test = 0
    data_no_in_test = []
    for example in data:  
        if example["raw_words"] not in test_data:
            num += len(example["raw_words"])
            data_no_in_test.append(example)
        else:
            num_in_test += 1

    # print(num/len(data_no_in_test), num_test_all/len(test_data), num_lap, num_in_test)
    
    ## no_term && with_term
    data_no_term = []
    data_with_term = []
    for example in data_no_in_test:
        if example["aspects"][0]["term"] == "" and example["opinions"][0]["term"] == "":
            data_no_term.append(example)
        else:
            data_with_term.append(example)

    # print(len(data_no_term))
    # term 为 NA 的 example, 均从 wang 中 sample
    print(len(data_no_term))

    if len(data_no_term) > 0:
        
        with open(os.path.join(output_path, "train_no_term.json"), 'w', encoding='utf-8') as fw_no:
            fw_no.write(json.dumps(data_no_term, indent=4, ensure_ascii=False))
    else:
        if "14lap" in dataset:
            fr_no = open("./data/absa/wang/14lap/train_no_term.json", "r", encoding="utf-8")
            data_no_term = json.load(fr_no)
        if "14res" in dataset:
            fr_no = open("./data/absa/wang/14res/train_no_term.json", "r", encoding="utf-8")
            data_no_term = json.load(fr_no)
        if "15res" in dataset or "16res" in dataset:
            fr_no = open("./data/absa/wang/15res/train_no_term.json", "r", encoding="utf-8")
            data_no_term = json.load(fr_no)

    ## sample data (with term)
    data_with_term_max_l = []
    for item in data_with_term:
        if len(item["raw_words"]) <= max_l and item["raw_words"] not in test_data:
            data_with_term_max_l.append(item)

    one_aspect_one_opinion = []
    one_aspect_multi_opinion = []
    multiple_aspects = []
    for item in data_with_term_max_l:
        if len(item["aspects"]) == 1 and item["aspects"][0]["term"] != "" and len(item["opinions"]) == 1 and item["opinions"][0]["term"] != "":
            one_aspect_one_opinion.append(item)
        if len(item["aspects"]) == 1 and item["aspects"][0]["term"] != "" and len(item["opinions"]) > 1:
            one_aspect_multi_opinion.append(item)
        if len(item["aspects"]) > 1:
            multiple_aspects.append(item)
    print(len(one_aspect_one_opinion), len(one_aspect_multi_opinion), len(multiple_aspects))

    if "fan" in dataset:
        num_one_asp_one_opi = 4
        num_one_asp_multi_opi = k - num_one_asp_one_opi
        sample_one_asp_one_opi = random.sample(one_aspect_one_opinion, num_one_asp_one_opi*fold)
        sample_one_asp_multi_opi = random.sample(one_aspect_multi_opinion, num_one_asp_multi_opi*fold)
        print(len(sample_one_asp_one_opi), len(sample_one_asp_multi_opi))
        
    else:
        num_one_asp_one_opi = 2
        num_one_asp_multi_opi = 1
        num_multiple = k - num_one_asp_one_opi - num_one_asp_multi_opi
        sample_one_asp_one_opi = random.sample(one_aspect_one_opinion, num_one_asp_one_opi*fold)
        sample_one_asp_multi_opi = random.sample(one_aspect_multi_opinion, num_one_asp_multi_opi*fold)
        sample_multi_asp = random.sample(multiple_aspects, num_multiple*fold)
        print(len(sample_one_asp_one_opi), len(sample_one_asp_multi_opi), len(sample_multi_asp))

    # sample_data_with_term = random.sample(data_with_term_max_l, k*fold)

    ## sample data (no term)
    data_no_term_max_l = []
    for item in data_no_term:
        if len(item["raw_words"]) <= 15 and item["raw_words"] not in test_data:
            data_no_term_max_l.append(item)
    
    sample_data_no_term = random.sample(data_no_term_max_l, fold)

    sample_data = []
    idx = 0
    if "fan" in dataset:
        while idx < fold:
            sample_data.append(sample_one_asp_one_opi[idx*(num_one_asp_one_opi)])
            sample_data.append(sample_one_asp_one_opi[idx*(num_one_asp_one_opi)+1])
            sample_data.append(sample_one_asp_one_opi[idx*(num_one_asp_one_opi)+2])
            sample_data.append(sample_one_asp_one_opi[idx*(num_one_asp_one_opi)+3])

            sample_data.append(sample_one_asp_multi_opi[idx*(num_one_asp_multi_opi)])

            sample_data.append(sample_data_no_term[idx])
            
            idx += 1
    else:
        while idx < fold:
            sample_data.append(sample_one_asp_one_opi[idx*(num_one_asp_one_opi)])
            sample_data.append(sample_one_asp_one_opi[idx*(num_one_asp_one_opi)+1])

            sample_data.append(sample_one_asp_multi_opi[idx*(num_one_asp_multi_opi)])

            sample_data.append(sample_multi_asp[idx*(num_multiple)])
            sample_data.append(sample_multi_asp[idx*(num_multiple)+1])

            sample_data.append(sample_data_no_term[idx])
            
            idx += 1

    for item in sample_data:
        text = item["raw_words"]
        if data_with_term_max_l[0]["task"] == "AE-OE":
            item["AE"] = get_prompt_ae_oe(text, item, "ae")
            item["OE"] = get_prompt_ae_oe(text, item, "oe")
            item["ALSC"] = get_prompt_alsc_aoe(text, item, "alsc")
            item["AESC"] = get_prompt_aesc_pair_triplet(text, item, "aesc")

        elif data_with_term_max_l[0]["task"] == "AOE":
            item["AOE"] = get_prompt_alsc_aoe(text, item, "aoe")

        elif data_with_term_max_l[0]["task"] == "AEOESC":
            item["AE"] = get_prompt_ae_oe(text, item, "ae")
            item["OE"] = get_prompt_ae_oe(text, item, "oe")
            item["ALSC"] = get_prompt_alsc_aoe(text, item, "alsc")
            item["AOE"] = get_prompt_alsc_aoe(text, item, "aoe")
            item["AESC"] = get_prompt_aesc_pair_triplet(text, item, "aesc")
            item["Pair"] = get_prompt_aesc_pair_triplet(text, item, "pair")
            item["Triplet"] = get_prompt_aesc_pair_triplet(text, item, "triplet")

    target_prompt = []

    idx = 0
    print(len(sample_data))
    while idx < fold:
        cur_dic = {}
        if data_with_term_max_l[0]["task"] == "AE-OE":
            idx_list = [idx*6, idx*6+1, idx*6+2, idx*6+3, idx*6+5]
            cur_dic["AE"] = "\n".join([sample_data[item]["AE"] for item in idx_list])
            cur_dic["OE"] = "\n".join([sample_data[item]["OE"] for item in idx_list])
            cur_dic["AESC"] = "\n".join([sample_data[item]["AESC"] for item in idx_list])

            idx_list = [idx*6, idx*6+1, idx*6+2, idx*6+3]
            alsc_list = []
            for item in idx_list:
                alsc_list += sample_data[item]["ALSC"]
            if len(sample_data[idx*6+3]["ALSC"]) == 3:
                alsc_list = alsc_list[:1] + alsc_list[2:]
            cur_dic["ALSC"] = "\n".join(alsc_list)
            

        if data_with_term_max_l[0]["task"] == "AOE":
            idx_list = [idx*6, idx*6+1, idx*6+2, idx*6+3, idx*6+4]
            aoe_list = []
            for item in idx_list:
                aoe_list += sample_data[item]["AOE"]
            cur_dic["AOE"] = "\n".join(aoe_list)

        if data_with_term_max_l[0]["task"] == "AEOESC":
            idx_list = [idx*6, idx*6+1, idx*6+2, idx*6+3, idx*6+5]
            cur_dic["AE"] = "\n".join([sample_data[item]["AE"] for item in idx_list])
            cur_dic["OE"] = "\n".join([sample_data[item]["OE"] for item in idx_list])
            cur_dic["AESC"] = "\n".join([sample_data[item]["AESC"] for item in idx_list])
            
            cur_dic["Pair"] = "\n".join([sample_data[item]["Pair"] for item in idx_list])
            cur_dic["Triplet"] = "\n".join([sample_data[item]["Triplet"] for item in idx_list])

            idx_list = [idx*6, idx*6+1, idx*6+2, idx*6+3]

            alsc_list = []
            for item in idx_list:
                alsc_list += sample_data[item]["ALSC"]
            if len(sample_data[idx*6+3]["ALSC"]) == 3:
                alsc_list = alsc_list[:1] + alsc_list[2:]
            cur_dic["ALSC"] = "\n".join(alsc_list)

            aoe_list = []
            for item in idx_list:
                aoe_list += sample_data[item]["AOE"]
            if len(sample_data[idx*6+3]["AOE"]) == 3:
                aoe_list = aoe_list[:1] + aoe_list[2:]
            cur_dic["AOE"] = "\n".join(aoe_list)
            
        target_prompt.append(cur_dic)

        idx += 1

    for k in target_prompt[0]:
        print(k)
        print(target_prompt[0][k])
        print()

    if data_with_term_max_l[0]["task"] == "AE-OE":
        result_dic = {
            "AE": [],
            "OE": [],
            "ALSC": [],
            "AESC": []
        }
        for d in target_prompt:
            result_dic["AE"].append(d["AE"])
            result_dic["OE"].append(d["OE"])
            result_dic["ALSC"].append(d["ALSC"])
            result_dic["AESC"].append(d["AESC"])



    if data_with_term_max_l[0]["task"] == "AOE":
        result_dic = {
            "AOE": [],
        }
        for d in target_prompt:
            result_dic["AOE"].append(d["AOE"])

    if data_with_term_max_l[0]["task"] == "AEOESC":
        result_dic = {
            "AE": [],
            "OE": [],
            "ALSC": [],
            "AOE": [],
            "AESC": [],
            "Pair": [],
            "Triplet": []
        }
        for d in target_prompt:
            result_dic["AE"].append(d["AE"])
            result_dic["OE"].append(d["OE"])
            result_dic["ALSC"].append(d["ALSC"])
            result_dic["AOE"].append(d["AOE"])
            result_dic["AESC"].append(d["AESC"])
            result_dic["Pair"].append(d["Pair"])
            result_dic["Triplet"].append(d["Triplet"])


    with open(os.path.join(output_path, output_file), 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(result_dic, indent=4, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    # ## ABSA
    # # # wang 
    absa_data_sample("absa/wang/14lap", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/wang/14res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/wang/15res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)

    # # # fan
    absa_data_sample("absa/fan/14lap", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/fan/14res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/fan/15res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/fan/16res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)

    # # # penga
    absa_data_sample("absa/penga/14lap", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/penga/14res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/penga/15res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/penga/16res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)

    # # # pengb
    absa_data_sample("absa/pengb/14lap", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/pengb/14res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/pengb/15res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)
    absa_data_sample("absa/pengb/16res", "train_convert.json", "test_convert.json", "prompt_icl.json", max_l=50, k=5, fold=5)

