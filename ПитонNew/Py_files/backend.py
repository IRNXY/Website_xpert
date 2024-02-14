import sqlite3
import pymorphy3
from flask import Flask, request, render_template

# передаём жедаемое количество колонок(n) и сами данные
def forming_n_in_row(n, data):
    result = []
    preparing = []
    for inf in enumerate(data):
        # проходимся по списку data и складируем элементы в preparing. На каждом n элементе переносим промежуточный список в result
        if (inf[0] + 1) % n == 0:
            preparing.append(inf[1][0])
            preparing.append(inf[1][1])
            result.append(preparing)
            preparing = []
        else:
            preparing.append(inf[1][0])
            preparing.append(inf[1][1])
    # позвращаем матрицу шириной n
    return result

def search(line):
    product_input = line

    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

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
        arg_product_type = cur.execute("""SELECT id FROM xpertools_type 
                                            WHERE type = '{0}' """.format(arg_product_type)).fetchall()[0][0]
    except Exception:
        arg_name.append(arg_product_type)
        arg_product_type = ''

    answ = []
    if len(arg_name) > 0:
        if arg_product_type != '':
            for i in arg_name:
                product_name = cur.execute("""SELECT name, id
                                                     FROM xpertools 
                                                      WHERE product_type = '{0}' AND name LIKE '%{2}%' """.format(
                    arg_product_type, arg_product_type_adjf, i)).fetchall()
                for i in product_name:
                    answ.append(i)
        else:
            for i in arg_name:
                product_name = cur.execute("""SELECT name, id
                                                        FROM xpertools 
                                                        WHERE name LIKE '%{1}%' AND name LIKE '%{0}%' """.format(
                    arg_product_type_adjf, i)).fetchall()
                for i in product_name:
                    answ.append(i)
    else:
        product_name = cur.execute("""SELECT name, id
                                                FROM xpertools 
                                                WHERE product_type = ? """, (arg_product_type,)).fetchall()
        for i in product_name:
            answ.append(i)

    return answ

app = Flask(__name__)

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        product_input = request.form['products'].split()

        goods = search(product_input)

        answ = forming_n_in_row(2, goods)

        return render_template('index.html', product=answ)
    else:
        return render_template('index.html', product=[])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/item/<username>')
def user_profile(username):
    return f"Это профиль пользователя {username}"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # проверка логина и пароля
        print(username, password)
        return 'Вы вошли в систему!'
    else:
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)