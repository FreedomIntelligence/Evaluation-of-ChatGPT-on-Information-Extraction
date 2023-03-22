import json
import os
from tqdm import tqdm

raw_data_dir = "./raw_data"
output_dir = "./data"


## semeval_2010
def semeval_2010_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = []
        ent_type = {}
        relation_type = {}
        for line in fr.readlines():
            dic = json.loads(line)
    
            new_dic = {}
            new_dic["seq"] = " ".join(dic["token"])
            h = dic["h"]
            h_entity = {
                "type": "",
                "start": h["pos"][0],
                "end": h["pos"][1],
                "name": h["name"]
            }

            t = dic["t"]
            t_entity = {
                "type": "",
                "start": t["pos"][0],
                "end": t["pos"][1],
                "name": t["name"]
            }

            assert h["pos"][0] < t["pos"][0]
            entities = [h_entity, t_entity]
            r = dic["relation"]
            if r.split("(")[0] not in relation_type:
                relation_type[r.split("(")[0]] = len(relation_type)

            if "(e1,e2)" in r:
                relations = [{
                    "r": r.split("(")[0],
                    "h": 0,
                    "h_name": h_entity["name"],
                    "t": 1,
                    "t_name": t_entity["name"]
                }]
            elif "(e2,e1)" in r:
                relations = [{
                    "r": r.split("(")[0],
                    "h": 1,
                    "h_name": t_entity["name"],
                    "t": 0,
                    "t_name": h_entity["name"]
                }]
            else:
                relations = [{
                    "r": r,
                    "h": 0,
                    "h_name": h_entity["name"],
                    "t": 1,
                    "t_name": t_entity["name"]
                }]

            new_dic["entities"] = entities
            new_dic["relations"] = relations
            new_dic["mode"] = "flat"
            data.append(new_dic)
    
    print("#example: {}".format(len(data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)


## conll04
def conll04_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    ## 纠错
    str_tokens = ["Nor", "did", "he", "argue", ",", "as", "he", "did", "in", "a", "speech", "at", "the", "University", "of", "Virginia", "in", "Charlottesville", "Dec.", "16", ",", "that", "Congress", "had", "perpetuated", "a", "dangerous", "situation", "in", "Central", "America", "by", "its", "`", "`", "on-again", ",", "off-again", "indecisiveness", "'", "'", "on", "his", "program", "of", "aid", "to", "the", "anti-communist", "Contra", "rebels", "."]

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = []
        ent_type = {}
        relation_type = {}
        for line in fr.readlines():
            dic = json.loads(line)
            if dic["tokens"] == ["Nor", "did", "he", "argue", ",", "as", "he", "did", "in", "a", "speech", "at", "the", "University", "of", "Virginia", "in", "Charlottesville", "Dec.", "16", ",", "that", "Congress", "had", "perpetuated", "a", "dangerous", "situation", "in", "Central", "America", "by", "its", "`", "`", "on-again", ",", "off-again", "indecisiveness", "'", "'", "on", "his", "program", "of", "aid", "to", "the", "anti-communist", "Contra", "rebels", "."]:
                dic["span_list"][2]["end"] -= 1
    
            new_dic = {}
            new_dic["seq"] = " ".join(dic["tokens"])
            new_dic["entities"] = []
            for ent in dic["span_list"]:
                ent_name = " ".join(dic["tokens"][ent["start"]:ent["end"]+1])
                ent["name"] = ent_name
                ent["end"] = ent["end"] + 1
                new_dic["entities"].append(ent)
                if ent["type"] not in ent_type:
                    ent_type[ent["type"]] = ent["type"]

            new_dic["relations"] = []
            uni_ent_pair = []
            for pair in dic["span_pair_list"]:
                n_pair = {}
                n_pair["r"] = pair["type"]
                if pair["type"] not in relation_type:
                    relation_type[pair["type"]] = len(relation_type)
                n_pair["h"] = pair["head"]
                n_pair["h_name"] = new_dic["entities"][pair["head"]]["name"]
                n_pair["t"] = pair["tail"]
                n_pair["t_name"] = new_dic["entities"][pair["tail"]]["name"]
                new_dic["relations"].append(n_pair)
                if [pair["head"], pair["tail"]] not in uni_ent_pair:
                    uni_ent_pair.append([pair["head"], pair["tail"]])
            
            if len(new_dic["relations"]) > len(uni_ent_pair):
                new_dic["mode"] = "overlap"
            else:
                new_dic["mode"] = "flat"
            
            data.append(new_dic)
    
    print("#example: {}".format(len(data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)


# nyt-multi
def nyt_process(dataset, file_in, file_out):
    def get_index(name, e_list):
        for i, e in enumerate(e_list):
            if e["name"] == name:
                return i

    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        new_data = []
        ent_type = {}
        relation_type = {}
        for dic in data:
    
            new_dic = {}
            new_dic["seq"] = " ".join(dic["tokens"])
            entities = []
            spo_list = dic["spo_list"]
            spo_details = dic["spo_details"]
            for i in range(len(spo_list)):
                if spo_details[i][2] not in ent_type:
                    ent_type[spo_details[i][2]] = spo_details[i][2]
                entity = {
                    "type": spo_details[i][2],
                    "start": spo_details[i][0],
                    "end": spo_details[i][1],
                    "name": spo_list[i][0]
                }
                if entity not in entities:
                    entities.append(entity)
                
                if spo_details[i][6] not in ent_type:
                    ent_type[spo_details[i][6]] = spo_details[i][6]
                entity = {
                    "type": spo_details[i][6],
                    "start": spo_details[i][4],
                    "end": spo_details[i][5],
                    "name": spo_list[i][2]
                }
                if entity not in entities:
                    entities.append(entity)
            entities = sorted(entities, key=lambda a: int(a["start"]))

            relations = []
            uni_ent_pair = []
            for i in range(len(spo_list)):
                h_name = spo_list[i][0]
                h = get_index(h_name, entities)
                t_name = spo_list[i][2]
                t = get_index(t_name, entities)
                r = spo_list[i][1]
                relations.append({
                    "r": r,
                    "h": h,
                    "h_name": h_name,
                    "t": t,
                    "t_name": t_name
                })
                if r not in relation_type:
                    relation_type[r] = len(relation_type)
                if [h, t] not in uni_ent_pair:
                    uni_ent_pair.append([h, t])

            new_dic["entities"] = entities
            new_dic["relations"] = relations 
            if len(uni_ent_pair) < len(relations):
                new_dic["mode"] = "overlap"
            else:
                new_dic["mode"] = "flat" 
            
            new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


# tacred
def tacred_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        new_data = []

        ent_type = {}
        relation_type = {}
        
        for dic in data:
            new_dic = {}
            new_dic["id"] = dic["id"]
            new_dic["docid"] = dic["docid"]
            new_dic["seq"] = " ".join(dic["token"])

            entities = []
            subj_start = dic["subj_start"]
            obj_start = dic["obj_start"]

            if dic["subj_type"] not in ent_type:
                ent_type[dic["subj_type"]] = dic["subj_type"]
            if dic["obj_type"] not in ent_type:
                ent_type[dic["obj_type"]] = dic["obj_type"]
                
            if subj_start < obj_start:
                entities.append({
                    "type": dic["subj_type"],
                    "start": subj_start,
                    "end": dic["subj_end"]+1,
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]+1])
                })
                entities.append({
                    "type": dic["obj_type"],
                    "start": obj_start,
                    "end": dic["obj_end"]+1,
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]+1])
                })
                sbj = 0
                obj = 1
            else:
                entities.append({
                    "type": dic["obj_type"],
                    "start": obj_start,
                    "end": dic["obj_end"]+1,
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]+1])
                })
                entities.append({
                    "type": dic["subj_type"],
                    "start": subj_start,
                    "end": dic["subj_end"]+1,
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]+1])
                })
                sbj = 1
                obj = 0

            relations = []
            
            h_name = entities[sbj]["name"]
            h = sbj
            t_name = entities[obj]["name"]
            t = obj
            r = dic["relation"]
            relations.append({
                "r": r,
                "h": h,
                "h_name": h_name,
                "t": t,
                "t_name": t_name
            })
            if r not in relation_type:
                relation_type[r] = len(relation_type)

            new_dic["entities"] = entities
            new_dic["relations"] = relations  
            new_dic["mode"] = "flat"
            
            new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)

