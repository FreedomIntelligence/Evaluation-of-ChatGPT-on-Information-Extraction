import os, argparse


def get_opts_re():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, default="api-key.txt")
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo-0301")
    parser.add_argument('--task', type=str, default="re")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="sent/conll04")
    parser.add_argument('--train_file', type=str, default="train.json")
    parser.add_argument('--test_file', type=str, default="test.json")
    parser.add_argument('--type_file', type=str, default="types.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=0)
    parser.add_argument('--sample', action='store_true', default=False)
    parser.add_argument('--logger_file', type=str, default="")
    parser.add_argument('--order', action='store_true', default=False)  # 是否考虑 subject 和 object 的顺序
    parser.add_argument('--threshold_head_tail', type=int, default=500)

    parser.add_argument('--ICL', action='store_true', default=False)
    parser.add_argument('--COT', action='store_true', default=False)
    parser.add_argument('--prompt', type=int, default=1)
    parser.add_argument('--multi_thread', action='store_true', default=False)
    parser.add_argument('--num_thread', type=int, default=10)
    
    parser.add_argument('--icl_prompt', type=str, default="prompt_icl.json")
    parser.add_argument('--cot_prompt', type=str, default="prompt_cot.json")
    parser.add_argument('--best_prompt', type=int, default=1)
    parser.add_argument('--irrelevant', action='store_true', default=False)

    # report metric
    parser.add_argument('--result_file', type=str, default="re_rc_result.json")
    parser.add_argument('--metric_file', type=str, default="metric_result.json")
    opts = parser.parse_args()

    ## output dir
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    log_dir = os.path.join("./logs", opts.task)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if opts.ICL:
        opts.logger_file += "ICL-"
    if opts.COT:
        opts.logger_file += "COT-"

    opts.logger_file += "-".join(opts.dataset.split("/")) + "-" + opts.result_file.split(".")[0] + ".txt"

    if opts.ICL:
        res_file = "ICL-" + opts.result_file
    elif opts.COT:
        res_file = "COT-" + opts.result_file
    else:
        res_file = opts.result_file
    opts.result_file = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, res_file)))
    opts.type_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.type_file)))
    opts.test_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.test_file)))

    return opts