import json
import os

raw_data_dir = "./raw_data"
output_dir = "./data"

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
    ## NER
    ner_data_process("ner/conll03/", "conll032_test_context.json", "conll03_test.json", "conll032_types.json")

    ner_data_process("ner/fewnerd/", "fewnerd_test_context.json", "fewnerd_test.json", "fewnerd_types.json")

    ner_data_process("ner/zhmsra/", "zhmsra_test_context.json", "zhmsra_test.json", "zhmsra_types.json", separator="")

    ner_data_process("ner/genia/", "genia_test_context.json", "genia_test.json", "genia_types.json")

    ner_nested_data_process("ner/ace2004", "mrc-ner.test", "ace04_test.json", 7)

    ner_nested_data_process("ner/ace2005", "mrc-ner.test", "ace05_test.json", 7)
    
    