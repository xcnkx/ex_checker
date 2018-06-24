import pandas as pd
import os
import datetime



print("Input the path to the folder wich has the uploaded ex files (ex:\"./uploaded\").")
print("path : ", end='')
path = input()

files = os.listdir(path)
names = []
id = []
ex = []
submitted_list = []

print("Input the Exercise number that you want to check (ex: \"Ex1\").")
print("Ex number : ", end='')

ex_n = input()

for file_name in files:
    names.append(file_name.split("_"))
for i in names:
    del i[1:3]
    if len(i) == 2:
        id.append(i)

for s_id in id:
    if ex_n in s_id[1]:
        submitted_list.append(s_id[0])

ex_n = ex_n[2:]

c_name = "Ex. " + ex_n + ": Sub"

print("Input the date of the sheet \"std6_YenClass\" that you want to overwrite. (ex: YYYY-MM-DD)")
print("Sheet date: ", end='')

sheet_name = "std6_YenClass_"+input()+".xlsx"

df = pd.read_excel(sheet_name)
for i in submitted_list:
    df.loc[df['ID'] == i, c_name] = 1
df.loc[df[c_name].isnull(), c_name] = 0


date = datetime.date.today()

f_name  = "./std6_YenClass_" + str(date) + ".xlsx"
df.to_excel(f_name,index = False)

print("The new "+f_name+" file was created")
