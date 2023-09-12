PomodoroTk
==========

Timer for pomodoro technique with GUI written in tkinter.


Install with pipx or pip
-------------------------

```
pipx install pomodorotk
```

or with pip:

```
pip install pomodorotk
```

### Run

```
pomodoro
```

Build single file executable
----------------------------

Install [PyEmpaq](https://pyempaq.readthedocs.io/)

```
# move to the directory containing this repo
cd ..

# build
pyempaq pomodoro
```

Run with:

```
python pomodorotk.pyz
```


Develop
-------

Clone this repo and install dependencies with Poetry:

```
poetry install
```

## Run in development mode

```
poetry run pomodoro
```