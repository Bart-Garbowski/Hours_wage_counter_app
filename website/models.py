from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    base = db.Column(db.Float, nullable=True)
    overtimes1 = db.Column(db.Float, nullable=True)
    overtimes2 = db.Column(db.Float, nullable=True)
    holidayrate = db.Column(db.Float, nullable=True)
    sick = db.Column(db.Float, nullable=True)
    shiftallowance1 = db.Column(db.Float, nullable=True)
    shiftallowance2 = db.Column(db.Float, nullable=True)
    shiftallowance3 = db.Column(db.Float, nullable=True)
    shiftallowance4 = db.Column(db.Float, nullable=True)
    shiftallowance5 = db.Column(db.Float, nullable=True)
    tax = db.Column(db.Float, nullable=True)



class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    startHours = db.Column(db.DateTime(timezone=True))
    hoursWorked = db.Column(db.Float)
    basehours = db.Column(db.Boolean)
    overtimes = db.Column(db.Boolean)
    holiday = db.Column(db.Boolean)
    sick = db.Column(db.Boolean)
    base_count = db.Column(db.Integer)
    overtimes1_count = db.Column(db.Integer)
    overtimes2_count = db.Column(db.Integer)
    holiday_count = db.Column(db.Integer)
    sick_count = db.Column(db.Integer)
    shiftallowance1_count = db.Column(db.Integer)
    shiftallowance2_count = db.Column(db.Integer)
    shiftallowance3_count = db.Column(db.Integer)
    shiftallowance4_count = db.Column(db.Integer)
    shiftallowance5_count = db.Column(db.Integer)
    def get_dict(self):
        return {
            "start_hours": str(self.startHours.date()),
            "hours_worked": self.hoursWorked,
            "base_hours": self.basehours,
            "overtimes": self.overtimes,
            "holiday": self.holiday,
            "sick": self.sick,
        }