## Запуск и останов процессов через MQTT

- ### Настройка polkit
Файл [49-nopasswd_global.rules](49-nopasswd_global.rules) надо скопировать в каталог `/etc/polkit-1/rules.d` . В файле написано правило для запуска административных команд без пароля для группы wheel.

- ### Настройка python
В CentOS 8 Python 3.10 можно установить из репозитария Raven, чтобы не собирать Python из исходников. 

1. Добавление репозитария Raven `sudo dnf install -y https://pkgs.dyn.su/el8/base/x86_64/raven-release.el8.noarch.rpm`
2. Установка Python 3.10 `sudo dnf -y install python310`

Файл [requirements.txt](requirements.txt) получен командой `python -m pip freeze > requirements.txt` и поправлен вручную.

Для установки зависимостей

    1. Перейдём в каталог где лежит программа [pscmd.py](pscmd.py) , в дальнейшем будем считать что это каталог `$HOME/.local/pscmd` .
    2. Создадим виртуальное окружение командой `python3.10 -m venv .venv` (вместо python3.10 можно указать более свежую версию Python, если имеется).
    3. Активируем его командой `source .venv/bin/activate`
    4. Проверим версию Python
    ```
    (.venv) [super@cabin2 cabincmd]$ python --version
    Python 3.10.8
    ```
    5. установим зависимости программы командой `python -m pip install -r requirements.txt`

- ### Запуск сервиса `pscmd.py`

    1. Разрешаем запуск пользовательских сервисов без логина в систему командой `loginctl enable-linger super`
    2. Создадим каталог, где будет находиться сервис pscmd `mkdir -p ~/.config/systemd/user`
    3. Копируем туда файл сервиса [pscmd.service](pscmd.service) `cp pscmd.service ~/.config/systemd/user`
    4. Запускаем сервис:
    ```bash
    systemctl --user enable pscmd.service
    systemctl --user start pscmd.service
    systemctl --user status pscmd.service
    ```

