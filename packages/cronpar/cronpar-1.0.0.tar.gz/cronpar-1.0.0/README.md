# Cronpar - a tool for parsing cron expression

### Requirements

To run this program, you need setup you local environment as following

- A Python Environment with Python 3.8+ and pip (reckon use pyenv and create a virtualenv)
- Poetry (Dependency management)
- make (a dev tool)

### Setup

Before you can run everything, please make sure you have setup a Python environment

if you are using make, you can setup the dev environmane by simply using

```shell
make init
```

this will install poetry and install all dependencies. If you don't want to use make, alternatively, just run the 
following commands

```shell
pip install poetry
poetry install
```

To prepare/build the cli tool for you to play with, run

```shell
make build
```

or, just run

```shell
pipx install .
```

Now, you should be able to run the program, for example

```shell
cronpar explain "*/15 0 1,15 * 1-5 /usr/bin/find"
```

### Yesting & Contribution

There are some test cases generated during development, to run the tests, you can either run

```shell
make test
```

pr 

```shell
poetry run pytest tests/ --cov --cov-fail-under 89
```

Please make sure you have tested all the changes you made properly, and all tests passed before you push

Also, it will be good to keep the code formatted, you can check this by running

```shell
make format
make lint
```

or 

```shell
poetry run black --preview --line-length 120 cronpar
poetry run isort --line-length 120 cronpar
poetry run flakehell lint .
```

### Notice

Please Note this program is still in development, it may be not very stable,
but we will fix and add more features in the coming future.
