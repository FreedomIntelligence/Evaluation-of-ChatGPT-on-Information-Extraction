## Evaluation-of-ChatGPT-on-Information-Extraction
An Evaluation of ChatGPT on Information Extraction task, including Named Entity Recognition (NER), Relation Extraction (RE), Event Extraction (EE) and Aspect-based Sentiment Analysis (ABSA).

* Paper: [Is Information Extraction Solved by ChatGPT? An Analysis of Performance, Evaluation Criteria, Robustness and Errors](https://arxiv.org/abs/2305.14450)

## Abstract

ChatGPT has stimulated the research boom in the field of large language models. In this paper, we assess the capabilities of ChatGPT from four perspectives including Performance, Evaluation Criteria, Robustness and Error Types. Specifically, we first evaluate ChatGPT's performance on 17 datasets with 14 IE sub-tasks under the zero-shot, few-shot and chain-of-thought scenarios, and find a huge performance gap between ChatGPT and SOTA results. Next, we rethink this gap and propose a soft-matching strategy for evaluation to more accurately reflect ChatGPT's performance. Then, we analyze the robustness of ChatGPT on 14 IE sub-tasks, and find that: 1) ChatGPT rarely outputs invalid responses; 2) Irrelevant context and long-tail target types greatly affect ChatGPT's performance; 3) ChatGPT cannot understand well the subject-object relationships in RE task. Finally, we analyze the errors of ChatGPT, and find that "unannotated spans" is the most dominant error type. This raises concerns about the quality of annotated data, and indicates the possibility of annotating data with ChatGPT. The data and code are released at Github site.


## Datasets, processed data, output result files 

All datasets, processed data and output result files are available at the [google drive](https://drive.google.com/drive/folders/1vvmXnWRUu_4y9lI89Xh3SkrfBIrGt3RL?usp=sharing), except [ACE04](https://catalog.ldc.upenn.edu/LDC2005T09), [ACE05](https://catalog.ldc.upenn.edu/LDC2006T06) and [TACRED](https://catalog.ldc.upenn.edu/LDC2018T24) raw datasets (for copyright reasons).

Download all the files, unzip them, and place them in the corresponding directories.


## Test with API

```
bash ./scripts/absa/eval.sh
bash ./scripts/ner/eval.sh
bash ./scripts/re/eval_rc.sh
bash ./scripts/re/eval_triplet.sh
bash ./scripts/ee/eval_trigger.sh
bash ./scripts/ee/eval_argument.sh
bash ./scripts/ee/eval_joint.sh
```
Before testing, you need to modify all ``--api_key`` and ``--result_file`` arguments in all ``*.sh `` scripts.


## Get Evaluation Metrics
```
bash ./scripts/absa/report.sh
bash ./scripts/ner/report.sh
bash ./scripts/re/report_rc.sh
bash ./scripts/re/report_triplet.sh
bash ./scripts/ee/report_trigger.sh
bash ./scripts/ee/report_argument.sh
bash ./scripts/ee/report_joint.sh
```
By default, the metrics are calculated based on our output result files at [Google Drive](https://drive.google.com/drive/folders/1vvmXnWRUu_4y9lI89Xh3SkrfBIrGt3RL?usp=sharing).

## Main results

![main results](./figs/main_result.png)

## Examples of prompts
![Zero-shot](./figs/zero-shot.png)
![Few-shot ICL](./figs/few-shot-ICL.png)
![Few-shot COT](./figs/few-shot-COT.png)

## Future Work

We will add the results and analysis of GPT-4.