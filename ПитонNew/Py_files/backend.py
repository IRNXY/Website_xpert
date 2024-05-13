import sqlite3
import pymorphy3
from flask import Flask, request, render_template, redirect, make_response
import telebot
from yookassa import Configuration, Payment
import asyncio
import uuid
import json
import time
import schedule


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

    find_goods = {"name": [], "id": []}
    count = len(answ)
    if count > 0:
        for i in answ:
            find_goods["name"].append(i[0])
            find_goods["id"].append(i[1])

    return find_goods, count


def search_sale_prod(num_of_prod):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id, price, sale_price, image_path FROM xpertools WHERE on_sale = 1""").fetchall()
    answ = {"name": [], "id": [], "price": [], "sale_price": [], "image_path": []}
    count = len(need)
    if count > 0:
        for i in need[:num_of_prod]:
            answ["name"].append(i[0])
            answ["id"].append(i[1])
            answ["price"].append(i[2])
            answ["sale_price"].append(i[3])
            answ["image_path"].append(i[4])

    return answ, count


def search_by_id(id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id, price, sale_price, on_sale, image_path FROM xpertools WHERE id = ?""", (id,)).fetchall()
    answ = {"name": need[0][0], "id": need[0][1], "price": need[0][2], "sale_price": need[0][3], "on_sale": need[0][4], "image_path": need[0][5]}
    return answ


def search_by_type(type):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    need = cur.execute("""SELECT name, id, price, sale_price, on_sale, image_path FROM xpertools WHERE product_type = ?""", (type,)).fetchall()
    answ = {"name": [], "id": [], "price": [], "sale_price": [], "on_sale": [],"image_path": []}
    count = len(need)
    if count > 0:
        for i in need:
            answ["name"].append(i[0])
            answ["id"].append(i[1])
            answ["price"].append(i[2])
            answ["sale_price"].append(i[3])
            answ["on_sale"].append(i[4])
            answ["image_path"].append(i[5])

    return answ, count


def get_categories():
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    need = cur.execute("""SELECT type, id FROM xpertools_type""").fetchall()
    count = len(need)
    answ = {"type": [], "id": []}
    for i in need:
        answ["type"].append(i[0])
        answ["id"].append(i[1])
    return answ, count


def add_user(id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()
    cur.execute("""INSERT INTO users VALUES (?, ?)""", (id, time.time())).fetchall()
    data.commit()
    data.close()


def add_product_to_user(user_id, product_id, amount):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    already_in = cur.execute("""SELECT * FROM user_order WHERE user_id = ? AND product_id = ?""",
                             (user_id, product_id)).fetchall()
    if len(already_in) == 0:
        cur.execute("""INSERT INTO user_order VALUES (?, ?, ?)""", (user_id, product_id, amount)).fetchall()

    data.commit()
    data.close()


def form_bin_layout(user_id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    goods_inf = cur.execute("""SELECT x.id, x.name, x.price, x.sale_price, x.on_sale, x.image_path, u.amount_in_bin
                                     FROM user_order u, xpertools x WHERE u.user_id = ? AND x.id = u.product_id""",
                          (user_id, )).fetchall()
    answ = {"id": [], "name": [], "price": [], "sale_price": [], "on_sale": [], "image_path": [], "amount": []}
    total = 0
    count = len(goods_inf)
    if len(goods_inf) > 0:
        for i in goods_inf:
            answ["id"].append(i[0])
            answ["name"].append(i[1])
            answ["price"].append(round(i[2] - i[2] * ((i[3] * i[4]) / 100)))
            total += round(i[2] - i[2] * ((i[3] * i[4]) / 100)) * i[6]
            answ["image_path"].append(i[5])
            answ["amount"].append(i[6])
    return answ, round(total), count


def del_prod_in_order(p_id, u_id):
    data = sqlite3.connect("DataBase/tution.db")
    cur = data.cursor()

    cur.execute("""DELETE FROM user_order WHERE user_id = ? and product_id = ?""", (u_id, p_id)).fetchall()

    data.commit()
    data.close()


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


def payment(value, description):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": value,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://huter-tech.ru/"
        },
        "capture": True,
        "description": description
    }, idempotence_key)

    # get confirmation url
    confirmation_url = payment.confirmation.confirmation_url
    return (confirmation_url, json.loads(payment.json()))


async def check_payment(pay_id):
    payment = json.loads((Payment.find_one(pay_id)).json())
    while payment['status'] == 'pending':
        payment = json.loads((Payment.find_one(pay_id)).json())
        await asyncio.sleep(3)

    if payment['status'] == 'succeeded':
        print("SUCCSESS RETURN")
        print(payment)
        return True
    else:
        print("BAD RETURN")
        print(payment)
        return False


