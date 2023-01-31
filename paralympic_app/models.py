from paralympic_app import db


class Region(db.Model):
    """NOC region"""

    __tablename__ = "region"
    NOC = db.Column(db.Text, primary_key=True)
    region = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    events = db.relationship("Event", back_populates="region")

    def __repr__(self):
        """
        Returns the attributes of the region as a string
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.NOC}, {self.region}, {self.notes}>"


class Event(db.Model):
    """Paralympic event"""

    __tablename__ = "event"
    event_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    location = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Text)
    lon = db.Column(db.Text)
    NOC = db.Column(db.Text, db.ForeignKey("region.NOC"), nullable=False)
    start = db.Column(db.Text, nullable=False)
    end = db.Column(db.Text, nullable=False)
    disabilities_included = db.Column(db.Text, nullable=False)
    events = db.Column(db.Text, nullable=False)
    sports = db.Column(db.Text, nullable=False)
    countries = db.Column(db.Integer, nullable=False)
    male = db.Column(db.Integer, nullable=False)
    female = db.Column(db.Integer, nullable=False)
    participants = db.Column(db.Integer, nullable=False)
    highlights = db.Column(db.Text)
    region = db.relationship("Region", back_populates="events")

    def __repr__(self):
        """
        Returns the attributes of the event as a string
        :returns str
        """
        clsname = self.__class__.__name__
        return f"<{clsname}: {self.type},{self.type}, {self.year}, {self.location}, {self.lat}, {self.lon}, {self.NOC}, {self.start}, {self.end}, {self.disabilities_included}, {self.events}, {self.sports}, {self.countries}, {self.male}, {self.female}, {self.participants}, {self.highlights}>"
