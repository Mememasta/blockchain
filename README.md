
blockchain

Здесь описано все, чтобы с легкостью настроить базу данных, виртуальное окружения и запустить проект.


## Установка проекта

```
git clone https://github.com/Mememasta/blockchain
```

Все библиотеки уже лежат в файле env, поэтому достаточно активировать виртуальное окружение командой:

```
sudo apt-get install python3-virtualenv
```

Если виртуальное окружение не работает, установим библиотеки вручную

```
pip3 install -r requirements.txt
```

## Установка PostgreSQL12

Установка postgresql достаточно сложная, ниже будет инструкция по полной настройке бд

```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - ; \
RELEASE=$(lsb_release -cs) ; \
echo "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list ; \
sudo apt update ; \
sudo apt -y install postgresql-12 ; \
sudo localedef ru_RU.UTF-8 -i ru_RU -fUTF-8 ; \
export LANGUAGE=ru_RU.UTF-8 ; \
export LANG=ru_RU.UTF-8 ; \
export LC_ALL=ru_RU.UTF-8 ; \
sudo locale-gen ru_RU.UTF-8 ; \
sudo dpkg-reconfigure locales
```

Добавьте локали в /etc/profile:

```
sudo vim /etc/profile #vim-редактор кода, можно использовать любой другой по типу nano
#после открытия редактора вписать след. строки
    export LANGUAGE=ru_RU.UTF-8
    export LANG=ru_RU.UTF-8
    export LC_ALL=ru_RU.UTF-8
```

Сменим пароль postgres, создадим пустую бд:

```
sudo passwd postgres
su - postgres
export PATH=$PATH:/usr/lib/postgresql/12/bin

createdb --encoding UNICODE (любое название бд, без скобок) --username postgres
exit
```
Теперь мы можем запустить файл "init_db.py" для создания всех таблиц, полей и пользователей

```
python3 init_db.py -a
```

Пояснение всех ключей

```
python3 init_db.py --help
usage: init_db.py [-h] [-c] [-d] [-r] [-a]

optional arguments:
  -h, --help      Показать значение ключей и выйти
  -c, --create    Создать пустую бд и пользователя с разрешениями
  -d, --drop      Удалить бд и пользователя
  -r, --recreate  Удалить, после чего переустановить бд и пользователя
  -a, --all       Создать бд с готовыми данными
```

В случае ошибки при запуске, возможным решением будет изменение конфигурации postgresql, а именно:

1) Заходим под пользователя postgres
```
sudo -u postgres psql
```
2) Смотрим путь до нужного нам файла
```
show hba_file ;

hba_file
--------------------------------------
/etc/postgresql/12/main/pg_hba.conf
```
3)Выходим из пользователя postgres, переходим по данному пути и меняем значения
!!! ВАЖНО: менять нужно последний столбец, все остальное может отличаться
```
local   all             postgres                                peer

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
```

4) Перезапустим postgresql

```
service postgresql restart
```

## Запуск приложения

1) Для запуска сервера используем команду:

```
python3 app.py --reload -c config/user_config.toml
```
### --reload перезапускает сервер, при сохранении изменений кода
### -с путь к конфиг файлу для подключения к бд, необязательный, по умолчанию путь config/user_config.toml
