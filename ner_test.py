from chatgpt_wrapper import ChatGPT
import argparse, os
import json
import random
import asyncio


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default="ner")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="conll03")
    parser.add_argument('--test_file', type=str, default="conll03_test.json")
    parser.add_argument('--type_file', type=str, default="types.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=50)
    opts = parser.parse_args()
    return opts


def ner_main(opts, bot):
    
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    input_dir = os.path.join(opts.input_dir, os.path.join(os.path.join(opts.task, opts.dataset), opts.test_file))
    type_dir = os.path.join(opts.input_dir, os.path.join(os.path.join(opts.task, opts.dataset), opts.type_file))
    print("loading data ...")
    with open(input_dir, 'r', encoding='utf-8') as fr:
        data = json.load(fr)
    with open(type_dir, 'r', encoding='utf-8') as fr:
        types = json.load(fr)
        e_types = list(types['entities'].keys())

    flat_data = []
    nested_data = []
    for example in data:
        if example["mode"] == "flat":
            flat_data.append(example)
        elif example["mode"] == "nested":
            nested_data.append(example)
        else:
            print("[Error]: unknown mode ", example["mode"])

    with open(os.path.join(result_dir, opts.test_file.split('.')[0] + "_result.json"), 'a', encoding='utf-8') as fw:
        fw.seek(0)
        fw.truncate()
        if len(nested_data) == 0:  ## flat
            print("Sampling examples ...")
            index_list = list(range(len(flat_data)))
            selected_idx = random.sample(index_list, opts.sample_k)
            selected_idx.sort()
            # print(len(selected_idx), selected_idx)
            print("Evaluation begining ...")
            i = 0
            for idx in selected_idx:
                i += 1
                example = data[idx]
                prompts = "Considering {} types of named entities including {} and {}, now recognize all entities in the following sentence with the format 'entity_type: entity_name': {}".format(len(e_types), ", ".join(e_types[:-1]), e_types[-1], example['seq'])
                
                print("[{}|{}]".format(i, idx), prompts)
                bot.new_conversation()
                response = asyncio.run(bot.ask(prompts))
                asyncio.run(bot.delete_conversation())
                print("[response]:", response)

                result_dict = dict()
                result_dict.update(example)
                result_dict.update({
                    "response": response
                })

                fw.write(json.dumps(result_dict, indent=4, ensure_ascii=False)) 
                fw.write("\n\n")

        else:  # nested
            print("Sampling examples ...")
            flat_index_list = list(range(len(nested_data)))
            flat_selected_idx = random.sample(flat_index_list, opts.sample_k//2)
            flat_selected_idx.sort()

            nested_index_list = list(range(len(flat_data)))
            nested_selected_idx = random.sample(nested_index_list, opts.sample_k//2)
            nested_selected_idx.sort()

            assert len(flat_index_list) == len(nested_index_list) == opts.sample_k//2

            print("Evaluation begining ...")
            i = 0
            for idx_list in [flat_index_list, nested_index_list]:
                for idx in idx_list:
                    i += 1
                    example = data[idx]
                    prompts = "Considering {} types of named entities including {} and {}, now recognize all entities in the following sentence with the format 'entity_type: entity_name': {}".format(len(e_types), ", ".join(e_types[:-1]), e_types[-1], example['seq'])

                    bot.new_conversation()
                    response = asyncio.run(bot.ask(prompts))
                    asyncio.run(bot.delete_conversation())

                    print("[{}|{}]".format(i, idx), prompts)
                    print("[response]:", response)

                    result_dict = dict()
                    result_dict.update(example)
                    result_dict.update({
                        "response": response
                    })

                    fw.write(json.dumps(result_dict, indent=4, ensure_ascii=False)) 
                    fw.write("\n\n")


if __name__ == "__main__":
    opts = get_opts()

    bot = ChatGPT()
    asyncio.run(bot.refresh_session())

    if opts.task == "ner":
        ner_main(opts, bot)

