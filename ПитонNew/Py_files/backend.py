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

# путь к базе данных
# file_path = "C://Program Files//SQLiteStudio//All_bases//first.db"
# устанавливаем соединение

# cur = data.cursor()
# выполняем запрос к базе данных
# product_name = cur.execute('SELECT name, path_image FROM zubr')
# answ = forming_n_in_row(2, product_name)
# print(answ)
# используем функцию для формирования католога с определённым количество колонок
# data.commit()
# data.close()

app = Flask(__name__)

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_input = request.form['products'].split()

        data = sqlite3.connect("DataBase/tution.db")
        cur = data.cursor()

        product_brands = ["зубр", "zubr", "ресанта", "рисанта", "resanta", "хутер", "хутэр", "huter", "штиль", "stihl",
                          "евролюкс", "eurolux"]
        # подключаем морф чтобы определять часть речи
        morph = pymorphy3.MorphAnalyzer()

        # ключи для поика
        arg_sku = ''
        arg_product_type = ''
        arg_product_subtype = ''
        arg_brand = ''
        arg_name = ''

        # проходим по каждому слову из строки
        for i in range(len(product_input)):
            word = product_input[i]
            # определяем является ли слово брендом
            if word.lower() in product_brands:
                arg_brand = word.lower()
            # существительное в большенстве случаев является видом товара
            elif "NOUN" in morph.parse(word.lower())[0].tag and arg_product_type == '':
                arg_product_type = morph.parse(word)[0].normal_form
            # прилагательное в большинстве случаев является подвидом товара
            elif "ADJF" in morph.parse(word.lower())[0].tag:
                arg_product_subtype = morph.parse(word)[0].normal_form
            # разделяем все слова на содержащие спецсимволы и цифры и на обычные слова
            elif word.isalpha():
                # если нет, добавляем слово в раздел проверки по имени товара
                arg_name = arg_name + word
            else:
                # проверяем наличие спецсивловол
                if "." not in word and "-" not in word:
                    special_char = "\/"
                    # на случай если пользователь написал артикул с пробелами
                    if len(word) < 2:
                        arg_sku = product_input[i - 1] + product_input[i] + product_input[i + 1]
                    # если есть \/ то это 100% артикул
                    elif special_char[0] in word or special_char[1] in word:
                        arg_sku = word
                    else:
                        # иначе это модель товара
                        arg_name = arg_name + " " + word
                else:
                    # это тоже модель или артику
                    arg_name = arg_name + " " + word

        # если не нашло артикула вида 00/00/00 записываем модель как артикул
        if arg_sku == None:
            arg_sku = arg_name

        # приводим бренд в нужный формат
        convertation = {"рисанта": "ресанта", "resanta": "ресанта", "zubr": "зубр", "хутер": "huter",
                        "хутэр": "huter", "штиль": "stihl", "евролюкс": "eurolux"}

        if arg_brand in convertation:
            arg_brand = convertation[arg_brand]

        # print(arg_sku, "|", arg_brand, "|", arg_product_type[:-1], "|", arg_product_subtype, "|", arg_name)
        product_name = cur.execute("""SELECT name, path_image
                            FROM zubr 
                            WHERE product_type LIKE '%{2}%' AND brand LIKE '%{1}%' 
                            AND sku LIKE '%{0}%' AND name LIKE '%{3}%' AND name LIKE '%{4}%' """.format(arg_sku,
                                                                                                        arg_brand,
                                                                                                        arg_product_type[:-1],
                                                                                                        arg_product_subtype[:-2],
                                                                                                        arg_name)).fetchall()
        answ = forming_n_in_row(2, product_name)
        # print(answ)

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