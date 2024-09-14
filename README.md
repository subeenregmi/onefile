
# Onefile

A simple and selfhosted way of sharing files.

## Features

- Downloading and viewing analytics
- Selfhosted solution
- Secure and safe


## Run Locally

Clone the project

```bash
  git clone https://github.com/subeenregmi/onefile.git
```

Go to the project directory

```bash
  cd onefile
```

Install dependencies

```bash
  cd static
  npm Install
  cd ..
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
```

Start the server

```bash
  python3 backend/server.py
```


## Running Tests

To run tests, run the following command

```bash
    cd tests
    pytest
```


## License

[MIT](https://choosealicense.com/licenses/mit/)

