# stepik-py-live

## Initialize project

### for win cmd
```
> python -m venv env
> env\Scripts\activate
(env) > pip install -r requirements.txt
```

### for nix sh (bash)
```
$ python3 -m venv env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```

## Activate virtual environment
If the virtual environment is activated, the command line must contain `(env)`

### for win cmd
```
> env\Scripts\activate
(env) >
```

### for nix sh (bash)
```
$ source env/bin/activate
(env) $
```

## Run application
```
(env) > flask run
```

## Run application in debug mode

### for win cmd
```
(env) > set FLASK_DEBUG=1
(env) > flask run
```

### for nix sh (bash)
```
(env) $ FLASK_DEBUG=1 flask run
```
