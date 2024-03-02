from bs4 import BeautifulSoup
import requests

# вставляем ссылку на страницу, из которой хотим скачать картинки
url = 'https://lm-nsk.ru/catalog/payalnye_i_svarochnye_instrumenty/'
page = requests.get(url)
content = page.content

# пользуемся библиотекой для того чтобы скачать html расскладку выбранной страницы
soup = BeautifulSoup(content, 'html.parser')
# ищем все упоминания img в html
images = soup.find_all("img")

# проходимся цмклоп по каждому такому найденному img. Цикл начинаем не с 0, так как обычно первыми идут не валидные для нас картинки
for i in range(3, len(images)):
    one = str(images[i])
    try:
        # определяем границы пути файла для скачивания (пример: data-src="/path/file_name.jpg")
        left = one.index('data-src=')
        right = one.index("jpg")
        # достаём нужную часть (path/file_name.jpg). Числа несут корректировочный характер
        way_to_file = one[left+11:right+3]
        print(way_to_file)
    except Exception:
        pass
    # Указываем ссылку на основную страницу
    must_have = "https://lm-nsk.ru/"
    # Картинка скачивается по схеме: ссылка на основную страницу + ссылка на картинку
    image_url = must_have + way_to_file
    img_data = requests.get(image_url).content
    # скачиваем в ту же папку где и наш parsing.py
    with open('image_name{0}.jpg'.format(str(i)), 'wb') as pic:
        pic.write(img_data)


# one = []
# need = soup.find_all("h2")
#
# for i in need:
#     try:
#         i = str(i)
#         left = i.index.css("href")
#         right = i.index.css('itemprop="url"')
#         one.append(i[left+6:right-2])
#     except Exception:
#         pass

# for product in one:
#     print(product)
#     url = 'https://resanta.ru' + product
#     page = requests.get(url)
#
#     content = page.content
#     soup = BeautifulSoup(content, 'html.parser')
#
#     a = str(soup.find(itemprop="description"))
#     left = a.index.css("<p>")
#     right = a.index.css("</article>")
#     print(a[left+3:right])
#
#     print()
