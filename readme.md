
https://github.com/user-attachments/assets/47085866-34ac-411c-af3e-91aee774eee5

## Installation
1. Clone this repository and set up the environment:
~~~
git clone https://github.com/smaiht//bazis-online-converter.git
~~~

2. Install required packages
~~~
cd bazis-online-converter/
pip install pywin32
pip install requests
pip install python-dotenv
~~~
or
~~~
cd bazis-online-converter/
pip install -r req.txt
~~~

3. Внутри main.py нужно указать путь до исполняемого файла Bazis (работает только с лицензионной версией)
~~~
BAZIS_PATH = "C:\\BazisOnline\\Bazis.exe"
~~~

4. Run
~~~
python main.py
~~~

------------

Короче вот такой питон скрипт получился. Крутится и каждые 10 секунд мониторит папку INPUTS.

Как только в папку INPUTS попадает хоть одна другая папка - то он сразу перемещает ее в PROCESSINGS и смотрит чтобы внутри обязательно был model.b3d (файл базиса) и user.json (о нем дальше напишу) и затем запускает базис со скриптом.

Базис открывается, авторизуется и выполняет JS скрипт конвертации и сохраняет сконвертированный файлик в корень output.s123proj
Пока базис конвертирует - в это время питон скрипт продолжает мониторить  либо ошибки в окне базиса, либо появление файлика output.s123proj 

Если были ошибки - то убивает базис и логирует, переносит файлы в папку ERRORS и продолжает мониторить папку INPUTS

Если увидел что появился файлик output.s123proj, то убивает базис, отправляет дотнету пост запрос с файлом и user.json, чтобы дотнет загрузил проект в систему и создал чат. В user.json соответсвенно нужна необходимая инфа чтобы загрузить проект от имени юзера в его компанию, и создать чат, и отправить уведомление.
