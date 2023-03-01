# 2. Unit / integration tests for Flask routes

## Contents

- [Introduction](#introduction)
- [Create fixtures to generate a Flask app and test client for testing](#create-a-fixture-to-generate-a-flask-app-for-testing-and-a-test-client)
- [Write tests for routes](#writing-the-tests-for-routes)
- [Tests for the paralympic app routes](#paralympic-app-routes)
- [Tests for the iris app routes](#iris-app-routes)

## Introduction

Some Flask routes may involve only a single function; others may involve multiple 'units'. The difference isn't meaningful in how you will code the tests so can be ignored.

You need to have basic awareness of Flask [application and request contexts](https://flask.palletsprojects.com/en/2.2.x/appcontext/#the-application-context). The importance of these is explained more clearly by [Patrick Kennedy in his blog](https://testdriven.io/blog/flask-contexts/).

One of the key points from Patrick's blog:

When an HTTP request is received, Flask provides two contexts:

| Context | Description | Available Objects |
|:--- |:-------- |:------ |
| Application | Keeps track of the application-level data (configuration variables, logger, database connection)|current_app, g |
| Request | Keeps track of the request-level data (URL, HTTP method, headers, request data, session info) | request, session |

These contexts are created when a view is generated as result of an HTTP request. THis is why, if you try to access the `current_app` or `request` outside of a view you get an error message such as `RuntimeError: Working outside of application context.`.

To get around this you can create a context. You've seen an example of this perhaps without realising when you created the app in the create_app() function and registered a blueprint or created database tables e.g.:

```python
with app.app_context():
    db.create_all()

```

The Flask documentation explains when you may [need an active context in your tests](https://flask.palletsprojects.com/en/2.2.x/testing/#tests-that-depend-on-an-active-context).

Sounds a little complex, however you most of this is handled for you when you use the [Flask test client](https://flask.palletsprojects.com/en/2.2.x/testing/#sending-requests-with-the-test-client). The test client makes requests to the application without running a live server and has knowledge of request contexts.

## Create a fixture to generate a Flask app for testing and a test client

The Flask documentation recommends that you [create fixtures](https://flask.palletsprojects.com/en/2.2.x/testing/#fixtures) to run the app and create a test client.

Their code has been slightly modified in the version below to include [Patrick Kennedy's version of the test client](https://gitlab.com/patkennedy79/flask_user_management_example/-/blob/main/tests/conftest.py). He yields the test_client with an application context so you don't have to explicitly use create the context in tests.

I have kept the fixtures as two rather than merging into the one used by Patrick. This is in case students later wish to use pytest-flask live_server for the Selenium tests as this requires that their be a fixture named `app` that create the Flask app. **Note**: do not use pytest-flask live_server if you use Windows.

A number of config parameters are also set:

- `"SQLALCHEMY_ECHO": True` prints all SQL statement to the terminal. The SQL is generated from the Flask-SQLAlchemy query syntax. This can be useful if you need to debug queries.
- `"WTF_CSRF_ENABLED": False` prevents forms with CSRF protection from causing the tests to fail. You need to set this if you have CSRF protection enabled.

To facilitate running the app for those using Windows, the create_app() function in the apps has been modified to accept configuration from a configuration class in a file called `config.py` in each app package/folder.

The following is an example for the paralympics_app, for the iris_app change the package reference in the import.

```python
import pytest
from paralympic_app import create_app, config

@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing"""
    app = create_app(config.TestConfig)
    yield app


@pytest.fixture(scope="function")
def test_client(app):
    """ Flask test client within an application context. """
    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client
```

Add the fixtures shown above to a `conftest.py` file for the app you wish to test (`tests/tests_paralympics_app/conftest.py` or `tests/tests_iris_app/conftest.py`).

Note: Patrick Kennedy's code also has fixtures for creating a database and logging in a user which may be useful.

## Writing the tests for routes

Some of the things you might test for in a route:

- when a request is received, that the expected HTTP status code is returned
- when a request is received, a particular element of value of an element is present on the page
- when a request is received, if the route includes a redirect, that the redirect is to the expected url
- when a request is received, check that the form data is as expected
- when a request is received that contains JSON data, check that the JSON is valid

When you make a request in Flask, a response is returned. The response contains [attributes](https://tedboy.github.io/flask/generated/generated/flask.Response.html#attributes), so you can assert for values in one or more of these. The attributes you will mostly use are:

- response.status_code  - the HTTP status code as a number
- response.data - gets the data content
- response.data.decode() - gets the content without the HTML tags
- response.json - get the JSON content

Create a python file within the tests folder where you will place all the tests for the routes.

### Paralympic app routes

Create the first test the paralympics app to test that when the '/noc' routes is requested that a '200' status code is returned (i.e. that the page was successfully returned).

```python
def test_get_all_regions(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP GET request is made to '/noc'
    THEN the status code should be 200, the code 'AFG' should be in the response data and the content type "application/json"
    """
    response = client.get("/noc")
    assert response.status_code == 200
    assert b"AFG" in response.data
    assert response.content_type == "application/json"
```

Some routes require you to pass data to them. For example a POST route to '/noc' to add a new region.

This test has more complex logic as we need to check if the data is in the database first or not (a better approach would be to modify the route to handle the exception and to handle the rolling back of database errors between tests. Handling errors is covered in week 10, rolling back database changes between tests is not covered, however if you search you will find examples of fixtures that will do this).

```python
def test_add_region(test_client):
    """
    GIVEN a Region model
    WHEN the HTTP POST request is made to /noc
    THEN a new region should be inserted in the database so there is 1 more row; and the response returned with the new region in JSON format
    """

    region = Region(
        NOC="NEW", region="New Region", notes="Some notes about the new region"
    )

    region_json = {
        "NOC": "NEW",
        "region": "New Region",
        "notes": "Some notes about the new region",
    }

    # Check if the region exists, it does then delete it
    exists = db.session.execute(
        db.select(Region).filter_by(NOC=region.NOC)
    ).scalar()
    if exists:
        db.session.execute(db.delete(Region).where(Region.NOC == region.NOC))
        db.session.commit()

    # Count() is not well explained in the documentation, try
    # https://github.com/sqlalchemy/sqlalchemy/issues/5908
    # Count the number of regions before adding a new one
    num_regions_in_db = db.session.scalar(
        db.select(db.func.count()).select_from(Region)
    )
    # Add a new region
    response = client.post("/noc", json=region_json)
    # Count the number of regions after the new region is added
    num_regions_in_db_after = db.session.scalar(
        db.select(db.func.count()).select_from(Region)
    )
    data = response.json
    assert response.status_code == 201
    assert "NEW" in data["NOC"]
    assert (num_regions_in_db_after - num_regions_in_db) == 1

```

To run the tests (change the directory name to whatever you named them):

`python -m pytest -v tests/tests_paralympics_app/`

Now try and write some of your own tests:

```python
def test_get_all_regions(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP GET request is made to '/noc'
    THEN the status code should be 200, the code 'AFG' should be in the response data and the content type "application/json"
    """

def test_get_specific_region(test_client):
    """
    GIVEN a running Flask app
    WHEN the "/noc/<code>" route is requested with the GBR code
    THEN the response should contain the region UK
    """

def test_delete_region(test_client):
    """
    GIVEN a region json AND the Region is in the database
    WHEN the DELETE "/noc/<code>" route is called
    THEN check the fields are defined correctly
    """

```

### Iris app routes

This assumes you've already created the fixture to run the app with a test client. The tests will fail otherwise.

Create a test for the homepage in an appropriately named test file (e.g. `tests/tests_iris_app/test_routes.py`):

```python
def test_index_success(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP GET request is made to '/'
    THEN the status code should be 200
    AND the page should contain the the html <title>Iris Home</title>"
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"<title>Iris Home</title>" in response.data
```

To run the test: `python -m pytest -v tests/tests_iris_app/` replacing the directory name(s) with the name(s) you used.

Use `python -m pytest -v tests/tests_iris_app/ --disable-warnings` if you don't want to keep seeing the package deprecation warnings.

The tests take a while to run the first time.

For the second test, test that you can post a form on the page and get a prediction result.

To do this make sure in your fixture that you set the parameter 'WTF_CSRF_ENABLED = False' or your test will fail due to CSRF protection.

You can pass values for the [form data to the request](https://flask.palletsprojects.com/en/2.2.x/testing/#form-data).

Try the following:

```python
def test_prediction_when_form_submitted(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP POST request is made to '/' with form data
    THEN the page should return a prediction result with the test "Predicted Iris type"
    AND the status code should be 200 OK
    """
    form_data = {
        "sepal_length": 5.0,
        "sepal_width": 3.3,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/", data=form_data)
    assert response.status_code == 200
    assert b"Predicted Iris type" in response.data
```

Now try and write the following tests yourself:

```python
def test_iris_contains_table(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP GET request is made to '/iris'
    THEN the page should have a table
    AND the status code should be 200 OK
    """


def test_new_user_created_when_form_submitted(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP POST request is made to '/register' with valid form data for the email and password
    THEN the page should return a message "You are registered!"
    AND the email should be on the page
    AND the status code should be 200 OK
    """


def test_error_when_register_form_email_format_not_valid(test_client):
    """
    GIVEN a running Flask app
    WHEN an HTTP POST request is made to '/register' with form data where the email is not an email address format
    THEN the page should return a message "This field is required."
    AND the status code should be 200 OK
    """
 ```