# re-tacred
def re_tacred_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        new_data = []

        ent_type = {}
        relation_type = {}
        
        for dic in data:
            new_dic = {}
            new_dic["id"] = dic["id"]
            new_dic["docid"] = dic["docid"]
            new_dic["seq"] = " ".join(dic["token"])

            entities = []
            subj_start = dic["subj_start"]
            obj_start = dic["obj_start"]

            if dic["subj_type"] not in ent_type:
                ent_type[dic["subj_type"]] = dic["subj_type"]
            if dic["obj_type"] not in ent_type:
                ent_type[dic["obj_type"]] = dic["obj_type"]
                
            if subj_start < obj_start:
                entities.append({
                    "type": dic["subj_type"],
                    "start": subj_start,
                    "end": dic["subj_end"]+1,
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]+1])
                })
                entities.append({
                    "type": dic["obj_type"],
                    "start": obj_start,
                    "end": dic["obj_end"]+1,
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]+1])
                })
                sbj = 0
                obj = 1
            else:
                entities.append({
                    "type": dic["obj_type"],
                    "start": obj_start,
                    "end": dic["obj_end"]+1,
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]+1])
                })
                entities.append({
                    "type": dic["subj_type"],
                    "start": subj_start,
                    "end": dic["subj_end"]+1,
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]+1])
                })
                sbj = 1
                obj = 0

            relations = []
            
            h_name = entities[sbj]["name"]
            h = sbj
            t_name = entities[obj]["name"]
            t = obj
            r = dic["relation"]
            relations.append({
                "r": r,
                "h": h,
                "h_name": h_name,
                "t": t,
                "t_name": t_name
            })
            if r not in relation_type:
                relation_type[r] = len(relation_type)

            new_dic["entities"] = entities
            new_dic["relations"] = relations
            new_dic["mode"] = "flat"
            
            new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


