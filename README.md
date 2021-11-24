# SurveyKong

## Included/installed Features:
- Debugging toolbar
- Django extensions
- "Switch user" admin feature
- Custom 403, 404, 500 error pages
- Custom error handling, including email and slack room hook notification features
- Site-wide banner notifications
- Basic flexible page template
- UI framework using Tachyons, select2, tooltip and overlays
- Template helpers for preset design components; buttons, icons, header, tabs, etc
- COS (Cloud Object Storage) storing and CDN serving of static files


## Install Requirements

Python 3.8 ish +

Postgres 11 ish +


## Install

Python 3 comes with built-in `venv` so no extra virtual environment package is required.
Setup a virtual environment:

&nbsp; &nbsp; `python3 -m venv /path/to/env/<name>`


Activate that environment:

&nbsp; &nbsp; `source /path/to/env/<name>/bin/activate`


Clone the repo:

&nbsp; &nbsp; `git clone git@github.com:ibm/surveykong.git`


CD to the repo root wherever you just cloned it to and install the dependencies:

&nbsp; &nbsp; `pip install -r requirements.txt`

Setup some localhost variables:
There are some local variables and settings needed for your implementation. They can either be set as environment variables, or you can add a `local_settings.py` file alongside the Django default `settings.py` file. 
If you set them as environment variables you will only have to do this once and each of our Django app will use those same settings.

You only need to replace the two `___`s with your local Postgres DB user ID and PW. 
`SCRIPT_NAME` is intentionally blank.


```
    export DJANGO_DB_USER=____
    export DJANGO_DB_PASSWORD=____
    export DJANGO_DEBUG_FLAG=True
    export DJANGO_FORCE_SCRIPT_NAME=
```
    
Create a postgresql database called `surveykong`
(Ensure your user account can write to the database)


Have Django setup the database according to the models. From the repo root:

&nbsp; &nbsp; `./manage.py migrate`

Create a superuser (follow the prompts, you can leave email blank):

&nbsp; &nbsp; `./manage.py createsuperuser`


## Running and developing

Every time you want to start the app, there are 3 steps:
1. Ensure you are in your environment you created above.
2. CD to the local repo root.
3. Start up Django.
 
 
Steps in detail: 

1. Ensure you have the environment activated:

&nbsp; &nbsp; `source /path/to/env/<name>/bin/activate`

2. CD to the repo root:

&nbsp; &nbsp; `cd /some/path/to/repo`

3. Start the Django app:

&nbsp; &nbsp; `./manage.py runserver`

Now you can open your browser to http://localhost:8000/  and you should see it.

Make your changes and simply reload your browser page to see them.


### Pro tip
Create a script alias to do all this for you. Add this line in your `.bash_profile` file:

`alias startsurveykong='source /path/to/this-app-env/bin/activate && cd /some/path/to/repo/ && ./manage.py runserver'`


## Documentation
We use `pydoctor` (https://pydoctor.readthedocs.io/en/latest/) for easy to read auto-generated documentation.
You can generate easily for any installed app.
1. Install pydoctor:  `pip install pydoctor`
2. Run pydoctor to generate HTML files for whichever app you want. Example:  `pydoctor --make-html --html-output=docs/survey survey`
3. Open the `docs/survey/index.html` file in your browser and read away.


## Coding style guidelines
 
We follow the basic Django and Python coding principles and styles:  
https://docs.djangoproject.com/en/2.2/misc/design-philosophies/  
https://docs.djangoproject.com/en/2.2/internals/contributing/writing-code/coding-style/  

  &nbsp;
  
