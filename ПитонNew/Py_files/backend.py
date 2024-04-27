import sqlite3
import pymorphy3
from flask import Flask, request, render_template
import telebot


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
    need = cur.execute("""SELECT name, id, price, sale_price FROM xpertools WHERE on_sale = 1""").fetchall()
    return need[:num_of_prod]


def search_by_id(id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id, price, sale_price, on_sale FROM xpertools WHERE id = ?""", (id,)).fetchall()
    return need


def search_by_type(type):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id, price, sale_price, on_sale FROM xpertools WHERE product_type = ?""", (type,)).fetchall()
    return need


def get_categories():
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    need = cur.execute("""SELECT type, id FROM xpertools_type""").fetchall()
    return need


def form_bin_layout():
    answ = []
    total = 0
    for i in list_product_bin:
        need = []
        goods = list(search_by_id(i)[0])

        if goods[-1] == 0:
            del goods[-1]
            del goods[-1]
        else:
            del goods[-1]
            del goods[-2]
        current_price = goods[-1]

        for e in goods:
            need.append(e)

        need.append(list_product_bin[i])
        total += current_price * list_product_bin[i]
        answ.append(need)
    return [answ, total]


def order_to_manager(goods_list):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    text_to_manager = 'Клиент заказал:'

    for i in enumerate(goods_list.keys()):
        if "display" in i[1]:
            id = i[1].split("display")[-1]
            need = cur.execute("""SELECT name FROM xpertools WHERE id = ?""", (id,)).fetchall()
            text_to_manager += "\n" + str(i[0] + 1) + ") " + need[0][0] + ", артикул = " + str(id) +\
                               ", в количестве " + str(goods_list[i[1]])

    return text_to_manager


def send_client_inf(out_str):
    bot.send_message(1998273938, out_str)


list_product_bin = dict()

bot = telebot.TeleBot('7195957173:AAFY5J_wXVQ3t3ipeIXnfZC-iXrhmLm61-k')
app = Flask(__name__)

@app.route('/base',)
def base():
    return render_template('base.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    cat = get_categories()

    sal = search_sale_prod(4)

    product_input, contact_name, contact_phone = '', '', ''

    if request.method == 'POST':

        try:
            product_input = request.form['products'].split()
        except Exception:
            pass

        try:
            contact_name = request.form['name']
            contact_phone = request.form['phone']
        except Exception:
            pass

        if len(product_input) > 0:
            goods = search_by_input(product_input)
            return render_template('catalog_page.html', product=goods)
        else:
            send_client_inf(contact_name + " " + contact_phone)
            return render_template("index.html", categories=cat, prod_with_sale=sal)

    else:
        return render_template('index.html', categories=cat, prod_with_sale=sal)


@app.route("/catalog", methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        answ = get_categories()
        return render_template('catalog.html', categories=answ)


@app.route("/promo", methods=['GET', 'POST'])
def promo():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        return render_template('promo.html')


@app.route("/delivery", methods=['GET', 'POST'])
def delivery():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        return render_template('delivery.html')


@app.route("/ur_pers", methods=['GET', 'POST'])
def ur_pers():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        return render_template('ur_pers.html')


@app.route("/certificate", methods=['GET', 'POST'])
def certificate():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        return render_template('certificate.html')


@app.route("/contacts", methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        return render_template('contacts.html')


@app.route('/catalog/<id>', methods=['GET', 'POST'])
def catalog_named(id):
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods)
    elif request.method == 'GET':
        goods = search_by_type(id.split()[-1])
        return render_template('catalog_page.html', product=goods)
    else:
        return 1111


@app.route('/item/<name>', methods=['GET', 'POST'])
def item(name):

    need = request.args.get('id', default=0)
    if need != 0:
        string = need.split("-")
        id_in_bin, amount_in_bin = string[0], string[-1]
        list_product_bin[int(id_in_bin)] = int(amount_in_bin)

    if request.method == 'POST':

        data = request.get_json()
        if data:
            text = order_to_manager(data)
            send_client_inf(data["name"] + " " + data["phone"] + "\n" + text)
            cat = get_categories()
            sal = search_sale_prod(4)
            return render_template("index.html", categories=cat, prod_with_sale=sal)
        else:
            product_input = request.form['products'].split()
            print(product_input)
            goods = search_by_input(product_input)
            return render_template('catalog_page.html', product=goods)
    else:
        need = name.split()
        id = need[-1]
        answ = search_by_id(id)[0]
        return render_template("item.html", name=name, product=answ,
                               image_item_path="/static/image/test_item.png",
                               image_sale_path="/static/image/sale_item.png")


@app.route('/bin', methods=['GET', 'POST'])
def bin():
    if request.method == 'POST':

        try:
            data = request.get_json()
        except Exception:
            data = dict()

        try:
            product_input = request.form['products'].split()
        except Exception:
            product_input = ''

        if "id" in data.keys():
            try:
                del list_product_bin[data["id"]]
            except Exception:
                pass

            answ, total = form_bin_layout()

            return render_template("bin.html", bin=answ, total=total)

        elif product_input and not(data):
            goods = search_by_input(product_input)
            return render_template('catalog_page.html', product=goods)
        else:
            text = order_to_manager(data)
            send_client_inf(data["name"] + " " + data["phone"] + "\n" + text)
            cat = get_categories()
            sal = search_sale_prod(4)
            return render_template("index.html", categories=cat, prod_with_sale=sal)
    else:
        answ, total = form_bin_layout()
        return render_template("bin.html", bin=answ, total=total)


if __name__ == '__main__':
    app.run(debug=True)