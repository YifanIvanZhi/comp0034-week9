from flask import (
    render_template,
    current_app as app,
    request,
    make_response,
    jsonify,
)
from paralympic_app import db
from paralympic_app.models import Region, Event
from paralympic_app.schemas import RegionSchema, EventSchema


# -------
# Schemas
# -------

regions_schema = RegionSchema(many=True)
region_schema = RegionSchema()
events_schema = EventSchema(many=True)
event_schema = EventSchema()

# ------
# Routes
# ------


@app.route("/")
def index():
    """Returns the home page"""
    return render_template("index.html")


@app.get("/noc")
def noc():
    """Returns a list of NOC region codes and their details in JSON."""

    # Query using the syntax in the Flask-SQLAlchemy 3.x documentation
    # https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/#select
    all_regions = db.session.execute(db.select(Region)).scalars()
    # Get the data using Marshmallow schema
    result = regions_schema.dump(all_regions)
    return jsonify(result)


@app.get("/noc/<code>")
def noc_code(code):
    """Returns the details for a given region code."""
    # Return a 404 code if the region is not found in the database
    region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    result = region_schema.dump(region)
    return jsonify(result)


@app.post("/noc")
def noc_add():
    """Adds a new NOC record to the dataset."""
    NOC = request.json.get("NOC", "")
    region = request.json.get("region", "")
    notes = request.json.get("notes", "")
    region = Region(NOC=NOC, region=region, notes=notes)
    db.session.add(region)
    db.session.commit()
    result = region_schema.jsonify(region)
    return result


@app.patch("/noc/<code>")
def noc_update(code):
    """Updates changed fields for the NOC record"""
    # https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/#insert-update-delete
    # Find the current region in the database
    existing_region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    # Get the updated details from the json sent in the HTTP patch request
    region_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes in the json
    region_schema.load(region_json, instance=existing_region, partial=True)
    # Commit the changes to the database
    db.session.commit()
    # Return json showing the updated record
    existing_region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    result = region_schema.jsonify(existing_region)
    return result


@app.delete("/noc/<code>")
def noc_delete(code):
    """Removes a NOC record from the dataset."""
    region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    db.session.delete(region)
    db.session.commit()
    # This example returns a custom HTTP response using flask make_response
    # https://flask.palletsprojects.com/en/2.2.x/api/?highlight=make_response#flask.make_response
    text = jsonify({"Successfully deleted": region.NOC})
    response = make_response(text, 200)
    response.headers["Content-type"] = "application/json"
    return response


@app.get("/event")
def event():
    """Returns the details for all events"""
    all_events = db.session.execute(db.select(Event)).scalars()
    return events_schema.dump(all_events)


@app.get("/event/<int:event_id>")
def event_id(event_id):
    """Returns the details for a specified event"""
    event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).one()
    return events_schema.dump(event)


@app.post("/event")
def event_add():
    """Adds a new event record to the dataset."""
    type = request.json.get("type")
    year = request.json.get("year")
    location = request.json.get("location")
    lat = request.json.get("lat")
    lon = request.json.get("lon")
    NOC = request.json.get("NOC")
    start = request.json.get("start")
    end = request.json.get("end")
    disabilities_included = request.json.get("disabilities_included")
    events = request.json.get("events")
    sports = request.json.get("sports")
    countries = request.json.get("countries")
    male = request.json.get("male")
    female = request.json.get("female")
    participants = request.json.get("participants")
    highlights = request.json.get("highlights")

    event = Event(
        type=type,
        year=year,
        location=location,
        lat=lat,
        lon=lon,
        NOC=NOC,
        start=start,
        end=end,
        disabilities_included=disabilities_included,
        events=events,
        sports=sports,
        countries=countries,
        male=male,
        female=female,
        participants=participants,
        highlights=highlights,
    )
    db.session.add(event)
    db.session.commit()
    # TODO: find the id  of the last record and then query the database as we need the id
    print(event.event_id, file=sys.stderr)
    result = event_schema.jsonify(event)
    return result


@app.patch("/event/<event_id>")
def event_update(event_id):
    """Updates changed fields for the event
    TODO: does not handle a partial update despite partial=True
    """
    # Find the current event in the database
    existing_event = db.one_or_404(
        db.select(Event).filter_by(event_id=event_id)
    )
    # Get the updated details from the json sent in the HTTP patch request
    event_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes in the json
    event_schema.load(event_json, instance=existing_event, partial=True)
    # Commit the changes to the database
    db.session.commit()
    # Return json showing the updated record
    existing_event = db.one_or_404(
        db.select(Event).filter_by(event_id=event_id)
    )
    result = event_schema.jsonify(existing_event)
    return result