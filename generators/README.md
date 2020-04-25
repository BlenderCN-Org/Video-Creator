# Генераторы данных
Предполагается, что аддон является неким API, упрощающим создание анимации в Blender. Используя API аддона, можно написать уникальные генераторы данных для него в формате _json_ под индивидуальные нужды. Примеры таких генераторов представлены в данной директории. Под каждый генератор отводится отдельная папка.

Генераторы являются полностью самостоятельными программами, которые запускаются вне Blender. Все, что они делают, - это создают json-файл заданного формата, который и открывается из аддона.
# Примеры
Примеры исходных данных и сгенерированных json-файлов можно найти [здесь](ссылка на гугл диск). Обратите внимание, что примеры данных на диске работают только для актуальной версии аддона.
# Описание генераторов
## pixels
Этот генератор получает на вход изображения **одинакового размера** (в пикселях), и создает объемную тепловую карту, где каждый пиксель - это прямоугольный параллелепипед, имеющий цвет соответствующего пикселя; его высота зависит от яркости цвета. Анимация представляет собой плавный переход между изображениями.

В pixels используется модуль _Pillow_, установить который можно командой `pip install pillow`. Чтобы прописать названия входных файлов и генерируемого json-файла, необходимо редактировать соответствующие поля в скрипте.