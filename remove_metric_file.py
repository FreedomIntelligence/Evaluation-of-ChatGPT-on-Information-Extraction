import os
import argparse

def config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default="absa")
    parser.add_argument('--result_dir', type=str, default="./result")
    parser.add_argument('--metric_file', type=str, default="metric_result.json")
    opts = parser.parse_args()

    return opts


def clear(opts):
    dump_metric_file = os.path.join(os.path.join(opts.result_dir, opts.task), opts.metric_file)
    fw = open(dump_metric_file, "w", encoding="utf-8") 
    fw.seek(0)  # 定位
    fw.truncate()  # 清空文件

if __name__ == "__main__":
    opts = config()
    clear(opts)