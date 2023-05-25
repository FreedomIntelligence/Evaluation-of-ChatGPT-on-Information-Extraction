import json
import os


raw_data_dir = "./raw_data"
output_dir = "./data"


def casie_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    new_data = []
    num_sentences = 0
    num_cross_sentence = 0
    with open(file_in, 'r', encoding='utf-8') as fr:
        data = [json.loads(item) for item in fr.readlines()]
        for example in data:
            new_example = {}
            new_sents = []
            for sent in example["sentences"]:
                # sent = [item["word"] for item in sent["tokens"]]
                # print(sent["span"])
                sent = example["text"][sent["span"][0]: sent["span"][1]]
                # print(sent)
                new_sents.append(sent)

            new_sents_token = []
            for sent in example["sentences"]:
                sent = [item["word"] for item in sent["tokens"]]
                new_sents_token.append(sent)

            new_example["id"] = example["id"]
            new_example["text"] = example["text"]
            num_sentences += len(new_sents)
            # new_example["info"] = example["info"]
            # new_example["sentences"] = new_sents

            events = example["event"]

            event_list = []
            trigger2mention = {}

            for event in events:
                
                for mention in event["mentions"]:
                    mention["trigger"] = mention["nugget"]["text"]
                    trigger_span = mention["nugget"]["span"]
                    assert example["text"][trigger_span[0]: trigger_span[1] + 1] == mention["nugget"]["text"]

                    tri_sent_list_cur_mention = []
                    sent_list_cur_mention = []
                    tokens = mention["nugget"]["tokens"]                    
                    for token in tokens:
                        s_id = token[0]
                        t_id = token[1]
                        if s_id not in tri_sent_list_cur_mention:
                            tri_sent_list_cur_mention.append(s_id)
                            sent_list_cur_mention.append(s_id)
                    assert len(tri_sent_list_cur_mention) == 1

                    mention["trigger_span"] = [tokens[0][1], tokens[-1][1]+1]

                    trigger_s_id = tri_sent_list_cur_mention[0]
                    if trigger_s_id not in trigger2mention:
                        trigger2mention[trigger_s_id] = []

                    mention.pop("id")
                    mention.pop("nugget")

                    new_argus = []
                    for arg in mention["arguments"]:
                        arg.pop("id")
                        # arg["span"] = arg["span"]
                        assert arg["text"] == example["text"][arg["span"][0]: arg["span"][1]+1]
                        role_tokens = arg["tokens"]
                        role_s_id = role_tokens[0][0]
                        role_start_id = role_tokens[0][1]
                        role_end_id = role_tokens[-1][1] + 1
                    
                        if role_s_id == trigger_s_id:
                            tmp = {
                                "role": arg["role"],
                                "filler_type": arg["filler_type"],
                                "text": arg["text"],
                                "token": " ".join(new_sents_token[trigger_s_id][role_start_id: role_end_id]),
                                "span": [role_start_id, role_end_id]
                            }
                            new_argus.append(tmp)

                        for token in role_tokens:
                            s_id = token[0]
                            t_id = token[1] 
                            if s_id not in sent_list_cur_mention:
                                sent_list_cur_mention.append(s_id)
                        # arg.pop("tokens")
                        # arg.pop("span")

                    # mention["trigger"] = mention["trigger"]
                    # mention["trigger_span"] = mention["trigger_span"]
                    mention["arguments"] = new_argus
                    new_mention = {
                        "type": mention["type"],
                        "subtype": mention["subtype"],
                        "realis": mention["realis"],
                        "trigger": mention["trigger"],
                        "trigger_token": " ".join(new_sents_token[trigger_s_id][mention["trigger_span"][0]: mention["trigger_span"][1]]),
                        "trigger_span": mention["trigger_span"],
                        "arguments": mention["arguments"]
                    }
                    trigger2mention[trigger_s_id].append(new_mention)
                    
                    if len(sent_list_cur_mention) > 1:
                        num_cross_sentence += 1
                        # print(tri_sent_list_cur_mention, sent_list_cur_mention, example["id"])
                    event_list.append(mention)
            new_example["event"] = event_list
            # print(len(event_list))

            # for key in trigger2mention:
            #     if len(trigger2mention[key]) != 1:
            #         print(key, trigger2mention[key])
            #         exit()

            for idx in range(len(new_sents)):
                if idx in trigger2mention:
                    tmp = {
                        "d_id": example["id"],
                        "s_id": idx,
                        "text": new_sents[idx],
                        "tokens": " ".join(new_sents_token[idx]),
                        "event": trigger2mention[idx]
                    }
                else:
                    tmp = {
                        "d_id": example["id"],
                        "s_id": idx,
                        "text": new_sents[idx],
                        "tokens": " ".join(new_sents_token[idx]),
                        "event": []
                    }
                new_data.append(tmp)

    print(num_sentences, num_cross_sentence)
    print(len(new_data))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


