import sqlite3
from docx import Document
import pymorphy3
from pprint import pprint
import csv


con = sqlite3.connect("DataBase/tution.db")
cur = con.cursor()

product_input = input().split()

# подключаем морф чтобы определять часть речи
morph = pymorphy3.MorphAnalyzer()

# ключи для поика
arg_product_type = ''
arg_product_type_adjf = ''
arg_name = []

# проходим по каждому слову из строки
for i in range(len(product_input)):
    word = product_input[i]
    # существительное в большенстве случаев является видом товара
    if word.isalpha() and "NOUN" in morph.parse(word.lower())[0].tag and arg_product_type == '':
        arg_product_type = morph.parse(word)[0].inflect({'plur'}).word
    # прилагательное в большинстве случаев является подвидом товара
    elif "ADJF" in morph.parse(word.lower())[0].tag:
        arg_product_type_adjf = morph.parse(word)[0].normal_form
    # разделяем все слова на содержащие спецсимволы и цифры и на обычные слова
    else:
        arg_name.append(word)

try:
    arg_product_type = cur.execute("""SELECT id FROM xpertools_type WHERE type = '{0}' """.format(arg_product_type, )).fetchall()[0][0]
except Exception:
    arg_name.append(arg_product_type)
    arg_product_type = ''
# print(arg_name, arg_product_type_adjf, arg_product_type)
answ = []
if len(arg_name) > 0:
    if arg_product_type != '':
        for i in arg_name:
            product_name = cur.execute("""SELECT id, name FROM xpertools WHERE product_type = '{0}' AND name LIKE '%{2}%' """.format(arg_product_type, arg_product_type_adjf, i)).fetchall()
            for i in product_name:
                answ.append(i)
    else:
        for i in arg_name:
            product_name = cur.execute("""SELECT id, name FROM xpertools WHERE name LIKE '%{1}%' AND name LIKE '%{0}%' """.format( arg_product_type_adjf, i)).fetchall()
            for i in product_name:
                answ.append(i)
else:
    product_name = cur.execute("""SELECT name FROM xpertools WHERE product_type = ? """, (arg_product_type,)).fetchall()
    for i in product_name:
        answ.append(i)
pprint(answ)

# con.commit()
con.close()








