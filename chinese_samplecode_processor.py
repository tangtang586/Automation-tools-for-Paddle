import math
import os
import pickle
import shutil
import subprocess
import multiprocessing
import sys

# 删除文件中被" code-block:: python"标记的代码描述信息
def remove_desc_code(srcls, filename):
    if filename == './fluid_cn/one_hot_cn.rst':
        srcls.pop(13)
        srcls.pop(28)
        srcls.pop(44)
    if filename == './layers_cn/one_hot_cn.rst':
        srcls.pop(15)
        srcls.pop(30)
        srcls.pop(46)
    if filename == './profiler_cn/profiler_cn.rst':
        srcls.pop(41)
    if filename == './layers_cn/natural_exp_decay_cn.rst':
        srcls.pop(13)
    if filename == './layers_cn/transpose_cn.rst':
        srcls.pop(20)
    if filename == './layers_cn/array_length_cn.rst':
        srcls.pop(36)
    if filename == './layers_cn/inverse_time_decay_cn.rst':
        srcls.pop(13)
    if filename == './layers_cn/stack_cn.rst':
        srcls.pop(12)
        srcls.pop(33)
    if filename == './layers_cn/sums_cn.rst':
        srcls.pop(11)
    if filename == './layers_cn/sum_cn.rst':
        for i in range(len(srcls)-1, 61, -1):
            srcls.pop(i)
    if filename == './layers_cn/softmax_cn.rst':
        srcls.pop(30)
        srcls.pop(57)
    if filename == './layers_cn/array_write_cn.rst':
        srcls.pop(37)
    if filename == './layers_cn/lod_append_cn.rst':
        srcls.pop(11)
    if filename == './layers_cn/reorder_lod_tensor_by_rank_cn.rst':
        srcls.pop(25)
    if filename == './layers_cn/round_cn.rst':
        srcls.pop(10)
    if filename == './layers_cn/squeeze_cn.rst':
        srcls.pop(11)
        srcls.pop(19)
        srcls.pop(27)
    if filename == './layers_cn/unsqueeze_cn.rst':
        srcls.pop(11)
    if filename == './layers_cn/array_read_cn.rst':
        srcls.pop(51)
    if filename == './layers_cn/scatter_cn.rst':
        srcls.pop(9)
    if filename == './layers_cn/topk_cn.rst':
        srcls.pop(11)
    if filename == './optimizer_cn/ModelAverage_cn.rst':
        srcls.pop(15)
    return srcls




def check_indent(code_line):
    indent = ""
    for c in code_line:
        if c == '\t':
            indent += '    '
        elif c == ' ':
            indent += ' '
        if c != ' ' and c != '\t':
            break
    return indent


# theses files' apis will connect server, causing process wait ,so remove them
def removeSomeApis(filenames):
    filenames.remove('./fluid_cn/DistributeTranspiler_cn.rst')
    filenames.remove('./transpiler_cn/DistributeTranspiler_cn.rst')
    filenames.remove('./transpiler_cn/DistributeTranspilerConfig_cn.rst')
    filenames.remove('./transpiler_cn/HashName_cn.rst')
    filenames.remove('./transpiler_cn/memory_optimize_cn.rst')
    filenames.remove('./transpiler_cn/release_memory_cn.rst')
    filenames.remove('./transpiler_cn/RoundRobin_cn.rst')
    # avoid deleting list elements while iterating, one solution we can delete from tail
    for i in range(len(filenames) - 1, -1, -1):
        length = len(filenames[i].split("/"))
        if length == 2:
            filenames.pop(i)
    return filenames


def find_all(src_str, substr):
    indices = []
    get_one = src_str.find(substr)
    while get_one != -1:
        indices.append(get_one)
        get_one = src_str.find(substr, get_one + 1)
    return indices


def extract_sample_code(srcfile, status_all):
    filename = srcfile.name
    # to debug
    # print(filename)
    srcc = srcfile.read()
    srcfile.seek(0, 0)
    srcls = srcfile.readlines()
    # remove description info for samplecode
    srcls = remove_desc_code(srcls, filename)
    status = []
    sample_code_begins = find_all(srcc, " code-block:: python")
    if len(sample_code_begins) == 0:
        status.append(-1)

    else:
        for i in range(0, len(srcls)):
            if srcls[i].find(".. code-block:: python") != -1:
                content = ""
                start = i

                blank_line = 1
                while srcls[start + blank_line].strip() == '':  # or if not len(srcls[start + blank_line].strip()):
                    blank_line += 1

                startindent = ""
                # remove indent error
                if srcls[start + blank_line].find("from") != -1:
                    startindent += srcls[start + blank_line][:srcls[start + blank_line].find("from")]
                elif srcls[start + blank_line].find("import") != -1:
                    startindent += srcls[start + blank_line][:srcls[start + blank_line].find("import")]
                else:
                    startindent += check_indent(srcls[start + blank_line])
                content += srcls[start + blank_line][len(startindent):]
                for j in range(start + blank_line + 1, len(srcls)):
                    # planish a blank line
                    if not srcls[j].startswith(startindent) and srcls[j] != '\n':
                        break
                    if srcls[j].find(" code-block:: python") != -1:
                        break
                    content += srcls[j].replace(startindent, "", 1)
                status.append(run_sample_code(content, filename))

    status_all[filename] = status
    return status_all