# cpr
def cpr_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        new_data = []

        ent_type = {}
        relation_type = {}
        
        for dic in data:
            new_dic = {}
            new_dic["id"] = dic["id"]
            new_dic["seq"] = " ".join(dic["token"])

            entities = []
            subj_start = dic["subj_start"]
            obj_start = dic["obj_start"]

            if dic["subj_type"] not in ent_type:
                ent_type[dic["subj_type"]] = dic["subj_type"]
            if dic["obj_type"] not in ent_type:
                ent_type[dic["obj_type"]] = dic["obj_type"]

            assert subj_start != dic["subj_end"]
            assert obj_start != dic["obj_end"]
                
            if subj_start < obj_start:
                entities.append({
                    "type": dic["subj_type"],
                    "start": subj_start,
                    "end": dic["subj_end"],
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]])
                })
                entities.append({
                    "type": dic["obj_type"],
                    "start": obj_start,
                    "end": dic["obj_end"],
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]])
                })
                sbj = 0
                obj = 1
            else:
                entities.append({
                    "type": dic["obj_type"],
                    "start": obj_start,
                    "end": dic["obj_end"],
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]])
                })
                entities.append({
                    "type": dic["subj_type"],
                    "start": subj_start,
                    "end": dic["subj_end"],
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]])
                })
                sbj = 1
                obj = 0

            relations = []
            
            h_name = entities[sbj]["name"]
            h = sbj
            t_name = entities[obj]["name"]
            t = obj
            r = dic["relation"]
            relations.append({
                "r": r,
                "h": h,
                "h_name": h_name,
                "t": t,
                "t_name": t_name
            })
            if r not in relation_type:
                relation_type[r] = len(relation_type)

            new_dic["entities"] = entities
            new_dic["relations"] = relations
            new_dic["mode"] = "flat"
            
            new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


# pgr
def pgr_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        new_data = []

        ent_type = {}
        relation_type = {}
        
        for dic in data:
            new_dic = {}
            new_dic["id"] = dic["id"]
            new_dic["seq"] = " ".join(dic["token"])

            entities = []
            subj_start = dic["subj_start"]
            obj_start = dic["obj_start"]

            assert "subj_type" not in dic.keys()
            assert "obj_type" not in dic.keys()
                
            if subj_start < obj_start:
                entities.append({
                    "type": "",
                    "start": subj_start,
                    "end": dic["subj_end"]+1,
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]+1])
                })
                entities.append({
                    "type": "",
                    "start": obj_start,
                    "end": dic["obj_end"]+1,
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]+1])
                })
                sbj = 0
                obj = 1
            else:
                entities.append({
                    "type": "",
                    "start": obj_start,
                    "end": dic["obj_end"]+1,
                    "name": " ".join(dic["token"][obj_start: dic["obj_end"]+1])
                })
                entities.append({
                    "type": "",
                    "start": subj_start,
                    "end": dic["subj_end"]+1,
                    "name": " ".join(dic["token"][subj_start: dic["subj_end"]+1])
                })
                sbj = 1
                obj = 0

            relations = []
            
            h_name = entities[sbj]["name"]
            h = sbj
            t_name = entities[obj]["name"]
            t = obj
            r = dic["relation"]
            relations.append({
                "r": r,
                "h": h,
                "h_name": h_name,
                "t": t,
                "t_name": t_name
            })
            if r not in relation_type:
                relation_type[r] = len(relation_type)

            new_dic["entities"] = entities
            new_dic["relations"] = relations
            new_dic["mode"] = "flat" 
            
            new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