Configuration.account_id = "379692"
Configuration.secret_key = "test_0xAutDCf-h1PEHV-5KXS16ql5QT4hztsgzarRB1TL6o"

bot = telebot.TeleBot('7195957173:AAFY5J_wXVQ3t3ipeIXnfZC-iXrhmLm61-k')
app = Flask(__name__)


@app.route('/base',)
def base():
    return render_template('base.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if not request.cookies.get('authentication_id'):
        uniq_id = str(uuid.uuid4())
        res = make_response("Setting a cookie")
        res.set_cookie('authentication_id', uniq_id)
        add_user(uniq_id)
        res.headers["location"] = "/"
        return res, 302

    cat, count_cat = get_categories()

    sal, count_sal = search_sale_prod(4)
    count_sal = 4

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
            goods, count = search_by_input(product_input)
            return render_template('catalog_page.html', product=goods, count=count)
        else:
            send_client_inf(contact_name + " " + contact_phone)
            return render_template("index.html", categories=cat, prod_with_sale=sal, count_sal=count_sal, count_cat=count_cat)

    else:
        return render_template('index.html', categories=cat, prod_with_sale=sal, count_sal=count_sal, count_cat=count_cat)


@app.route("/catalog", methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        answ, count = get_categories()
        return render_template('catalog.html', categories=answ, count=count)


@app.route("/promo", methods=['GET', 'POST'])
def promo():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        return render_template('promo.html')


@app.route("/delivery", methods=['GET', 'POST'])
def delivery():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        return render_template('delivery.html')


@app.route("/ur_pers", methods=['GET', 'POST'])
def ur_pers():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        return render_template('ur_pers.html')


@app.route("/certificate", methods=['GET', 'POST'])
def certificate():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        return render_template('certificate.html')


@app.route("/contacts", methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        return render_template('contacts.html')


@app.route('/catalog/<id>', methods=['GET', 'POST'])
def catalog_named(id):
    if request.method == 'POST':
        product_input = request.form['products'].split()
        goods, count = search_by_input(product_input)
        return render_template('catalog_page.html', product=goods, count=count)
    elif request.method == 'GET':
        goods, count = search_by_type(id.split()[-1])
        return render_template('catalog_page.html', product=goods, count=count)
    else:
        return 1111


@app.route('/item/<name>', methods=['GET', 'POST'])
def item(name):

    need = request.args.get('id', default=0)
    if need != 0:
        string = need.split("-")
        id_in_bin, amount_in_bin = string[0], string[-1]
        add_product_to_user(request.cookies.get('authentication_id'), id_in_bin, amount_in_bin)

    if request.method == 'POST':

        data = request.get_json()
        if data:
            text = order_to_manager(data)
            send_client_inf(data["name"] + " " + data["phone"] + "\n" + text)
            cat, count_cat = get_categories()
            sal, count_sal = search_sale_prod(4)
            count_sal = 4
            return render_template("index.html", categories=cat, prod_with_sale=sal, count_sal=count_sal, count_cat=count_cat)
        else:
            product_input = request.form['products'].split()
            goods, count = search_by_input(product_input)
            return render_template('catalog_page.html', product=goods, count=count)
    else:
        need = name.split()
        id = need[-1]
        answ = search_by_id(id)
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

            u_id = request.cookies.get('authentication_id')
            del_prod_in_order(data["id"], u_id)

            answ, total, count = form_bin_layout(u_id)

            return render_template("bin.html", bin=answ, total=total, count=count)

        elif product_input and not(data):
            goods, count = search_by_input(product_input)
            return render_template('catalog_page.html', product=goods, count=count)
        else:
            text = order_to_manager(data)
            send_client_inf(data["name"] + " " + data["phone"] + "\n" + text)
            cat, count_cat = get_categories()
            sal, count_sal = search_sale_prod(4)
            count_sal = 4
            return render_template("index.html", categories=cat, prod_with_sale=sal, count_sal=count_sal, count_cat=count_cat)
    else:
        answ, total, count = form_bin_layout(request.cookies.get('authentication_id'))
        return render_template("bin.html", bin=answ, total=total, count=count)


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        url_pay, json_payment_inf = payment(10, "testing in website")
        # asyncio.run(check_payment(json_payment_inf["id"]))
        return redirect(url_pay)
    else:
        return render_template("test.html")


if __name__ == '__main__':
    app.run(debug=True)