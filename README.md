# VerifAI
VerifAI, is a full-stack web application built with a Django backend and a React frontend that uses the OpenAI API to create, process, and analyze survey responses (such as those regarding tobacco usage habits in the example given in the surveys folder).


## 1. Mandatory installations
These should be all additional installations needed to run this project.

```bash
    pip install django
    pip install djangorestframework
    python -m pip install django-cors-headers
    pip install openai
    pip install python-dotenv
    pip install openpyxl
```

Or install all at once:

```bash
    pip install -r requirements.txt
```

## 2. Set up the environment
In order to have functional OpenAI calls, you should set up the environment file appropriately. Adjust your own OPENAI_API_KEY in case the existing key no longer works.
## 3. Make migrations
Once you are positioned in the verifai/ directory, you need to set up the mandatory Django migrations. Run these commands in your terminal:

```bash
  python manage.py makemigrations
  python manage.py migrate
```

Bonus tip: If you encounter any additional errors related to db.sqlite3, run this command:

```bash
  python manage.py migrate  --run-syncdb
```


## 4. Run backend
In order to run the code, open your terminal, position your seft to project root and run the following command:

```bash
    python manage.py runserver
```


## 5. Run frontend
Open your terminal, position your seft to "/frontend" folder and run the following command in order to install node modules:

```bash
    npm install
```

Then run the following command in order to start the application:

```bash
    npm start
```
