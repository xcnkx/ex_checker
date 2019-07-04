import pandas as pd
import os
import datetime
import zipfile
import re
import traceback


def check_sub_id(ex_number):
    for fn in files:
        if -1 != fn.find(ex_number):
            s_fname = fn.split("_")
            submitted_fnames.update({s_fname[0]: fn})


def check_exfiles(file_name):
    id = file_name.split("_")
    x = []
    print(path + '/' + file_name)
    with zipfile.ZipFile(path + '/' + file_name) as existing_zip:
        files_n = 0
        for name in existing_zip.namelist():
            m = re.findall(r'ex[0-9]*/p[0-9]*/\w*.pdf$', str(name).lower())
            # m = re.findall(r"ex[0-9]*/\w*.pdf$", str(.name).lower())

            if m:
                files_n += 1
        x.append(files_n)

    x.append(id[0])
    if files_n != p_n:
        err_std.append(id[0])
    return x


def request_ex_folder():
    print("Input the path to the folder which has the uploaded ex files (ex:\"./uploaded\").")
    print("path : ", end='')
    global path
    path = input()


def do_request():
    global files
    try:
        request_ex_folder()
        files = os.listdir(path)
    except:
        traceback.print_exc()
        print('\n')
        do_request()
        pass


do_request()

names = []
submitted_fnames = {}
ids = []
ex = []
submitted_list = []
err_std = []

print("Input the Exercise number that you want to check and it's Problems numbers (ex: \"Ex1\" 1).")
print("Ex number & P numbers: ", end='')

epn = input().split()
ex_n = epn[0]
p_n = float(epn[1])

check_sub_id(ex_n)
print(ex_n)
ex_n = ex_n[2:]

c_name = "Ex. " + ex_n + ": Sub"

print("Input the date of the sheet \"std6_YenClass\" that you want to overwrite. (ex: YYYY-MM-DD)")
print("Sheet date: ", end='')

sheet_name = "std6_YenClass_" + input() + ".xlsx"

df = pd.read_excel("./sheets/"+sheet_name)

for i in submitted_fnames.values():
    sub_id = check_exfiles(i)
    score = sub_id[0] / p_n
    df.loc[df['ID'] == sub_id[1], c_name] = score

df.loc[df[c_name].isnull(), c_name] = 0

date = datetime.date.today()

f_name = "./std6_YenClass_" + str(date) + "_auto_created" ".xlsx"
df.to_excel('.sheets/' + f_name, index=False)

print("The new " + f_name + " file was created")

print("Number of Students which has submitted this exercise:" + str(len(submitted_fnames)))

print("Students that may be checked:")

for j in err_std:
    print("Student ID: " + j)
    with zipfile.ZipFile(path + '/' + submitted_fnames[j]) as existing_zip:
        print(existing_zip.namelist())
