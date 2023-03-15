import json
import os

raw_data_dir = "./raw_data"
output_dir = "./data"

polarity_mapping = {
    "POS": "positive",
    "NEG": "negative",
    "NEU": "neutral",
    "CON": "conflict",  # wang, 并且 14res 有4个 aspect 漏标了 polarity
}

## ABSA dataset statistics
def absa_data_process(dataset, input_file):

    def get_opinion_by_index(opi_list, index):
        for opi in opi_list:
            if opi["index"] == index:
                return " ".join(opi["term"])

    total_num_sentence = 0
    total_num_aspect = 0
    total_num_opinion = 0
    total_num_pair = 0
    num_no_aspect = 0
    num_no_opinion = 0
    num_no_alsc = 0
    num_no_aoe = 0
    num_no_aesc = 0
    num_no_pair = 0
    num_no_triplet = 0

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    in_file_name = os.path.join(raw_data_dir, os.path.join(dataset, input_file))
    print("begin processing: ", in_file_name)
    with open(in_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = []
    if "task" in data[0].keys() and data[0]["task"] == "AOE":  # fan

        sent_list = []
        asp_list, opi_list = [], []
        pre_sentence = ""
        # print(len(data))
        for example in data:
            new_example = dict()

            ### 修正 fan/14lap/test_convert.json
            if example["raw_words"] == "Did not enjoy the new Win1. dows 8 and touchscreen functions .":
                example["raw_words"] = "Did not enjoy the new Windows 8 and touchscreen functions ."
                example["words"] = ["Did", "not", "enjoy", "the", "new", "Windows", "8", "and", "touchscreen", "functions", "."]
                example["aspects"][0]["term"] = ["Windows", "8"]

            sent = example["raw_words"]

            ## sent_list 去重
            asp_str = ""
            for asp in  example["aspects"]:
                if "from" in asp.keys():
                    asp_str += (str(asp["from"]) + "#" + str(asp["to"]))
                else:
                    asp_str += "aspect_empty"
            
            opi_str = ""
            for opi in  example["opinions"]:
                if "from" in opi.keys():
                    opi_str += (str(opi["from"]) + "#" + str(opi["to"]))
                else:
                    opi_str += "opinion_empty"
            
            sent_aspect_opinion = sent + "-" + asp_str + "-" + opi_str
            if sent_aspect_opinion not in sent_list:
                sent_list.append(sent_aspect_opinion)  
            else:  ## 去重 begin
                # print(sent)
                continue
            
            # 统计 #s, #a, #o, #p
            if sent != pre_sentence:
                total_num_sentence += 1
                pre_sentence = sent
                total_num_aspect += len(asp_list)
                total_num_opinion += len(opi_list)
                asp_list = []
                opi_list = []

            for asp in example["aspects"]:
                if "from" not in asp.keys():
                    num_no_aspect += 1
                    continue
                span = str(asp["from"]) + "#" + str(asp["to"])
                assert span not in asp_list
                if span not in asp_list:
                    asp_list.append(span)
                    total_num_pair += len(example["opinions"])  # opinions 无重复

            for opi in example["opinions"]:
                if "from" not in opi.keys():
                    num_no_opinion += 1
                    continue
                span = str(opi["from"]) + "#" + str(opi["to"])
                if span not in opi_list:
                    opi_list.append(span)

            new_example["raw_words"] = sent
            new_example["task"] = example["task"]
            # asp： 一个example 只有 一个 aspect
            new_asp_list_processed = []
            new_asp_dict = dict()
            asp = example["aspects"][0]
            span = [asp["from"], asp["to"]]
            span_word = " ".join(asp["term"])

            opi_word_for_asp_list = []
            for opi in example["opinions"]:
                opi_word_for_asp_list.append(" ".join(opi["term"]))
            new_asp_dict["span"] = span
            new_asp_dict["term"] = span_word
            new_asp_dict["opinions"] = opi_word_for_asp_list
            if len(opi_word_for_asp_list) == 0:
                num_no_aoe += 1
            new_asp_list_processed.append(new_asp_dict)
            new_example["aspects"] = new_asp_list_processed

            # opi
            new_opi_list_processed = []
            for opi in example["opinions"]:
                new_opi_list_processed.append(
                    {
                    "span": [opi["from"], opi["to"]],
                    "term": " ".join(opi["term"])
                    }
                )
            new_example["opinions"] = new_opi_list_processed

            new_data.append(new_example)

        total_num_aspect += len(asp_list)
        total_num_opinion += len(opi_list)

    else:  # wang, penga, pengb
        sent_list = []
        for example in data:
            new_example = dict()
            sent = example["raw_words"]
            if sent not in sent_list:
                sent_list.append(sent)
            else: 
                # print(sent)
                if "task" not in data[0].keys() or data[0]["task"] == "AEOESC" or data[0]["task"] == "AE-OE": 
                    continue  # wang, penga, pengb去重
            new_example["raw_words"] = sent

            ## asp
            if "task" not in data[0].keys() or data[0]["task"] == "AEOESC":
                asp_span_to_opis = dict()
                asp_span_to_pairs = dict()
                asp_span_to_triplets = dict()
                asp_list = []
                for asp in example["aspects"]:
                    index = asp["index"]
                    opi_word = get_opinion_by_index(example["opinions"], index)
                    span = str(asp["from"]) + "#" + str(asp["to"])
                    span_word = " ".join(asp["term"])
                    cur_pair = [span_word, opi_word]
                    polarity = polarity_mapping[asp["polarity"]]
                    cur_triplet = [span_word, polarity, opi_word]
                    if span not in asp_list:
                        asp_list.append(span)
                        asp_span_to_opis[span] = [opi_word]
                        asp_span_to_pairs[span] = [cur_pair]
                        asp_span_to_triplets[span] = [cur_triplet]
                    else:
                        asp_span_to_opis[span].append(opi_word)
                        asp_span_to_pairs[span].append(cur_pair)
                        asp_span_to_triplets[span].append(cur_triplet)


            asp_list = []
            new_asp_list_processed = []
            for asp in example["aspects"]:
                new_asp = dict()
                if "from" not in asp.keys():
                    new_asp_list_processed.append({"span":[], "term": ""})
                    num_no_aspect += 1
                    continue
                span = str(asp["from"]) + "#" + str(asp["to"])
                span_word = (" ".join(asp["term"]))
                if "polarity" not in asp:
                    num_no_alsc += 1
                    num_no_aesc += 1
                    span_polarity = ""  # wang/14res 漏标, 设置为 ""
                    print(asp["term"], " : no polarity label.")
                else:
                    span_polarity = polarity_mapping[asp["polarity"]]

                if span not in asp_list:
                    asp_list.append(span)
                    new_asp["span"] = [asp["from"], asp["to"]]
                    new_asp["term"] = span_word
                    new_asp["polarity"] = span_polarity
                    if "task" not in data[0].keys() or data[0]["task"] == "AEOESC":
                        new_asp["opinions"] = asp_span_to_opis[span]
                        if len(asp_span_to_opis[span]) == 0:
                            num_no_aoe += 1
                        new_asp["pairs"] = asp_span_to_pairs[span]
                        if len(asp_span_to_pairs[span]) == 0:
                            num_no_pair += 1
                        new_asp["triplets"] = asp_span_to_triplets[span]
                        if len(asp_span_to_triplets[span]) == 0:
                            num_no_triplet += 1
                    new_asp_list_processed.append(new_asp)
 

            new_example["aspects"] = new_asp_list_processed
            total_num_aspect += len(asp_list)
            ## asp

            ## opi
            opi_list = []  # 去重
            new_opi_list_processed = []
            for opi in example["opinions"]:
                new_opi = dict()
                if "from" not in opi.keys():
                    new_opi_list_processed.append({"span":[], "term": ""})
                    num_no_opinion += 1
                    continue
                span = [opi["from"], opi["to"]]
                span_word = (" ".join(opi["term"])).lower()

                if span not in opi_list:
                    opi_list.append(span)
                    new_opi["span"] = span
                    new_opi["term"] = span_word
                    new_opi_list_processed.append(new_opi)
            
            new_example["opinions"] = new_opi_list_processed
            total_num_opinion += len(opi_list)
            ## opi

            if "task" not in data[0].keys() or data[0]["task"] == "AEOESC":
                assert len(example["aspects"]) == len(example["opinions"])
                total_num_pair += len(example["aspects"])

            if "task" not in example.keys():
                new_example.update({"task": "AEOESC"})
            else:
                new_example["task"] = example["task"]

            new_data.append(new_example)

        total_num_sentence = len(sent_list)
        print(total_num_sentence, len(data))

    print("#sentence: ", total_num_sentence)
    print("#aspect : ", total_num_aspect)
    print("#opinion : ", total_num_opinion)
    print("#pair    : ", total_num_pair)
    print("#sentence no aspect: ", num_no_aspect)
    print("#sentence no opinion: ", num_no_opinion)
    print("#sentence no alsc: ", num_no_alsc)
    print("#sentence no aoe: ", num_no_aoe)
    print("#sentence no aesc: ", num_no_aesc)
    print("#sentence no pair: ", num_no_pair)
    print("#sentence no triplet: ", num_no_triplet)
    
    with open(os.path.join(output_path, input_file), 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(new_data, indent=4, ensure_ascii=False))       


if __name__ == "__main__":
    ## ABSA
    # wang
    absa_data_process("absa/wang/14lap", "test_convert.json")  # 800 654 674 0
    absa_data_process("absa/wang/14res", "test_convert.json")  # 800 1134 1008 0
    absa_data_process("absa/wang/15res", "test_convert.json")  # 685 542 510 0 -> 681 541 509 0
    # aewsome / highly recommended ! / loved it: 0 aspect 0 opinion
    # great food: 1 aspect 1 opinion
    # fan
    absa_data_process("absa/fan/14lap", "test_convert.json")  # 343 481 498 565 -> ? 重复一个sample -> 481
    # # the volume is really low to low for a laptopwas not expectin t volume to be so lowan i hate that about this computer
    absa_data_process("absa/fan/14res", "test_convert.json")  # 500 864 888 1030 -> ? 无重复句子，就是864个sample
    absa_data_process("absa/fan/15res", "test_convert.json")  # 325 436 469 493
    absa_data_process("absa/fan/16res", "test_convert.json")  # 329 457 486 525 -> 328 456 485 524 : Great Breakfast
    # # penga
    absa_data_process("absa/penga/14lap", "test_convert.json")  # 339 418 490 490
    absa_data_process("absa/penga/14res", "test_convert.json")  # 496 726 862 862
    absa_data_process("absa/penga/15res", "test_convert.json")  # 318 403 455 455
    absa_data_process("absa/penga/16res", "test_convert.json")  # 320 405 465 465 -> 319 404 464 464 : Great Breakfast
    # # pengb
    absa_data_process("absa/pengb/14lap", "test_convert.json")  # 328 463 474 543
    absa_data_process("absa/pengb/14res", "test_convert.json")  # 492 848 854 994
    absa_data_process("absa/pengb/15res", "test_convert.json")  # 322 432 461 485
    absa_data_process("absa/pengb/16res", "test_convert.json")  # 326 452 475 514 -> 325 451 474 513 : Great Breakfast

    