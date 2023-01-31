from pathlib import Path
import pickle
from flask import render_template, current_app as app, request
import numpy as np
from iris_app.forms import PredictionForm, UserForm
from iris_app import db
from iris_app.models import Iris, User


pickle_file = Path(__file__).parent.joinpath("data", "model_lr.pkl")
IRIS_MODEL = pickle.load(open(pickle_file, "rb"))


@app.route("/", methods=["GET", "POST"])
def index():
    """Create the homepage"""
    form = PredictionForm()

    if form.validate_on_submit():

        # Get all values from the form
        features_from_form = [
            form.sepal_length.data,
            form.sepal_width.data,
            form.petal_length.data,
            form.petal_width.data,
        ]

        # Make the prediction
        prediction = make_prediction(features_from_form)

        prediction_text = f"Predicted Iris type: {prediction}"

        return render_template(
            "index.html", form=form, prediction_text=prediction_text
        )
    return render_template("index.html", form=form)


# The predict route is no longer needed
@app.get("/predict")
def predict():
    """Predict iris species

    Takes the arguments sepal_length,sepal_width,petal_length,petal_width  from an HTTP request. Passes the arguments to the model and returns a prediction (classification of Iris species).

    Returns:
        species(str): A string of the iris species.
    """

    sepal_length = request.args.get("sep-len")
    sepal_width = request.args.get("sep-wid")
    petal_length = request.args.get("pet-len")
    petal_width = request.args.get("pet-wid")

    prediction = make_prediction(
        [sepal_length, sepal_width, petal_length, petal_width]
    )

    return prediction


def make_prediction(flower_values):
    """Takes the flower values, makes a model using the prediction and returns a string of the predicted flower variety

    Parameters:
    flower_values (List): List of sepal length, sepal width, petal length, petal width

    Returns:
    variety (str): Name of the predicted iris variety
    """

    # Convert to a 2D numpy array with float values, needed as input to the model
    input_values = np.asarray([flower_values], dtype=float)

    # Get a prediction from the model
    prediction = IRIS_MODEL.predict(input_values)

    # convert the prediction to the variety name
    varieties = {0: "iris-setosa", 1: "iris-versicolor", 2: "iris-virginica"}
    variety = np.vectorize(varieties.__getitem__)(prediction[0])

    return variety


@app.route("/iris")
def iris_list():
    """Render page with a list of all the iris entries from the database"""
    iris = db.session.execute(db.select(Iris)).scalars()
    return render_template("iris.html", iris_list=iris)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = UserForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        text = f"<p>You are registered! {repr(new_user)}</p>"
        return text
    return render_template("register.html", form=form)
