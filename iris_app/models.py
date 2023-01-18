from iris_app import db


class Iris(db.Model):
    """Iris class"""

    __tablename__ = "iris"
    rowid = db.Column(db.Integer, primary_key=True)
    sepal_length = db.Column(db.Float, nullable=False)
    sepal_width = db.Column(db.Float, nullable=False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    species = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """
        Returns the attributes of an iris as a string
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.sepal_length}, {self.sepal_width}, {self.petal_length}, {self.petal_width}, {self.species}>"


class User(db.Model):
    """Class to represent users who have created a login"""

    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """
        Returns the attributes of a User as a string, except for the password
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.user_id}, {self.email}>"