def ace_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    new_data = []
    num_sentences = 0
    num_has_event = 0
    with open(file_in, 'r', encoding='utf-8') as fr:
        data = [json.loads(item) for item in fr.readlines()]
        for example in data:

            doc_text = []
            for item in example["sentences"]:
                doc_text += item

            d_id = example["doc_key"]

            for s_id, sent in enumerate(example["sentences"]):
                num_sentences += 1
                event = []
                for evt in example["events"][s_id]:
                    assert len(evt[0]) == 2
                    evt_type = evt[0][-1]
                    trigger_start = evt[0][0]
                    trigger_end = evt[0][-2] + 1
                    trigger_text = doc_text[trigger_start: trigger_end]

                    args_list = []
                    for evt_1 in evt[1:]:
                        role = evt_1[2]
                        arg_start = evt_1[0]
                        arg_end = evt_1[1] + 1
                        arg_text = doc_text[arg_start: arg_end]

                        args_list.append({
                            "role": role,
                            "text": " ".join(arg_text),
                            "token": arg_text
                        })
                    
                    event.append({
                        "type": evt_type,
                        "subtype": evt_type,
                        "trigger": " ".join(trigger_text),
                        "trigger_token": trigger_text,
                        "arguments": args_list
                    })
                    num_has_event += 1

                new_example = {
                    "d_id": d_id,
                    "s_id": s_id,
                    "text": " ".join(sent),
                    "tokens": sent,
                    "event": event
                }

                new_data.append(new_example)
                

    print(num_sentences, num_has_event)
    print(len(new_data))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


def ace_plus_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    new_data = []
    num_sentences = 0
    num_has_event = 0
    with open(file_in, 'r', encoding='utf-8') as fr:
        data = [json.loads(item) for item in fr.readlines()]
        for example in data:

            num_sentences += 1

            event = []
            for evt in example["event_mentions"]:

                args_list = []
                for arg in evt["arguments"]:
                    args_list.append({
                        "role": arg["role"],
                        "text": arg["text"],
                        "token": arg["text"].split(" ")
                    })
                
                event.append({
                    "type": evt["event_type"],
                    "subtype": evt["event_type"],
                    "trigger": evt["trigger"]["text"],
                    "trigger_token": evt["trigger"]["text"].split(" "),
                    "arguments": args_list
                })
                num_has_event += 1

            new_example = {
                    "d_id": example["doc_id"],
                    "s_id": example["sent_id"],
                    "text": " ".join(example["tokens"]),
                    "tokens": example["tokens"],
                    "event": event
                }
            new_data.append(new_example)
                

    print(num_sentences, num_has_event)
    print(len(new_data))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


def commodity_news_ee_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    new_data = []
    num_sentences = 0
    num_has_event = 0
    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        for example in data:

            num_sentences += 1

            event = []
            for evt in example["golden-event-mentions"]:

                args_list = []
                for arg in evt["arguments"]:
                    args_list.append({
                        "role": arg["role"],
                        "text": arg["text"],
                        "token": arg["text"].split(" ")
                    })
                
                event.append({
                    "type": evt["event_type"],
                    "subtype": evt["event_type"],
                    "trigger": evt["trigger"]["text"],
                    "trigger_token": evt["trigger"]["text"].split(" "),
                    "arguments": args_list
                })
                num_has_event += 1

            new_example = {
                    "d_id": example["sentence_id"],
                    "s_id": example["sentence_id"],
                    "text": example["sentence"],
                    "tokens": example["words"],
                    "event": event
                }
            new_data.append(new_example)
                

    print(num_sentences, num_has_event)
    print(len(new_data))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)
    

if __name__ == "__main__":

    # casie
    casie_process("ee/casie/", "test_processed.jsonlines", "test.json")
    casie_process("ee/casie/", "train_processed.jsonlines", "train.json")
    casie_process("ee/casie/", "dev_processed.jsonlines", "dev.json")

    # ace05
    ace_process("ee/ace05/", "test.json", "test.json")
    ace_process("ee/ace05/", "train.json", "train.json")
    ace_process("ee/ace05/", "dev.json", "dev.json")

    # ace05+
    ace_plus_process("ee/ace05+/", "test.oneie.json", "test.json")
    ace_plus_process("ee/ace05+/", "train.oneie.json", "train.json")
    ace_plus_process("ee/ace05+/", "dev.oneie.json", "dev.json")

    # commodity news ee
    commodity_news_ee_process("ee/commodity_news_EE/", "event_extraction_test.json", "test.json")
    commodity_news_ee_process("ee/commodity_news_EE/", "event_extraction_train.json", "train.json")