def run_sample_code(content, filename):
    # three status ,-1:no sample code; 1: running error; 0:normal
    fname = filename.split("/")[-1].replace("_cn", "").replace(".rst", "") + ".py"
    tempf = open("temp/" + fname, 'w')
    tempf.write(content)
    tempf.close()
    # cmd = ["/opt/anaconda3/envs/paddle_env/bin/python3.7", "temp/" + fname]
    cmd = ["python", "temp/" + fname]

    subprc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, error = subprc.communicate()
    err = "".join(error.decode(encoding='utf-8'))

    if subprc.returncode != 0:
        print("\nSample code error found in ", filename, ":\n")
        print("subprocess return code: ", str(subprc.returncode))
        print("Error Raised from Sample Code  content:\n", content, " :\n")
        print(err)
        status = 1
    else:
        status = 0
    os.remove("temp/" + fname)
    return status


def test(file_list):
    res_status = []
    for file in file_list:
        src = open(file, 'r')
        status_all = {}
        extract_sample_code(src, status_all)
        res_status.append(status_all)
        src.close()
    return res_status


# 这么做的原因是如果后续新增了需要连接远程服务器的api，进程会一直尝试连接服务器，卡死
# 进而导致临时目录temp里的文件未删除，建议api里面设置超时时长控制
# 目的是为了消除程序上次非正常结果对于下次程序运行的影响；
if os.path.isdir("temp"):
    shutil.rmtree("temp")
    # os.mkdir("temp")

# 删除api产生的模型文件和图像文件等
if os.path.isdir("infer_model"):
    shutil.rmtree("infer_model")
if os.path.isdir("image"):
    shutil.rmtree("image")
if os.path.isdir("my_paddle_model"):
    shutil.rmtree("my_paddle_model")
if os.path.isdir("my_paddle_vars"):
    shutil.rmtree("my_paddle_vars")

if not os.path.isdir("temp"):
    os.mkdir("temp")

filenames = []
for root, dirs, files in os.walk("."):
    for f in files:
        filenames.append(os.path.join(root, f))

# 这里删除不是api的文件（包括描述api目录的文件 和运行程序产生的文件）和 api文件中需要连接远程服务器的，会导致进程一直try，处于wait状态
filenames = removeSomeApis(filenames)

# convenient to debug
# filenames.remove('./chinese_samplecode_processor.py')
# filenames = filenames[21:]
# filenames = filenames[24:]
# print(filenames)
# sys.exit(0)
# filenames = ['./fluid_cn/DataFeeder_cn.rst']
# filenames = ['./fluid_cn/program_guard_cn.rst']
# filenames = ['./backward_cn/append_backward_cn.rst']




one_part_filenames = int(math.ceil(len(filenames) / 10))
divided_file_list = [
    filenames[i:i + one_part_filenames]
    for i in range(0, len(filenames), one_part_filenames)
]

# calculate the total nums of sample demos
total_api_num = 0

po = multiprocessing.Pool(10)
output = []

for file_list in divided_file_list:
    res = po.apply_async(test, (file_list,))
    output.append(res.get())

po.close()
po.join()

os.rmdir("temp")
# print(output)

status_groups = {-1: [], 0: [], 1: []}
# polishes show format
ci_pass = True
for one_file in output:
    for dicts in one_file:
        for key in dicts:
            status = dicts[key]
            for ele in status:
                if ele != 0:
                    ci_pass = False
                    break
            if len(status) == 1:
                status_groups[status[0]].append(key)
            else:
                for u in range(0, len(status)):
                    status_groups[status[u]].append(key + '_' + str(u + 1))

total_api = status_groups[-1] + status_groups[1] + status_groups[0]
error_api = status_groups[-1] + status_groups[1]

total_api_num = len(total_api)
total_error_number = len(error_api)

# 将不合规的api条目dump到文本中，再用开源xls处理框架写入xls，免于人工键入信息
# f = open("no_code.txt", "wb")
# pickle.dump(status_groups[-1], f)
# f.close()
#
f = open("error_code.txt", "wb")
pickle.dump(status_groups[1], f)
f.close()

print("****************************************************")
print("----------------End of the Check--------------------")
print("total number of sample api demos is:{}".format(total_api_num))
print("****************************************************")
if total_error_number > 0:
    print("Error sample code number is:{}".format(total_error_number))
    type_one_number = len(status_groups[-1])
    type_two_number = len(status_groups[1])
    if type_one_number > 0:
        print("Error type one sample number is:{}".format(type_one_number))
        print("Error raised from type one:no sample code.", str(status_groups[-1]))
    if type_two_number > 0:
        print("Error type two sample number is:{}".format(type_two_number))
        print("Error raised from type two:running error sample code.", str(status_groups[1]))
if not ci_pass:
    print("Mistakes found in sample codes.")
    exit(1)
else:
    print("Sample code check is successful!")
