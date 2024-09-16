
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
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  cd static
  npm install && npx webpack
```

Start the server

```bash
  python3 backend/server.py
```

The app will be hosted at [localhost:5000](http://localhost:5000)

## Deployment

To deploy this project with docker


Build the docker image
```bash
  docker build -t onefile . 
```
Run the container with `docker run`

```bash
docker run \
    --name onefile
    -p <any_port>:5000
    --restart unless-stopped
    onefile
```
Run the container with provided `docker-compose.yaml`
```bash
docker compose up -d
```
*Note*: `docker-compose.yaml` uses the port 6868, this can be changed to anything.
## Running Tests

To run tests, run the following command

```bash
    cd tests
    pytest
```


## License

[MIT](https://choosealicense.com/licenses/mit/)

