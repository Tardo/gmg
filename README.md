# Give Me the Garbage

_Web application to analyze the content of public forums_

### INSTALLATION

#### Automatic Mode (recommended)

```shell
copier copy gh:Tardo/gmg-template gmg
cd gmg
docker-compose up
```

See 'gmg-template' repo for more info: https://github.com/tardo/gmg-template

#### Manual Mode

```shell
python -m pip install --upgrade pip
pip install poetry
curl -L https://raw.githubusercontent.com/tj/n/master/bin/n -o n
bash n latest
npm install --global npm
npm install --global postcss postcss-cli rollup
git clone git@gitlab.com:Tardo/gmg.git
cd gmg
poetry install
poetry run npm install
poetry run npm run srv:dev
```

Now can visit: http://localhost:8000

\*\* Check the `gmg.conf` file to enable various debug options. You will need
restart the service every time you edit this file.

### Translations

#### Add a new language

\*\*\* _You will need install 'pybabel'_

\*\* Do this using the project directory!

- Generate .pot file

```shell
pybabel extract -F babel.cfg -o messages.pot .
```

- Generate folder structure and .po file (Omit if you already do it)

```shell
pybabel init -i messages.pot -d translations -l <language code: ISO 639-1>
```

#### Update translations with new strings

```shell
poetry run npm run upd:translations
```

- Edit .po file(s) using for example '[poedit](http://poedit.net/download)'

- Update again to compile .mo with the lastest changes:
  ```shell
  poetry run npm run upd:translations
  ```

### Migrate Database Changes

1. Create commit

```shell
poetry run flask db migrate -m "COMMIT MESSAGE"
```

3. Review migrations/versions/...py script

4. Apply the changes

```shell
poetry run flask db upgrade
```

### Possible Problems

- Get the exception `UnkownTimeZoneError`: To fix this configure the time zone
  of your system: `dpkg-reconfigure tzdata`

### Limits

- The default maximum size of upload is 16MB per mod (can change it in gmg.conf)