# docred
def docred_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    print("process file: {}".format(file_in))
    print("saved file: {}".format(file_out))

    with open(file_in, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
        new_data = []
        
        for dic in data:
            new_dic = {}
            new_dic["title"] = dic["title"]
            new_dic["seq"] = " ".join([" ".join(sent) for sent in dic["sents"]])

            sent_len_start = [0]
            for sent in dic["sents"]:
                sent_len_start.append(len(sent)+sent_len_start[-1])
            # print(sent_len_start)

            entities = []
            relations = []
            for ent_list in dic["vertexSet"]:
                new_ent_list = []
                for ent in ent_list:
                    # print(ent)
                    sent_id = ent["sent_id"]
                    ent["pos"] = [ent["pos"][0]+sent_len_start[sent_id], ent["pos"][1]+sent_len_start[sent_id]]
                    new_ent_list.append(ent)
                    # print(ent)
                # print(new_ent_list)
                # exit()
                ent_list = sorted(new_ent_list, key=lambda a: a["pos"][0])
                ent = ent_list[0]
                entities.append({
                    "type": ent["type"],
                    "start": ent["pos"][0],
                    "end": ent["pos"][1],
                    "name": ent["name"]
                })

            uni_ent_pair = []
            for label in dic["labels"]:
                r = label["r"]
                h = label["h"]
                t = label["t"]
                h_name = entities[h]["name"]
                t_name = entities[t]["name"]
                relations.append({
                    "r": r,
                    "h": h,
                    "h_name": h_name,
                    "t": t,
                    "t_name": t_name
                })
                if [h, t] not in uni_ent_pair:
                    uni_ent_pair.append([h, t])

            new_dic["entities"] = entities
            new_dic["relations"] = relations

            if len(uni_ent_pair) < len(relations):
                new_dic["mode"] = "overlap"
            else:
                new_dic["mode"] = "flat" 
            
            new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)


## cdr and gda
# cdr_rel2id = {'1:NR:2': 0, '1:CID:2': 1}
# gda_rel2id = {'1:NR:2': 0, '1:GDA:2': 1}

def chunks(l, n):
    res = []
    for i in range(0, len(l), n):
        assert len(l[i:i + n]) == n
        res += [l[i:i + n]]
    return res

def get_sent_id(start_id, sent_len):
    for idx, s_len in enumerate(sent_len):
        if start_id < s_len:
            return idx-1
        
def get_entity_id(e_id, vset_list):
    for idx, v in enumerate(vset_list):
        if v[0]["id"] == e_id:
            return idx

