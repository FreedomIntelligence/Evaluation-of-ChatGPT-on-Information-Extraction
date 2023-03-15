import argparse, os

def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default="absa")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="pengb/14lap")
    parser.add_argument('--test_file', type=str, default="test_convert.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=50)
    parser.add_argument('--sample', action='store_true', default=False)
    parser.add_argument('--soft_match', action='store_true', default=False)  # hard-matching or soft-matching

    # report metric
    parser.add_argument('--report_metric_file', type=str, default="test_convert_result.json")
    opts = parser.parse_args()
    return opts


def get_opts_ner():
    parser = argparse.ArgumentParser()
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

    opts.logger_file = opts.task + "-" + opts.dataset
    if opts.coarse_grain:
        opts.logger_file += "-coarse"
    if opts.verbose_type:
        opts.logger_file += "-verbose"
    opts.logger_file += "-test.log"

    return opts



# python tests_with_api\report_metric_absa.py --dataset pengb/14lap --report_metric_file test_convert_result.json

# python tests_with_api\absa_test_with_api.py --dataset pengb/14lap --sample --sample_k 5

# python ner_test_with_api.py --task ner --dataset conll03 --test_file ner_test.json --sample --sample_k 10

# python ner_report_metric.py --report_metric_file ner_test_result_verbose.json --verbose_type