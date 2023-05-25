# # sent/conll04
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-conll04.json
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/conll04 --result_file re_rc_type_result_5.json --prompt 5 --ICL


# # # sent/nyt-multi
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-nyt-multi.json
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/nyt-multi --result_file re_rc_type_result_5.json --prompt 5 --ICL


# # # sent/tacred
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-tacred.json
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/tacred --result_file re_rc_type_result_5.json --prompt 5 --ICL


# # # sent/semeval2010
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-semeval2010.json
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/semeval2010 --result_file re_rc_result_5.json --prompt 5 --ICL


# # # sent/re-tacred
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-re-tacred.json
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/re-tacred --result_file re_rc_type_result_5.json --prompt 5 --ICL


# # sent/pgr
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-pgr.json
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/pgr --result_file re_rc_result_5.json --prompt 5 --ICL

# # sent/cpr
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-sent-cpr.json
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset sent/cpr --result_file re_rc_type_result_5.json --prompt 5 --ICL

# # doc/docred
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-doc-docred.json
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/docred --result_file re_rc_type_result_5.json --prompt 5 --ICL

# # doc/re-docred
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-doc-re-docred.json
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/re-docred --result_file re_rc_type_result_5.json --prompt 5 --ICL

# # doc/dwie
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-doc-dwie.json
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/dwie --result_file re_rc_type_result_5.json --prompt 5 --ICL

# # doc/cdr
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-doc-cdr.json
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/cdr --result_file re_rc_type_result_5.json --prompt 5 --ICL

# # doc/gda
python remove_metric_file.py --task re --result_dir ./result --metric_file re-rc-metric-doc-gda.json
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_1.json --prompt 1
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_2.json --prompt 2
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_3.json --prompt 3
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_4.json --prompt 4
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_5.json --prompt 5

python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_1.json --prompt 1 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_2.json --prompt 2 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_3.json --prompt 3 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_4.json --prompt 4 --ICL
python ./2_RE/re_rc_report_metric.py --dataset doc/gda --result_file re_rc_type_result_5.json --prompt 5 --ICL


