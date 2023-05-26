# sent/conll04
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/conll04 --test_file test.json \
--result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# sent/nyt-multi
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/nyt-multi --test_file test_3k.json \
--result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/nyt-multi --test_file test_3k.json \
--result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/nyt-multi --test_file test_3k.json \
--result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/nyt-multi --test_file test_3k.json \
--result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/nyt-multi --test_file test_3k.json \
--result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# sent/tacred
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/tacred --test_file test_3k.json \
--result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/tacred --test_file test_3k.json \
--result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/tacred --test_file test_3k.json \
--result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/tacred --test_file test_3k.json \
--result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/tacred --test_file test_3k.json \
--result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# # # sent/re-tacred
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/re-tacred --test_file test_3k.json \
# # --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/re-tacred --test_file test_3k.json \
# # --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/re-tacred --test_file test_3k.json \
# # --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/re-tacred --test_file test_3k.json \
# # --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/re-tacred --test_file test_3k.json \
# # --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# # sent/semeval2010
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
# # --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
# # --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
# # --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
# # --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/semeval2010 --test_file test.json \
# # --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# # # sent/pgr
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/pgr --test_file test.json \
# # --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/pgr --test_file test.json \
# # --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/pgr --test_file test.json \
# # --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/pgr --test_file test.json \
# # --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/pgr --test_file test.json \
# # --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# # # sent/cpr
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/cpr --test_file test_3k.json \
# # --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/cpr --test_file test_3k.json \
# # --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/cpr --test_file test_3k.json \
# # --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/cpr --test_file test_3k.json \
# # --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset sent/cpr --test_file test_3k.json \
# # --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json



# # doc/cdr
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/cdr --test_file test.json \
# # --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/cdr --test_file test.json \
# # --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/cdr --test_file test.json \
# # --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# # python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/cdr --test_file test.json \
# # --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/cdr --test_file test.json \
# --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# # doc/gda
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/gda --test_file test.json \
# --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/gda --test_file test.json \
# --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/gda --test_file test.json \
# --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/gda --test_file test.json \
# --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/gda --test_file test.json \
# --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc.json

# # doc/docred
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/docred --test_file dev.json \
# --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/docred --test_file dev.json \
# --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/docred --test_file dev.json \
# --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/docred --test_file dev.json \
# --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/docred --test_file dev.json \
# --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json

# # doc/re-docred
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/re-docred --test_file test.json \
# --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/re-docred --test_file test.json \
# --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/re-docred --test_file test.json \
# --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/re-docred --test_file test.json \
# --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/re-docred --test_file test.json \
# --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json

# # doc/dwie
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/dwie --test_file test.json \
# --result_file new_re_rc_result_1.json --prompt 1 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/dwie --test_file test.json \
# --result_file new_re_rc_result_2.json --prompt 2 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/dwie --test_file test.json \
# --result_file new_re_rc_result_3.json --prompt 3 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/dwie --test_file test.json \
# --result_file new_re_rc_result_4.json --prompt 4 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
# python ./2_RE/re_rc_test_with_api.py --api_key api-key.txt --dataset doc/dwie --test_file test.json \
# --result_file new_re_rc_result_5.json --prompt 5 --multi_thread --num_thread 10 --ICL --icl_prompt prompt_icl_rc_1.json
