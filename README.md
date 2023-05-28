# Django Ninja REST API Gnerator
> Generate your REST API by defining `DomainModels`

## Requirements

- Python3
- venv
- docker-compose
- git

### Generate the Application

1. adapt the `DomainModels` in the `main.py` file
2. generate the aplication `python main.py`
3. move to the `/tmp/{your_app_name}` directory
4. build the application locally `./build_local.sh`
5. run the applocation locally `./run_local.sh`
6. open the browser and enjoy your REST API http://localhost:8000

## Features

The generator will provide you the following features:

- generate Django project and application
- `setting.py` is adapted
    - generate `RSA Keys` to sign the Bearer Token
    - DEBUG is set by environtment valiable `APP_ENV=PROD` or `APP_ENV=LOCAL`
    - starting of a postgres database using docker when `APP_ENV=LOCAL`
    - setting `ALLOWED_HOSTS=['*']`
    - `SECRET_KEY` can be set by environment valiable `APP_SECRET`, but have default value
    - Adding Middleware `WhiteNoise` to provide static files also in `PROD`
    - Database configuration using `jd-database-url` defined by environment variable `DATABASE_URL`
    - adding template directory
    - providing a welcome page `templates/index.html`
- CRUD endpoints
    - `GET` (one or all)
      - find all = uses pagination and filters
      - find one = pass the id as a path parameter
    - `POST` (create a new record)
    - `PUT` (update an existing record)
    - `PATCH` (partial update of an existing record)
    - `DELETE` (delete an existing record)
- OpenApi Docs
    - http://localhost:8000/api/docs
- Admin Panel
    - http://localhost:8000/admin
- Model generation
    - Django Models
    - Enums
    - Audit information `creator`, `create_date`, `modifier`, `modified_date`
- Schema generation
- Postgres database
- build and run scripts
    - `build_local.sh`
    - `run_local.sh`
    - `build_prod.sh`
    - `run_prod.sh`
- create `docker-compose.yml`
    - used for local development
- authentication
    - using `Authorization` Bearer Token signed by RSA
    - expiration can be defined by environment variable `TOKEN_EXPIRATION_MINUTES` default 1 year
- generate a `README.md`
- git
  - create a `.gitignore`
  - creates an initial commit if there was no git repo before
  - creates an update commit if there was a repo before
- test generation
  - for the REST endpoints
  - for the login
- frontend generation (Angular)
  - Navigation
  - login / logout
  - CRUD

## Usage

### Initial

    python3 -m venv .env
    source .env/bin/activate
    pip install -r requirements.txt