def cdr_gda_process(dataset, file_in, file_out):
    file_in = os.path.join(raw_data_dir, os.path.join(dataset, file_in))
    out_dir = os.path.join(output_dir, dataset)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    file_out_1 = os.path.join(raw_data_dir, os.path.join(dataset, file_out))
    file_out = os.path.join(output_dir, os.path.join(dataset, file_out))
    
    print("process file: {}".format(file_in))

    pmids = set()
    docred_data = []
    with open(file_in, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        for i_l, line in enumerate(tqdm(lines)):
            line = line.rstrip().split('\t')
            pmid = line[0]

            docred_dic = {}
            docred_dic['title'] = str(pmid)
            docred_vset = []
            docred_labels = []
            docred_sents = []

            if pmid not in pmids:
                pmids.add(pmid)
                text = line[1]
                sent_len = [0]
                for t in text.split('|'):
                    sent = t.split(" ")
                    sent_len.append(len(sent) + sent_len[-1])
                    docred_sents.append(sent)

                prs = chunks(line[2:], 17)
                uni_ent_list = []
                for p in prs:
                    e_start = list(map(int, p[8].split(':')))
                    e_end = list(map(int, p[9].split(':')))
                    e_name = list(p[6].split('|'))
                    e_type = p[7]
                    e_id = p[5]
                    e_sent_id = [get_sent_id(start_id, sent_len) for start_id in e_start]
                    if e_id not in uni_ent_list:
                        uni_ent_list.append(e_id)
                        tmp_mention_list = []
                        for idx in range(len(e_start)):
                            tmp_mention_list.append({
                                "name": e_name[idx],
                                "pos": [e_start[idx]-sent_len[e_sent_id[idx]], e_end[idx]-sent_len[e_sent_id[idx]]],
                                "sent_id": e_sent_id[idx],
                                "type": e_type,
                                "global_pos": [e_start[idx], e_end[idx]],
                                "id": e_id
                            })
                        
                        docred_vset.append(tmp_mention_list)
                    
                    e_start = list(map(int, p[14].split(':')))
                    e_end = list(map(int, p[15].split(':')))
                    e_name = list(p[12].split('|'))
                    e_type = p[13]
                    e_id = p[11]
                    e_sent_id = [get_sent_id(start_id, sent_len) for start_id in e_start]
                    if e_id not in uni_ent_list:
                        uni_ent_list.append(e_id)
                        tmp_mention_list = []
                        for idx in range(len(e_start)):
                            tmp_mention_list.append({
                                "name": e_name[idx],
                                "pos": [e_start[idx]-sent_len[e_sent_id[idx]], e_end[idx]-sent_len[e_sent_id[idx]]],
                                "sent_id": e_sent_id[idx],
                                "type": e_type,
                                "global_pos": [e_start[idx], e_end[idx]],
                                "id": e_id
                            })
                        
                        docred_vset.append(tmp_mention_list)

                for p in prs:
                    if p[0] == "not_include":
                        continue
                    if p[1] == "L2R":
                        h_id, t_id = p[5], p[11]  
                    else:
                        t_id, h_id = p[5], p[11]

                    r = p[0]
                    h_e_id = get_entity_id(h_id, docred_vset)
                    t_e_id = get_entity_id(t_id, docred_vset)
                    docred_labels.append({
                        "r": r,
                        "h": h_e_id,
                        "t": t_e_id,
                        "evidence": []
                    })
            docred_dic["vertexSet"] = docred_vset
            docred_dic["labels"] = docred_labels
            docred_dic["sents"] = docred_sents
            docred_data.append(docred_dic)
    
    print("#example: {}".format(len(docred_data)))
    print("saved file: {}".format(file_out_1))
    with open(file_out_1, 'w', encoding='utf-8') as fw:
        json.dump(docred_data, fw, indent=4, ensure_ascii=False)   

    new_data = []
        
    for dic in docred_data:
        new_dic = {}
        new_dic["title"] = dic["title"]
        new_dic["seq"] = " ".join([" ".join(sent) for sent in dic["sents"]])

        entities = []
        relations = []
        for ent_list in dic["vertexSet"]:
            ent_list = sorted(ent_list, key=lambda a: a["pos"][0])
            ent = ent_list[0]
            entities.append({
                "type": ent["type"],
                "start": ent["pos"][0],
                "end": ent["pos"][1],
                "name": ent["name"]
            })

        uni_ent_pair = []
        for label in dic["labels"]:
            r = label["r"]
            h = label["h"]
            t = label["t"]
            h_name = entities[h]["name"]
            t_name = entities[t]["name"]
            relations.append({
                "r": r,
                "h": h,
                "h_name": h_name,
                "t": t,
                "t_name": t_name
            })
            if [h, t] not in uni_ent_pair:
                uni_ent_pair.append([h, t])

        new_dic["entities"] = entities
        new_dic["relations"] = relations

        if len(uni_ent_pair) < len(relations):
            new_dic["mode"] = "overlap"
        else:
            new_dic["mode"] = "flat" 
        
        new_data.append(new_dic)
    
    print("#example: {}".format(len(new_data)))
    print("saved file: {}".format(file_out))
    with open(file_out, 'w', encoding='utf-8') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)      
                    

if __name__ == "__main__":

    # semeval 2010
    # semeval_2010_process("re/sent/semeval2010/", "semeval_test.txt", "test.json")

    # conll04
    conll04_process("re/sent/conll04/", "test.jsonlines", "test.json")

    # # nyt-multi
    # nyt_process("re/sent/nyt-multi", "test.json", "test.json")

    # # tacred
    # tacred_process("re/sent/tacred", "test.json", "test.json")

    # # re-tacred
    # re_tacred_process("re/sent/re-tacred", "test.json", "test.json")

    # # cpr
    # cpr_process("re/sent/cpr", "test.json", "test.json")

    # # pgr
    # pgr_process("re/sent/pgr", "test.json", "test.json")

    # # docred
    # docred_process("re/doc/re-docred", "test_revised.json", "test.json")
    # docred_process("re/doc/dwie", "test.json", "test.json")
    # docred_process("re/doc/docred", "dev.json", "dev.json")
    # cdr_gda_process("re/doc/cdr", "test_filter.data", "test.json")
    # cdr_gda_process("re/doc/gda", "test.data", "test.json")
