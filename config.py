import argparse

def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default="absa")
    parser.add_argument('--input_dir', type=str, default="./data")
    parser.add_argument('--dataset', type=str, default="wang/14lap")
    parser.add_argument('--test_file', type=str, default="test_convert.json")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--sample_k', type=int, default=50)
    parser.add_argument('--sample', action='store_true', default=False)

    # report metric
    parser.add_argument('--report_metric_file', type=str, default="test_convert_result.json")
    opts = parser.parse_args()
    return opts