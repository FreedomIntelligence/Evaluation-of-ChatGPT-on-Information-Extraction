import argparse, os

def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, default="api-key.txt")
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo-0301")
    parser.add_argument('--task', type=str, default="absa")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="pengb/14lap")
    parser.add_argument('--test_file', type=str, default="test_convert.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--prompt_dir', type=str, default="./4_ABSA/prompt")
    parser.add_argument('--basic_prompt', type=str, default="absa_prompt.json")
    parser.add_argument('--icl_prompt', type=str, default="prompt_icl.json")
    parser.add_argument('--cot_prompt', type=str, default="prompt_cot.json")
    parser.add_argument('--sample_k', type=int, default=50)
    parser.add_argument('--sample', action='store_true', default=False)
    parser.add_argument('--soft_match', action='store_true', default=False)  # hard-matching or soft-matching
    parser.add_argument('--ICL', action='store_true', default=False)
    parser.add_argument('--COT', action='store_true', default=False)
    parser.add_argument('--prompt', type=int, default=1)
    parser.add_argument('--best_prompt', type=int, default=1)
    parser.add_argument('--multi_thread', action='store_true', default=False)
    parser.add_argument('--num_thread', type=int, default=10)
    parser.add_argument('--irrelevant', action='store_true', default=False)

    # report metric
    parser.add_argument('--result_file', type=str, default="test_convert_result.json")
    opts = parser.parse_args()

    log_dir = os.path.join("./logs", opts.task)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return opts
