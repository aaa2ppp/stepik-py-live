# stepik-py-quest

Это реализация мини-проекта 3.3 курса *"Web-фреймворк Flask: введение"* на *stepik.org*.

## Путеводитель для рецензентов

Все команды выполняются в оболочке <code>cmd</code> *os windows*. Протестировано на *win10*.
У пользователей *nix*, я надеюсь, не возникнет особых сложностей адаптировать
эту инструкцию под свою систему 😈

### Проверьте, что у вас установлены необходимы программы

```
> python -V
Python 3.10.1
> pip -V
pip 21.2.4
> git --version
git version 2.33.1.windows.1
```

* пользователи *nix* должны использовать команду <code>python3</code>

### Получите проект

```
> cd "%TEMP%"
> git clone https://github.com/aaa2ppp/stepik-py-quest.git
Cloning into 'stepik-py-quest'...
...
... done.
```

### Инициализируйте проект

```
> cd stepik-py-quest
> python -m venv env
> env\Scripts\activate.bat
(env) > pip install -r requirements.txt
```

* пользователи *nix*, для активации виртуального окружения, должны использовать команду:

```
$ source env/bin/activate
```

### Запустите приложение

Для удобного просмотра исходного кода страниц, запустите приложение в режиме отладки <code>FLASK_DEBUG=1</code>

Для отключения кеширования на стороне браузера вы можете установить переменную окружения <code>NO_CACHE=1</code>

```
(env) > set FLASK_DEBUG=1
(env) > set NO_CACHE=1
(env) > flask run
 ...
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 ...
```

### Откройте приложение в браузере

http://127.0.0.1:5000

---

### Протестируйте приложение и оставите свою рецензию на *stepik.org* :)

---

### Остановите приложение и удалите проект

Что бы остановите приложение, нажмите <code>Ctrl+C</code>, в окне терминала в котором оно запущено
(мда... у меня срабатывало через раз).

```
^C
(env) > env\Scripts\deactivate.bat
> cd ..
> rmdir /s /q stepik-py-quest
```

## Спасибо за проделанную работу!
