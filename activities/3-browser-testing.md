# Browser-based tests using Selenium WebDriver

You may also see these referred to as 'front-end tests', 'end-to-end' tests or possibly even 'integration' tests.

This activity assumes you completed the routes activities and have created the pytest fixtures from that activity.

In this activity the tests require simulation of user actions in a web brower using a Chrome driver and Selenium; and test assertions using pytest.

## Contents

- [Create test modules](#create-test-modules)
- [Install Chrome driver](#install-chrome-driver)
- [Write pytest fixtures](#write-pytest-fixtures)
- [Browser tests for the paralympic app](#selenium-tests-for-the-paralympic-app)
- [Browser tests for the iris app](#selenium-tests-for-the-iris-app)

Note: the tests for the paralmpic app and iris app use different approaches so you should try and complete both sets of activities.

## Create test modules

Add test modules/python files for the selenium tests for each app to the test directory.

Use appropriate file names e.g. `test_para_front_end.py` and `test_iris_front_end.py`.

## Install Chrome driver

Before starting, make sure you have a Chrome driver installed that is correct for your version of Chrome and your operating system. You may have one from testing the Dash app, if not then make sure you install one now. See [COMP0034 week 4 activities](https://github.com/nicholsons/comp0034-week4/blob/main/activities/activities.md#download-and-install-the-correct-version-of-chromedriver-for-your-computer).

## Write pytest fixtures

You need two fixtures: (1) to start a live server; and (2) to configure the chrome driver.

Add these to your `conftest.py`.

Note: the `week-9-complete` repo code contains multiple `conftest.py` files to separate the fixtures for each app.

###  Fixture to configure the Chrome driver

In the Chrome driver for the tests to run on a remote server that doesn't have a screen (like GitHub Actions) you need to make sure that headless is set. However, it is useful to see the tests running in a browser when testsing on your own computer.

Add a fixture that configures the chrome driver for either environment.

```python
@pytest.fixture(scope='class')
def chrome_driver():
    """ Selenium webdriver with options to support running in GitHub actions
    Note:
        For CI: `headless` not commented out, comment out driver.maximise_window()
        For running on your computer: `headless` to be commented out, use driver.maximise_window()
    """
    options = ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()
```

### Fixture to create a live server

While you have a fixture for running the Flask app with a test client for the routes; this won't work for running the tests for Selenium. The Selenium tests assume that the app is running on a live server (which yours is not); this means that you need to run the app and run the test code in parallel. To do this you start the server in a new 'thread'.

For MacOS you can use a standard Python package called 'multiprocessing' (other options exist).

For Windows you will need to use a standard package called 'subprocess' as the multiprocessing fork method appears not be to be supported. To start Flask using this method you will also need to modify the `__init__.py create_app()` function to take config from a file or class. In the code you will see that the method now uses classes defined in `config.py`.

The following fixtures run the app in a thread.

#### macOS fixtures

```python
@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing"""
    app = create_app(config.TestConfig)
    yield app


@pytest.fixture(scope='module')
def run_app(app):
    """
    Runs the Flask app as a live server for Selenium tests on MacOS
    """
    multiprocessing.set_start_method("fork")  # Fork needed in Python 3.8 and later
    process = multiprocessing.Process(target=app.run, args=())
    process.start()
    yield process
    process.terminate()
```

#### Windows fixture

```python
@pytest.fixture(scope="module", autouse=True)
def run_app():
    """
    Runs the Flask app as a live server for Selenuin tests on Windows (Paralympic app)
    """
    server = subprocess.Popen(
        [
            "flask",
            "--app",
            "paralympic_app:create_app('paralympic_app.config.TestConfig')",
            "run",
            "--port",
            "5000"
        ]
    )
    try:
        yield server
    finally:
        server.terminate()

```

Note that `multiprocessing.set_start_method()` for macOS can only be run once per session otherwise you will get a runtime error. In the week 10 code you will see an additional fixture to handle this as there are tests for several apps that could potentially call the method twice. This is unlikely to be an issue for you in your coursework though. The `week 9 complete` version has the following fixture:

```python
import pytest
import multiprocessing


@pytest.fixture(scope="session")
def init_multiprocessing():
    """Sets multiprocessing to fork once per session.

    If already set once then on subsequent calls a runtime error will be raised which should be ignored.

    Needed in Python 3.8 and later
    """
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        pass
```

The use of multiprocessing or subprocess to start the app for testing is not clearly documented anywhere. Much of the information is in forum posts and contained in the code for other packages.

**pytest-flask liver_server fixture alternative for macOS (not Windows)**: To avoid handling the running of the app as a live server yourself, you can use a package such as `pytest-flask`. This provides a [live_server fixture for Selenium tests](https://pytest-flask.readthedocs.io/en/latest/features.html#live-server-application-live-server). Install it as you would for any other package, e.g. `pip install pytest-flask`. The fixture will automatically be available to you once this is installed.

I encountered the following with pytest-flask:

- Do not use on Windows as the live_server fixture in pytest-flask uses multiprocessing!
- Make sure you have a fixture called `app` (not any other name) that runs your app code and that it has session scope i.e. `scope="session"`.
- Check that your `test_client` fixture is not called `client`; as pytest-flask includes a fixture with this name and it wasn't clear how to control which version of the `client` fixture is used.

**In the week-9-complete code, the tests for the paralympics app uses the `run_app` fixture approach; the tests for the iris app use the pytest-flask live_server fixture approach.**. This is to give an illustration of using both approaches. Use either for your coursework.

## Selenium tests for the paralympic app

A REST API does not have a web browser user interface. To allow tests to be created for the app, a couple of routes have been added that use data from the API to create pages purely to provide something to test:

- '/' generates a page with hyperlinks for each event in the dataset
= '/display_event/<event_id>' generates a page with the event details for a particular event

Run the app so you can see what is in the interface: `python -m flask --app 'paralympic_app:create_app("paralympic_app.config.DevConfig")' --debug run`

The code approach to create a Selenium test is broadly:

- if you are using Python 3.8 or later, set the multiprocessing start method to 'fork'
- use a fixture to create a running app in a server on a thread
- initialise a chrome_driver
- use the driver to navigate to a URL
- use the driver find an element on a page
- (optionally) use the driver interact with one or more elements such as enter a value, or click
- use the driver to find the value of an element
- use a pytest assert to assert that the value equals an expected value (or other comparison)

The first test example below is to test that the home page is accessed.

The fixtures for chrome_driver and live running app are passed to the test. The test then uses the chrome driver function to make a GET request to the homepage. Flask runs on port 5000 by default, if you set Flask to run on a different port you'll need to change the code below.

The code then waits for 3 seconds, this is not really necessary however it means the the page should be visible for 3 seconds allowing you the opportunity to see the browser is being controlled by the chrome driver, otherwise it would be too quick for you to see.

The driver is then used to get the `<title>` from the `<head>` of the page. The pytest assertion is then used to check that the page title is as expected. You can see the title in the `index.html` template for the paralympics app.

Add the following code to

```python
def test_home_page_title(chrome_driver, run_app):
    """
    GIVEN a running app
    WHEN the homepage is accessed
    THEN the value of the page title should be "Paralympics Home"
    """
    chrome_driver.get("http://127.0.0.1:5000/")
    chrome_driver.implicitly_wait(3)
    assert chrome_driver.title == "Paralympics Home"
```

Add the above test to an appropriately named python module in your tests folder and run the tests.

e.g. `python -m pytest -v tests/tests_paralympic_app/test_para_front_end.py --disable-warnings` replacing the test path with the name as it is on your computer

The following test has more steps:

```python
def test_event_detail_page_selected(chrome_driver, run_app):
    """
    GIVEN a running app
    WHEN the homepage is accessed
    AND the user clicks on the event with the id="1"
    THEN a page with the title "Rome" should be displayed
    AND the page should contain an element with the id "highlights" should be displayed and contain a text value "First Games"
    """
    chrome_driver.get("http://127.0.0.1:5000/")
    # Wait until the element with id="1" is on the page  https://www.selenium.dev/documentation/webdriver/waits/ and then click on it
    el_1 = WebDriverWait(chrome_driver, timeout=3).until(
        lambda d: d.find_element(By.ID, "1")
    )
    el_1.click()
    # Find the text value of the event highlights
    text = chrome_driver.find_element(By.ID, "highlights").text
    assert "First Games" in text

```

Try and create your own test. For example:

```python
def test_home_nav_link_returns_home(chrome_driver, run_app):
    """
    GIVEN a running app
    WHEN the homepage is accessed
    AND the user clicks on the event with the id="1"
    AND the user clicks on the navbar in the 'Home' link
    THEN the page url should be "http://127.0.0.1:5000/"
    """
```

## Selenium tests for the iris app

Run the app so you can see what is in the interface.

`python -m flask --app 'iris_app:create_app("iris_app.config.DevConfig")' --debug run`

Read the section on [selenium tests for the paralympic app](#selenium-tests-for-the-paralympic-app) for a general overview of the code approach for selenium webdriver tests.

The Iris App has slightly more in the interface that can be tested via the browser:

- The homepage displays a form with fields for sepal length, sepal width, petal length and petal width. On submission the form returns a prediction of the iris species
- The nabvar includes links to the home page, iris data set and register
- The Iris dataset page a page that lists all the iris details from the data set
- The register page contains for form for a new user to register for an account. The form requires and email address and password to be entered

In the week 10 code the tests for the iris_app use the pytest-flask library. If you don't want to use this, then look at the examples for the `paralympic app` instead.

Install pytest-flask.

Make sure your fixture that creates the Flask app is called `app` and that your test client fixture is not called `client`.

Create a test using the pytest-flask `live_server` fixture to check that the app is up and running:

```python
import requests
from flask import url_for


def test_server_is_up_and_running(init_multiprocessing, live_server):
    response = requests.get(url_for("index", _external=True))
    assert b"Iris Home" in response.content
    assert response.status_code == 200
```

Create a test that completes a form to get a prediction of iris species.

The data is just copied from the data set, though you can make up data. Data used: 4.8,3.0,1.4,0.1,setosa

If you run the app and use a browser developer tool option to view the source, then you can find the `id`s and `name`s for the elements on the form. For example:

![inspect element screenshot](/activities/inspect-element.png)

The following test uses [Selenium `send_keys()`](https://www.selenium.dev/documentation/webdriver/elements/interactions/#send-keys) to complete form fields; and [`click()`](https://www.selenium.dev/documentation/webdriver/elements/interactions/#click) to press the 'Predict' button.

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def test_prediction_returns_value(live_server, chrome_driver):
    """
    GIVEN a live_server with the iris predictor app
    WHEN the url for the home page is entered
    AND valid details are entered in the prediction form fields
    AND the form is submitted
    THEN the <p id="prediction-text"> element should include the word "setosa"
    """
    iris = {
        "sepal_length": 4.8,
        "sepal_width": 3.0,
        "petal_length": 1.4,
        "petal_width": 0.1,
        "species": "iris-setosa",
    }
    # Go to the home page, you can use the Flask url_for to avoid hard-coding the URL
    chrome_driver.get(url_for("index", _external=True))
    # Complete the fields in the form
    sep_len = chrome_driver.find_element(By.NAME, "sepal_length")
    sep_len.send_keys(iris["sepal_length"])
    sep_wid = chrome_driver.find_element(By.NAME, "sepal_width")
    sep_wid.send_keys(iris["sepal_width"])
    pet_len = chrome_driver.find_element(By.NAME, "petal_length")
    pet_len.send_keys(iris["petal_length"])
    pet_wid = chrome_driver.find_element(By.NAME, "petal_width")
    pet_wid.send_keys(iris["petal_width"])
    # Click the submit button
    chrome_driver.find_element(By.ID, "btn-predict").click()
    # Wait for the prediction text to appear on the page then get the element
    pt = WebDriverWait(chrome_driver, timeout=3).until(
        lambda d: d.find_element(By.ID, "prediction-text")
    )
    # Assert that 'setosa' is in the text value of the <p "prediction-text"> element. This assumes the model correctly predicts the species!
    assert iris["species"] in pt.text
```

Now try and create some tests yourself. There are many more tests you could come up with for this app, try and think of your own. Here are a couple of suggestions to start with:

```python
def test_register_form_on_submit_returns(live_server):
    """
    GIVEN a live_server with the iris predictor app
    WHEN the url for the register is entered
    AND valid details are entered in the email and password fiels
    AND the form is submitted
    THEN the page content should include the words "You are registered!" and the email address
    """

def test_register_link_from_nav(client, live_server):
    """
    GIVEN a live_server with the iris predictor app
    WHEN the url for the homepage is entered
    THEN the page title should equal "Iris Home"
    """
```
