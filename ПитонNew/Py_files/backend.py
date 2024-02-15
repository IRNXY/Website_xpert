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

def search_by_input(line):
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
        if arg_product_type != '':
            arg_name.append(arg_product_type)
            arg_product_type = ''

    # print(arg_name, arg_product_type, arg_product_type_adjf)

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


def search_by_id(id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id FROM xpertools WHERE product_type = ?""", (id,)).fetchall()
    return need

def get_categories():
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    need = cur.execute("""SELECT type, id FROM xpertools_type""").fetchall()
    return need


app = Flask(__name__)


@app.route('/base',)
def base():
    return render_template('base.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(2, goods)
        return render_template('caralog_page.html', product=answ)
    else:
        return render_template('index.html', product=[])


@app.route("/catalog", methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(2, goods)
        return render_template('caralog_page.html', product=answ)
    else:
        answ = get_categories()
        answ = forming_n_in_row(3, answ)
        return render_template('catalog.html', categories=answ)


@app.route('/catalog/<name>', methods=['GET', 'POST'])
def catalog_named(name):
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    else:
        goods = search_by_id(name.split()[1])
        goods = forming_n_in_row(2, goods)
        return render_template('catalog_page.html', product=goods)


@app.route('/item/<name>', methods=['GET', 'POST'])
def item(name):
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    else:

        return name


if __name__ == '__main__':
    app.run(debug=True)