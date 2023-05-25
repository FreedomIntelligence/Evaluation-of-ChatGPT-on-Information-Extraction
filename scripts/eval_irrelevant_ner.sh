# python ner_test_with_api.py --api_key key-120-4.txt --dataset conll03 --test_file ner_test.json --type_file types.json \
# --verbose_type --result_file irrelevant_ner_result_1.json --prompt 1 --irrelevant
# conll03
python ner_test_with_api.py --api_key key-120-4.txt --dataset conll03 --test_file ner_test.json --type_file types.json \
--verbose_type --result_file irrelevant_ner_result_1.json --prompt 1 --multi_thread --num_thread 10 --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset conll03 --test_file ner_test.json --type_file types.json \
--verbose_type --result_file irrelevant_ner_result_2.json --prompt 2 --multi_thread --num_thread 10 --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset conll03 --test_file ner_test.json --type_file types.json \
--verbose_type --result_file irrelevant_ner_result_3.json --prompt 3 --multi_thread --num_thread 10 --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset conll03 --test_file ner_test.json --type_file types.json \
--verbose_type --result_file irrelevant_ner_result_4.json --prompt 4 --multi_thread --num_thread 10 --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset conll03 --test_file ner_test.json --type_file types.json \
--verbose_type --result_file irrelevant_ner_result_5.json --prompt 5 --multi_thread --num_thread 10 --irrelevant

# ace05
python ner_test_with_api.py --api_key key-120-4.txt --dataset ace2005 --verbose_type \
--result_file irrelevant_ner_result_1.json --prompt 1 --multi_thread --num_thread 10  --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset ace2005 --verbose_type \
--result_file irrelevant_ner_result_2.json --prompt 2 --multi_thread --num_thread 10  --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset ace2005 --verbose_type \
--result_file irrelevant_ner_result_3.json --prompt 3 --multi_thread --num_thread 10  --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset ace2005 --verbose_type \
--result_file irrelevant_ner_result_4.json --prompt 4 --multi_thread --num_thread 10  --irrelevant
python ner_test_with_api.py --api_key key-120-4.txt --dataset ace2005 --verbose_type \
--result_file irrelevant_ner_result_5.json --prompt 5 --multi_thread --num_thread 10  --irrelevant
