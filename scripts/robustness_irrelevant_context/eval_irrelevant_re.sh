# # sent/semeval2010
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
--result_file new_irrelevant_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
--result_file new_irrelevant_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
--result_file new_irrelevant_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
--result_file new_irrelevant_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
--result_file new_irrelevant_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --irrelevant

# sent/conll04
python ./2_RE/re_triplet_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_irrelevant_re_triplet_result_1.json --prompt 1 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_triplet_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_irrelevant_re_triplet_result_2.json --prompt 2 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_triplet_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_irrelevant_re_triplet_result_3.json --prompt 3 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_triplet_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_irrelevant_re_triplet_result_4.json --prompt 4 --multi_thread --num_thread 10 --irrelevant
python ./2_RE/re_triplet_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_irrelevant_re_triplet_result_5.json --prompt 5 --multi_thread --num_thread 10 --irrelevant