# Week 9 Testing

For this week's activities it is suggested that you try the tests for both apps as different techniques are covered in each app.

## Setup

You may need to refer to COMP0035 or [COMP0034 week 4 activities](https://github.com/nicholsons/comp0034-week4/blob/main/activities/activities.md) to complete the following:

1. Configure your IDE to support pytest.
2. Create a `tests` directory. Note: `tests` already created if you clone the week 9 repo)
3. Add a `conftest.py` file to add fixtures to.
4. Install the paralympics and iris app using `pip install -e .`
5. Set-up a GitHub Actions workflow for continuous integration

> **IMPORTANT**: Windows users, please `pip uninstall pytest-flask` as the `live_server` fixture will not work on Windows.

Check you can run the apps:

`python -m flask --app 'paralympic_app:create_app("paralympic_app.config.DevConfig")' --debug run`

`python -m flask --app 'iris_app:create_app()' --debug run`

## Test directory structure

There is no single structure. Best practice, and to support test discovery, create a tests folder.

There are different patterns for creating the tests within the test folder. For example:

[Patrick's blog tests directory](https://testdriven.io/blog/flask-pytest/#project%20structure)

```text
├── app.py
├── project
│   ├── __init__.py
│   ├── models.py
│   └── ...
├── requirements.txt
├── tests
│   ├── conftest.py
│   ├── functional
│   │   ├── __init__.py
│   │   ├── test_stocks.py
│   │   └── test_users.py
│   └── unit
│       ├── __init__.py
│       └── test_models.py
└── venv
```

[Flask documentation tutorial](https://flask.palletsprojects.com/en/2.2.x/tutorial/layout/)

```text
/home/user/Projects/flask-tutorial
├── flaskr/
│   ├── __init__.py
│   ├── auth.py
│   ├── blog.py
│   ├── templates/
│   │   ├── ...
│   └── static/
│       └── style.css
├── tests/
│   ├── conftest.py
│   ├── data.sql
│   ├── test_factory.py
│   ├── test_db.py
│   ├── test_auth.py
│   └── test_blog.py
├── venv/
├── setup.py
```

[Pytest documentation: tests outside application code](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#tests-outside-application-code)

```text
src/
    mypkg/
        __init__.py
        app.py
        view.py
tests/
    test_app.py
    test_view.py
    ...
```

## Running the tests

Assume that you have a tests directory with two subdirectoris called `tests_paralympics_app` and `tests_iris_app`. Code to run the tests is given below.

The extra flag ignores package deprecation warnings. This is done to reduce the amount of text reported from the tests which hopefully makes it a little easier for you to see the errors that are specific to the test code:

`python -m pytest -v tests/tests_paralympic_app/ -W ignore::DeprecationWarning`

`python -m pytest -v tests/tests_iris_app/ -W ignore::DeprecationWarning`

## Tests for Flask apps

You will see different names for tests, but generally the types we are concerned with here are:

- **unit tests** - a small component tested in isolation, e.g. a function
- **integration tests** - more than one unit tested together
- **end-to-end tests** - testing that the web app as a whole works, for example clicking buttons on a site to complete a typical user task e.g. the login process

You should already be able to write Pytest tests. These can be used to write unit tests for the database model classes or other utility functions (i.e NOT routes) in your application.

This was covered in COMP0035 and is not covered again here, though there are a few examples in [week 9 complete tests](https://github.com/nicholsons/comp0034-week9-complete/tree/master/tests/tests_paralympic_app) directories for model classes if you wish to have a look.

## Activity files

This week's activities are in multiple files due to the length of the text.

You should work through them in order; later activities assume you have completed the earlier ones so some of the code will not work if you have not completed the prior steps.

- [/activities/1-activity-intrio.md](/activities/1-activity-intro.md)
- [/activities/2-testing-routes.md](/activities/2-testing-routes.md)
- [/activities/3-browser-testing.md](/activities/3-browser-testing.md)
