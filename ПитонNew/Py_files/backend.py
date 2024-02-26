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
    if len(preparing) > 0:
        result.append(preparing)
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

def search_sale_prod(num_of_prod):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id FROM xpertools WHERE on_sale = 1""").fetchall()
    return need[:num_of_prod]

def search_by_id(id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id FROM xpertools WHERE id = ?""", (id,)).fetchall()
    return need

def search_by_type(type):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id FROM xpertools WHERE product_type = ?""", (type,)).fetchall()
    return need

def get_categories():
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    need = cur.execute("""SELECT type, id FROM xpertools_type""").fetchall()
    return need


list_product_bin = dict()

app = Flask(__name__)


@app.route('/base',)
def base():
    return render_template('base.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    else:
        cat = get_categories()
        cat = forming_n_in_row(5, cat)

        sal = search_sale_prod(4)
        sal = forming_n_in_row(4, sal)
        print(sal)
        print(cat)
        return render_template('index.html', categories=cat, prod_with_sale=sal)


@app.route("/catalog", methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    elif request.method == 'GET':
        answ = get_categories()
        answ = forming_n_in_row(3, answ)
        return render_template('catalog.html', categories=answ)


@app.route('/catalog/<id>', methods=['GET', 'POST'])
def catalog_named(id):
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    elif request.method == 'GET':
        goods = search_by_type(id.split()[-1])
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    else:
        return 1111


@app.route('/item/<name>', methods=['GET', 'POST'])
def item(name):

    need = request.args.get('id', default=0)
    if need != 0:
        id_in_bin, amount_in_bin = need.split("-")
        list_product_bin[int(id_in_bin)] = int(amount_in_bin)

    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    else:
        need = name.split()
        name, id = " ".join(need[:-1]), need[-1]
        return render_template("item.html", title=name, id=id,
                               image_item_path="/static/image/test_item.png",
                               image_sale_path="/static/image/sale_item.png")


@app.route('/bin', methods=['GET', 'POST'])
def bin():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        answ = forming_n_in_row(3, goods)
        return render_template('catalog_page.html', product=answ)
    else:
        answ = []
        print(list_product_bin)

        for i in list_product_bin:
            need = []
            goods = search_by_id(i)

            for e in goods[0]:
                need.append(e)
            print(need)
            need.append(list_product_bin[i])
            answ.append(need)

        print(answ)
        return render_template("bin.html", bin=answ)


if __name__ == '__main__':
    app.run(debug=True)