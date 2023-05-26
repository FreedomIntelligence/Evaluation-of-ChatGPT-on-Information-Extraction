python ./1_NER/analyze_head_tail.py --dataset fewnerd --result_file ner_result_1.json --verbose_type --prompt 1 --threshold_head_tail 2000
python ./1_NER/analyze_head_tail.py --dataset fewnerd --result_file ner_result_2.json --verbose_type --prompt 2 --threshold_head_tail 2000
python ./1_NER/analyze_head_tail.py --dataset fewnerd --result_file ner_result_3.json --verbose_type --prompt 3 --threshold_head_tail 2000
python ./1_NER/analyze_head_tail.py --dataset fewnerd --result_file ner_result_4.json --verbose_type --prompt 4 --threshold_head_tail 2000
python ./1_NER/analyze_head_tail.py --dataset fewnerd --result_file ner_result_5.json --verbose_type --prompt 5 --threshold_head_tail 2000


python ./1_NER/analyze_head_tail.py --dataset ace2005 --result_file ner_result_1.json --verbose_type --prompt 1 --threshold_head_tail 1000
python ./1_NER/analyze_head_tail.py --dataset ace2005 --result_file ner_result_2.json --verbose_type --prompt 2 --threshold_head_tail 1000
python ./1_NER/analyze_head_tail.py --dataset ace2005 --result_file ner_result_3.json --verbose_type --prompt 3 --threshold_head_tail 1000
python ./1_NER/analyze_head_tail.py --dataset ace2005 --result_file ner_result_4.json --verbose_type --prompt 4 --threshold_head_tail 1000
python ./1_NER/analyze_head_tail.py --dataset ace2005 --result_file ner_result_5.json --verbose_type --prompt 5 --threshold_head_tail 1000


python ./2_RE/re_rc_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_rc_type_result_1.json --prompt 1 --threshold_head_tail 500
python ./2_RE/re_rc_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_rc_type_result_2.json --prompt 2 --threshold_head_tail 500
python ./2_RE/re_rc_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_rc_type_result_3.json --prompt 3 --threshold_head_tail 500
python ./2_RE/re_rc_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_rc_type_result_4.json --prompt 4 --threshold_head_tail 500
python ./2_RE/re_rc_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_rc_type_result_5.json --prompt 5 --threshold_head_tail 500

python ./2_RE/re_triplet_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_triplet_result_1.json --prompt 1 --threshold_head_tail 500
python ./2_RE/re_triplet_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_triplet_result_2.json --prompt 2 --threshold_head_tail 500
python ./2_RE/re_triplet_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_triplet_result_3.json --prompt 3 --threshold_head_tail 500
python ./2_RE/re_triplet_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_triplet_result_4.json --prompt 4 --threshold_head_tail 500
python ./2_RE/re_triplet_analyze_head_tail.py --dataset sent/nyt-multi --result_file re_triplet_result_5.json --prompt 5 --threshold_head_tail 500


python ./3_EE/ee_trigger_analyze_head_tail.py --dataset ace05 --result_file ee_trigger_result_1.json --prompt 1 --threshold_head_tail 50
python ./3_EE/ee_trigger_analyze_head_tail.py --dataset ace05 --result_file ee_trigger_result_2.json --prompt 2 --threshold_head_tail 50
python ./3_EE/ee_trigger_analyze_head_tail.py --dataset ace05 --result_file ee_trigger_result_3.json --prompt 3 --threshold_head_tail 50
python ./3_EE/ee_trigger_analyze_head_tail.py --dataset ace05 --result_file ee_trigger_result_4.json --prompt 4 --threshold_head_tail 50
python ./3_EE/ee_trigger_analyze_head_tail.py --dataset ace05 --result_file ee_trigger_result_5.json --prompt 5 --threshold_head_tail 50

python ./3_EE/ee_argument_analyze_head_tail.py --dataset ace05 --result_file ee_argument_result_1.json --prompt 1 --threshold_head_tail 50
python ./3_EE/ee_argument_analyze_head_tail.py --dataset ace05 --result_file ee_argument_result_2.json --prompt 2 --threshold_head_tail 50
python ./3_EE/ee_argument_analyze_head_tail.py --dataset ace05 --result_file ee_argument_result_3.json --prompt 3 --threshold_head_tail 50
python ./3_EE/ee_argument_analyze_head_tail.py --dataset ace05 --result_file ee_argument_result_4.json --prompt 4 --threshold_head_tail 50
python ./3_EE/ee_argument_analyze_head_tail.py --dataset ace05 --result_file ee_argument_result_5.json --prompt 5 --threshold_head_tail 50

python ./3_EE/ee_joint_analyze_head_tail.py --dataset ace05 --result_file ee_joint_result_1.json --prompt 1 --threshold_head_tail 50
python ./3_EE/ee_joint_analyze_head_tail.py --dataset ace05 --result_file ee_joint_result_2.json --prompt 2 --threshold_head_tail 50
python ./3_EE/ee_joint_analyze_head_tail.py --dataset ace05 --result_file ee_joint_result_3.json --prompt 3 --threshold_head_tail 50
python ./3_EE/ee_joint_analyze_head_tail.py --dataset ace05 --result_file ee_joint_result_4.json --prompt 4 --threshold_head_tail 50
python ./3_EE/ee_joint_analyze_head_tail.py --dataset ace05 --result_file ee_joint_result_5.json --prompt 5 --threshold_head_tail 50