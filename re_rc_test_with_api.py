import json, os
import random
import time
import ast
import openai
from utils import Logger, bot_run
from config import get_opts_re as get_opts


def re_rc_main(opts, bot, logger):
    start_time = time.time()

    logger.write("{}\n".format(opts.test_file))
    logger.write("{}\n".format(opts.type_file))
    ## load data
    logger.write("loading data ...\n")
    with open(opts.test_file, 'r', encoding='utf-8') as fr, open(opts.type_file, 'r', encoding='utf-8') as fr_type:
        data = json.load(fr)
        types = json.load(fr_type)
        r_types = list(types["relation"].values())

    ## sample
    index_list = list(range(0, len(data)))
    if opts.sample:
        logger.write("Sampling examples ...\n")
        selected_idx = random.sample(index_list, opts.sample_k)
        selected_idx.sort()
    else:
        selected_idx = index_list
    # selected_idx = index_list[:30]
    ## sample end

    ## API
    with open(opts.result_file, 'a', encoding='utf-8') as fw:
        # fw.seek(0)  #定位
        # fw.truncate()   #清空文件
        # fw.write("[\n")
        logger.write("Evaluation begining ...\n")
        i = 110
        while i < len(selected_idx):
        
            idx = selected_idx[i]
            i += 1
            logger.write("No. "+ str(i) + " | example's id: " + str(idx) + " | total examples: " + str(len(data)) + "\n")
            example = data[idx]

            ## all entities
            ent_list = []
            ent_list_lower = []
            for ent in example["entities"]:
                ent_name = ent["name"]
                if ent_name.lower() not in ent_list_lower:
                    ent_list_lower.append(ent_name.lower())
                    ent_list.append(ent_name)

            ## each pair
            pairs_str = ""
            for subj in ent_list:
                for obj in ent_list:
                    if subj != obj:
                        pairs_str += '("{}", "{}")\n'.format(subj, obj)
            pairs_str =pairs_str.strip("\n")       

            prompt = 'According to the text "{}", from the list of relations: {}, identify all relations for each of the following subject-object entity pairs of the form ("subject", "object"). Answer in the format "("subject", "object"): ["relation_1", "relation_2", ...].\n {}'.format(example["seq"], json.dumps(r_types), pairs_str)

            response = bot_run(bot, prompt, "RE-RC", logger, model=opts.model)

            lines = response.split("\n")
            result_dict = {}

            for line in lines:
                line = line.strip()
                if line  == "":
                    continue
                item_list = line.split(":")
                # print(item_list)
                es = item_list[0].strip().strip("(").strip(")").split(",")
                es = [e.strip().strip('"') for e in es]

                rel_str = item_list[1].strip()

                if "[" not in rel_str and "]" not in rel_str:
                    result_dict[es[0] + " # " + es[1]] = {
                        "h": es[0],
                        "t": es[1],
                        "r": rel_str
                    }
                else:
                    rel_list = ast.literal_eval(item_list[1].strip())
                    for rel in rel_list: 
                        result_dict[es[0] + " # " + es[1]] = {
                            "h": es[0],
                            "t": es[1],
                            "r": rel
                        }

            example.update({
                "RE": result_dict,
                "prompt": prompt,
                "response": response
            })

            fw.write(json.dumps(example, indent=4, ensure_ascii=False))  
            if i != len(selected_idx):
                fw.write("\n,\n")
            else:
                fw.write("\n")
        fw.write("]\n")
    end_time = time.time()
    logger.write("The result is saved: {}\n".format(opts.result_file))
    logger.write("Times: {:.2f}s = {:.2f}m\n".format(end_time-start_time, (end_time-start_time)/60.0))


if __name__ == "__main__":
    opts = get_opts()

    api_key_file = os.path.join("./api-keys", opts.api_key)
    openai.api_key_path = api_key_file
    bot = openai.ChatCompletion()
    
    ## log file
    logger_file = os.path.join(opts.task, opts.logger_file)
    logger = Logger(file_name=logger_file)
    logger.write(json.dumps(opts.__dict__, indent=4) + "\n")

    if opts.task == "re":
        re_rc_main(opts, bot, logger)

