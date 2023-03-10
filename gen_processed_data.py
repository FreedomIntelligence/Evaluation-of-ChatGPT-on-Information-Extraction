import json
import os

raw_data_dir = "./raw_data"
output_dir = "./data"

polarity_mapping = {
    "POS": "positive",
    "NEG": "negative",
    "NEU": "neutral",
    "CON": "conflict",  # wang, 并且 14res 有三个 aspect 漏标了 polarity
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
                    continue
                span = str(asp["from"]) + "#" + str(asp["to"])
                assert span not in asp_list
                if span not in asp_list:
                    asp_list.append(span)
                    total_num_pair += len(example["opinions"])  # opinions 无重复

            for opi in example["opinions"]:
                if "from" not in opi.keys():
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
                    continue
                span = str(asp["from"]) + "#" + str(asp["to"])
                span_word = (" ".join(asp["term"]))
                if "polarity" not in asp:
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
                        new_asp["pairs"] = asp_span_to_pairs[span]
                        new_asp["triplets"] = asp_span_to_triplets[span]
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
    print("#aspecct : ", total_num_aspect)
    print("#opinion : ", total_num_opinion)
    print("#pair    : ", total_num_pair)
    
    with open(os.path.join(output_path, input_file), 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(new_data, indent=4, ensure_ascii=False))       


## NER dataset pre-processing
def ner_data_process(dataset, input_file, output_file, type_file, separator=" "):

    total_num_entity = 0
    total_length_sentence = 0.0
    max_num_entity_per_sentence = 0
    num_nested_sentence = 0
    num_nested_entity = 0

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    in_file_name = os.path.join(raw_data_dir, os.path.join(dataset, input_file))
    print("begin processing: ", in_file_name)
    with open(in_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_data = []
    for example in data:
        seq_tokens = example['tokens']
        total_length_sentence += len(seq_tokens)
        sent = separator.join(seq_tokens)

        entities = example['entities']
        if len(entities) > max_num_entity_per_sentence:
            max_num_entity_per_sentence = len(entities)

        entity_list = []
        for entity in entities:
            total_num_entity += 1

            e_seq = separator.join(seq_tokens[entity['start']: entity['end']])
            e_type = entity['type']
            entity_list.append(
                {
                "e_name": e_seq,
                "e_type": e_type,
                "start": entity['start'],
                "end": entity["end"]
                }
            )

        entity_list = sorted(entity_list, key=lambda e: e['start'])

        ### judge nested entities
        nested_entity_list = []
        for ii in range(len(entity_list)):
            entity = entity_list[ii]
            start = entity["start"]
            end = entity["end"]

            for jj in range(len(entity_list)):
                if ii != jj:
                    entity_1 = entity_list[jj]
                    tar_start = entity_1["start"]
                    tar_end = entity_1["end"]
                    if (start >= tar_start and end <= tar_end) or (start <= tar_start and end >= tar_end):
                        if entity not in nested_entity_list:
                            nested_entity_list.append(entity)
                        if entity_1 not in nested_entity_list:
                            nested_entity_list.append(entity_1)
        ###

        new_example = dict()
        if len(nested_entity_list) != 0:
            new_example['mode'] = "nested"
            num_nested_sentence += 1
            num_nested_entity += len(nested_entity_list)
            nested_entity_list = sorted(nested_entity_list, key=lambda e: e['start'])
        else:
            new_example['mode'] = "flat"
        
        new_example['seq'] = sent
        new_example['entities'] = entity_list
        new_data.append(new_example)

    print("#sentences: ", len(new_data))
    print("#entities : ", total_num_entity)
    print("avg. sentence length       : ", total_length_sentence/len(new_data))
    print("max. #entities per sentence: ", max_num_entity_per_sentence)
    print("avg. #entities per sentence: ", total_num_entity*1.0/len(new_data))
    print("# nested sentences : ", num_nested_sentence)
    print("# nested entities  : ", num_nested_entity)
    print("nesting ratio      : ", num_nested_entity*1.0/total_num_entity)
    
    with open(os.path.join(output_path, output_file), 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(new_data, indent=4, ensure_ascii=False))

    ## type file
    type_file_name = os.path.join(raw_data_dir, os.path.join(dataset, type_file))
    print("begin processing: ", type_file_name)
    with open(type_file_name, 'r', encoding='utf-8') as fr_t:
        type_data = json.load(fr_t)
    with open(os.path.join(output_path, "types.json"), 'w', encoding='utf-8') as fw_t:
        fw_t.write(json.dumps(type_data, indent=4, ensure_ascii=False))


def ner_nested_data_process(dataset, input_file, output_file, num_type, separator=" "):

    total_num_entity = 0
    total_length_sentence = 0.0
    max_num_entity_per_sentence = 0
    num_nested_sentence = 0
    num_nested_entity = 0

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    in_file_name = os.path.join(raw_data_dir, os.path.join(dataset, input_file))
    print("begin processing: ", in_file_name)
    with open(in_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)

    i = 0
    new_data = []
    while i < len(data):
        sent = data[i]["context"]
        seq_tokens = sent.split(separator)
        total_length_sentence += len(seq_tokens)

        entity_list = []
        for j in range(num_type):
            example = data[i + j]
            spans = example["span_position"]
            e_type = example["entity_label"]

            for span in spans:
                start_id = int(span.split(";")[0])
                end_id = int(span.split(";")[1]) + 1
                e_name = separator.join(seq_tokens[start_id: end_id])
                entity_list.append(
                    {
                    "e_name": e_name,
                    "e_type": e_type,
                    "start": start_id,
                    "end": end_id
                    }
                )
        
        total_num_entity += len(entity_list)
        if len(entity_list) > max_num_entity_per_sentence:
            max_num_entity_per_sentence = len(entity_list)

        entity_list = sorted(entity_list, key=lambda e: e['start'])

        ### judge nested entities
        nested_entity_list = []
        # print_list = []
        # print_list_1 = []
        for ii in range(len(entity_list)):
            entity = entity_list[ii]
            start = entity["start"]
            end = entity["end"]
            # print_list.append([start, end])

            for jj in range(len(entity_list)):
                if ii != jj:
                    entity_1 = entity_list[jj]
                    tar_start = entity_1["start"]
                    tar_end = entity_1["end"]
                    if (start >= tar_start and end <= tar_end) or (start <= tar_start and end >= tar_end):
                        if entity not in nested_entity_list:
                            nested_entity_list.append(entity)
                            # print_list_1.append([start, end])
                        if entity_1 not in nested_entity_list:
                            nested_entity_list.append(entity_1)
                            # print_list_1.append([tar_start, tar_end])
        ###

        new_example = dict()
        if len(nested_entity_list) != 0:
            new_example['mode'] = "nested"
            num_nested_sentence += 1
            num_nested_entity += len(nested_entity_list)
            nested_entity_list = sorted(nested_entity_list, key=lambda e: e['start'])
        else:
            new_example['mode'] = "flat"
        new_example['seq'] = sent
        new_example['entities'] = entity_list
        new_data.append(new_example)
        i += num_type

    print("#sentences: ", len(new_data))
    print("#entities : ", total_num_entity)
    print("avg. sentence length       : ", total_length_sentence/len(new_data))
    print("max. #entities per sentence: ", max_num_entity_per_sentence)
    print("avg. #entities per sentence: ", total_num_entity*1.0/len(new_data))
    print("# nested sentences : ", num_nested_sentence)
    print("# nested entities  : ", num_nested_entity)
    print("nesting ratio      : ", num_nested_entity*1.0/total_num_entity)

    # json.dump(new_data, open(os.path.join(output_path, output_file), 'w'))
    with open(os.path.join(output_path, output_file), 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(new_data, indent=4, ensure_ascii=False))

    ## ace2004 and ace2005 types
    types = {
        "entities": {
            "GPE": {"verbose": "geographical political entities", "short": "GPE"}, 
            "ORG": {"verbose": "organization", "short": "ORG"}, 
            "PER": {"verbose": "person", "short": "PER"},
            "FAC": {"verbose": "facility", "short": "FAC"},
            "VEH": {"verbose": "vehicle", "short": "VEH"},
            "LOC": {"verbose": "location", "short": "LOC"},
            "WEA": {"verbose": "weapon", "short": "WEA"}
        }, 
        "relations": {}
    }
    with open(os.path.join(output_path, "types.json"), 'w', encoding='utf-8') as fw_t:
        fw_t.write(json.dumps(types, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    ## ABSA
    # wang
    absa_data_process("absa/wang/14lap", "test_convert.json")  # 800 654 674 0
    absa_data_process("absa/wang/14res", "test_convert.json")  # 800 1134 1008 0
    absa_data_process("absa/wang/15res", "test_convert.json")  # 685 542 510 0 -> 681 541 509 0
    # aewsome / highly recommended ! / loved it: 0 aspect 0 opinion
    # great food: 1 aspect 1 opinion
    # fan
    absa_data_process("absa/fan/14lap", "test_convert.json")  # 343 481 498 565
    absa_data_process("absa/fan/14res", "test_convert.json")  # 500 864 888 1030
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


    ## NER
    ner_data_process("ner/conll03/", "conll032_test_context.json", "conll03_test.json", "conll032_types.json")
    ner_data_process("ner/fewnerd/", "fewnerd_test_context.json", "fewnerd_test.json", "fewnerd_types.json")
    ner_data_process("ner/zhmsra/", "zhmsra_test_context.json", "zhmsra_test.json", "zhmsra_types.json", separator="")
    ner_data_process("ner/genia/", "genia_test_context.json", "genia_test.json", "genia_types.json")
    ner_nested_data_process("ner/ace2004", "mrc-ner.test", "ace04_test.json", 7)
    ner_nested_data_process("ner/ace2005", "mrc-ner.test", "ace05_test.json", 7)
    
    