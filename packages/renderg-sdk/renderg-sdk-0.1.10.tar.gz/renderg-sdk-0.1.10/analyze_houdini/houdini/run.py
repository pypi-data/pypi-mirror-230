# coding=utf-8

import sys
import os

current_file = os.path.dirname(__file__)
sys.path.insert(0, current_file)

try:
    import HoudiniAnalyze
except:
    try:
        import HoudiniAnalyze_py37 as HoudiniAnalyze
    except:
        import HoudiniAnalyze_py39 as HoudiniAnalyze

args = sys.argv

cmd_input = '-input'
cmd_output = '-output'


if cmd_input in args:
    cg_file_flag = args.index(cmd_input)
    hip_file = args[cg_file_flag + 1]

if cmd_output in args:
    path_json_flag = args.index(cmd_output)
    json_file = args[path_json_flag + 1]


param_dict = {
    "hip_path": hip_file,
    "output_path": json_file,
}

HoudiniAnalyze.HoudiniAnalyze(param_dict)
