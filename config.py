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
    parser.add_argument('--sample_k', type=int, default=50)
    parser.add_argument('--sample', action='store_true', default=False)
    parser.add_argument('--soft_match', action='store_true', default=False)  # hard-matching or soft-matching

    # report metric
    parser.add_argument('--result_file', type=str, default="test_convert_result.json")
    opts = parser.parse_args()
    return opts


def get_opts_ner():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, default="api-key.txt")
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo-0301")
    parser.add_argument('--task', type=str, default="ner")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="conll03")
    parser.add_argument('--test_file', type=str, default="ner_test.json")
    parser.add_argument('--type_file', type=str, default="types.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=0)
    parser.add_argument('--sample', action='store_true', default=False)
    parser.add_argument('--logger_file', type=str, default="")

    # report metric
    parser.add_argument('--result_file', type=str, default="ner_test_result.json")
    parser.add_argument('--coarse_grain', action='store_true', default=False)  # fewnerd 粗粒度
    parser.add_argument('--verbose_type', action='store_true', default=False)  # type 是否全写 
    # parser.add_argument('--soft_match', action='store_true', default=False)  # # hard-matching or soft-matching
    opts = parser.parse_args()

    ## output dir
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    if opts.coarse_grain:
        if opts.verbose_type:
            opts.result_file = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.result_file.split(".")[0] + "_coarse_verbose.json")))
        else:
            opts.result_file = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.result_file.split(".")[0] + "_coarse.json")))
        opts.type_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.type_file.split(".")[0] + "_coarse.json")))
        opts.test_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.test_file.split(".")[0] + "_coarse.json")))
    else:
        if opts.verbose_type:
            opts.result_file = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.result_file.split(".")[0] + "_verbose.json")))
        else:
            opts.result_file = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.result_file)))
        opts.type_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.type_file)))
        opts.test_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.test_file)))

    log_dir = os.path.join("./logs", opts.task)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    opts.logger_file = opts.task + "-" + opts.dataset
    if opts.coarse_grain:
        opts.logger_file += "-coarse"
    if opts.verbose_type:
        opts.logger_file += "-verbose"
    opts.logger_file += "-test.txt"

    return opts


def get_opts_re():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, default="api-key.txt")
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo-0301")
    parser.add_argument('--task', type=str, default="re")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="sent/conll04")
    parser.add_argument('--test_file', type=str, default="test.json")
    parser.add_argument('--type_file', type=str, default="types.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=0)
    parser.add_argument('--sample', action='store_true', default=False)
    parser.add_argument('--logger_file', type=str, default="")
    parser.add_argument('--order', action='store_true', default=False)  # 是否考虑 subject 和 object 的顺序

    # report metric
    parser.add_argument('--result_file', type=str, default="re_rc_test_result.json")
    # parser.add_argument('--soft_match', action='store_true', default=False)  # # hard-matching or soft-matching
    opts = parser.parse_args()

    ## output dir
    result_dir = os.path.join(opts.result_dir, os.path.join(opts.task, opts.dataset))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    log_dir = os.path.join("./logs", opts.task)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger_file = "-".join(opts.dataset.split("/")) + "-" + opts.result_file.split(".")[0] + ".txt"

    opts.result_file = os.path.join(opts.result_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.result_file)))
    opts.type_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.type_file)))
    opts.test_file = os.path.join(opts.input_dir, os.path.join(opts.task, os.path.join(opts.dataset, opts.test_file)))

    return opts
