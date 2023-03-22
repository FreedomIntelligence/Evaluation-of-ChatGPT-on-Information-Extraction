## ABSA

python absa_test_with_api.py --api_key api-key-1.txt --model gpt-3.5-turbo-0301 --result_file test_convert_result_0319.json --dataset fan/14lap

python absa_report_metric.py --result_file test_convert_result.json --dataset fan/14lap 
## NER 


### conll03:
python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset conll03 --test_file ner_test.json --result_file ner_test_result.json --verbose_type

python ner_report_metric.py --dataset conll03 --result_file ner_test_result_turbo.json --verbose_type
python ner_report_metric.py --dataset conll03 --result_file ner_test_result_misc.json --verbose_type

### fewnerd

python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset fewnerd --test_file ner_test.json --result_file ner_test_result_1.json --coarse_grain --sample --sample_k 1882
python ner_report_metric.py --dataset fewnerd --result_file ner_test_result.json --coarse_grain

python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset fewnerd --test_file ner_test.json --result_file ner_test_result_1.json --sample --sample_k 1882
python ner_report_metric.py --dataset fewnerd --result_file ner_test_result.json

### ace
python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset ace2004 --result_file ner_test_result_1.json
python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset ace2004 --verbose_type --result_file ner_test_result_1.json

python ner_report_metric.py --dataset ace2004 --result_file ner_test_result.json
python ner_report_metric.py --dataset ace2004 --result_file ner_test_result.json --verbose_type

python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset ace2005 --result_file ner_test_result_1.json
python ner_test_with_api.py --api_key api-key.txt --model gpt-3.5-turbo-0301 --dataset ace2005 --verbose_type --result_file ner_test_result_1.json

python ner_report_metric.py --dataset ace2005 --result_file ner_test_result.json
python ner_report_metric.py --dataset ace2005 --result_file ner_test_result.json --verbose_type


### genia
python ner_test_with_api.py --api_key api-key-2.txt --model gpt-3.5-turbo-0301 --dataset genia --verbose_type

python ner_report_metric.py --dataset genia --result_file ner_test_result.json --verbose_type


## RE

### RC

python re_rc_test_with_api.py --result_file re_rc_test_result.json --dataset sent/conll04

python re_report_metric.py --dataset sent/conll04