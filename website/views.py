from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Event
from . import db
import json
from datetime import datetime, timedelta

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/savesettings', methods=['POST', 'GET'])
@login_required
def savesettings():
    if request.form:
        data = request.form
        current_user.base = data["base"]
        current_user.overtimes1 = data["overtimes1"]
        current_user.overtimes2 = data["overtimes2"]
        current_user.holidayrate = data["holidayrate"]
        current_user.sick = data["sick"]
        current_user.shiftallowance1 = data["shiftallowance1"]
        current_user.shiftallowance2 = data["shiftallowance2"]
        current_user.shiftallowance3 = data["shiftallowance3"]
        current_user.shiftallowance4 = data["shiftallowance4"]
        current_user.shiftallowance5 = data["shiftallowance5"]
        current_user.tax = data["tax"]
        db.session.add(current_user)
        db.session.commit()
    
    return render_template("settings.html", user=current_user)

def calculate_payment(date_hour_relation, overtime, holiday, sick):
    hours = {
        "base": 0,
        "overtimes1": 0,
        "overtimes2": 0,
        "holiday": 0,
        "sick": 0,
        "shiftallowance1": 0,
        "shiftallowance2": 0,
        "shiftallowance3": 0,
        "shiftallowance4": 0,
        "shiftallowance5": 0,
    }
    if overtime:
        for element in date_hour_relation:
            hours = calculate_overtimes_hours(element, hours)
    elif holiday:
        hours["holiday"] = len(date_hour_relation)
    elif sick:
        for element in date_hour_relation:
            hours = calculate_sick(element, hours)
    else:
        for element in date_hour_relation:
            hours = calculate_hours(element, hours)
        hours = calculate_sa(date_hour_relation[-1], hours)
    return hours


def calculate_overtimes_hours(element, hours):
    weekday,hour = element.split("-")
    hours_worked = int(weekday) * 24 + int(hour)
    if 6 <= hours_worked < 134:
        hours["overtimes1"] += 1
    else:
        hours["overtimes2"] += 1
    return hours
        

def calculate_hours(element, hours):
    weekday,hour = element.split("-")
    int_hour = int(hour)
    hours_worked = int(weekday) * 24 + int_hour
    if 6 <= hours_worked < 126:
        hours["base"] += 1
    elif 126 <= hours_worked < 134:
        hours["overtimes1"] += 1
    else:
        hours["overtimes2"] += 1
    return hours

def calculate_sick(element, hours):
    weekday,hour = element.split("-")
    int_hour = int(hour)
    hours_worked = int(weekday) * 24 + int_hour
    if 6 <= hours_worked < 126:
        hours["sick"] += 1
    return hours

def calculate_sa(element, hours):
    weekday,hour = element.split("-")
    int_hour = int(hour)
    hours_worked = int(weekday) * 24 + int_hour
    if 6 <= hours_worked < 126:
        if 6 <= int_hour < 22:
            hours["shiftallowance2"] += 1
        else:
            hours["shiftallowance2"] += 1
            hours["shiftallowance3"] += 1
    elif 126 <= hours_worked < 134:
        hours["shiftallowance2"] += 1
    else:
        if 134 <= hours_worked < 142 or 150 <= hours_worked < 166:
            hours["shiftallowance2"] += 1
        else:
            hours["shiftallowance2"] += 1
            hours["shiftallowance4"] += 1
    return hours

@views.route('/saveday', methods=['POST'])
def saveday():
    data = json.loads(request.data)
    delete = data["delete_events"]
    if delete:
        id_to_delete = None
        events = Event.query.filter(Event.user_id==current_user.id).all()
        current_date = data['currentDate']
        print(current_date)
        for event in events:
            if event.startHours.strftime("%Y-%m-%d")==current_date:
                id_to_delete = event.id
                break
        if id_to_delete:
            id = id_to_delete
            zmienna = Event.query.get(id)
            db.session.delete(zmienna)
            db.session.commit()
            return jsonify({})
    
    start = data["startHours"]
    if ":" not in start:
        start += ":00"
    start_date = datetime.strptime(f"{data['currentDate']} {start}", "%Y-%m-%d %H:%M")
    print(start_date)
    hours_worked = int(data["hoursWorked"])
    date_hour_relation = []
    for hour in range(hours_worked):
        tmp_date = start_date + timedelta(hours=hour)
        date_hour_relation.append(f"{tmp_date.weekday()}-{tmp_date.hour}")
    hours = calculate_payment(date_hour_relation, data["overtimes"], data["holiday"], data["sick"]) 
    event = Event(
        user_id=current_user.id,
        startHours=start_date, 
        hoursWorked=hours_worked, 
        basehours=data["basehours"], 
        overtimes=data["overtimes"], 
        holiday=data["holiday"], 
        sick=data["sick"], 
        base_count=hours["base"],
        overtimes1_count=hours["overtimes1"],
        overtimes2_count=hours["overtimes2"],
        holiday_count=hours["holiday"],
        sick_count=hours["sick"],
        shiftallowance1_count=hours["shiftallowance1"],
        shiftallowance2_count=hours["shiftallowance2"],
        shiftallowance3_count=hours["shiftallowance3"],
        shiftallowance4_count=hours["shiftallowance4"],
        shiftallowance5_count=hours["shiftallowance5"],
        )
    db.session.add(event)
    db.session.commit()

    return jsonify({})

@views.route('/getEvents')
def get_events():
    events = Event.query.filter(Event.user_id==current_user.id)
    events_as_dict = [event.get_dict() for event in events]
    return jsonify(events_as_dict)

@views.route('/calculate_payment', methods=['POST'])
def calculate_final_payment():
    hours = {}
    if request.form:
        month_from = request.form["from"]
        month_to = request.form["to"]
        start_date = datetime.strptime(f"{month_from} 6:00", "%Y-%m-%d %H:%M")
        end_date = datetime.strptime(f"{month_to} 6:00", "%Y-%m-%d %H:%M")
        events = Event.query.filter(Event.user_id==current_user.id).filter(Event.startHours >= start_date).filter(Event.startHours < end_date).all()
        hours = {
        "base": {"count": 0, "rate": current_user.base, "value": 0},
        "overtimes1": {"count": 0, "rate": current_user.overtimes1, "value": 0},
        "overtimes2": {"count": 0, "rate": current_user.overtimes2, "value": 0},
        "holiday": {"count": 0, "rate": current_user.holidayrate / 8, "value": 0},
        "sick": {"count": 0, "rate": current_user.sick, "value": 0},
        "shiftallowance1": {"count": 0, "rate": current_user.shiftallowance1, "value": 0},
        "shiftallowance2": {"count": 0, "rate": current_user.shiftallowance2, "value": 0},
        "shiftallowance3": {"count": 0, "rate": current_user.shiftallowance3, "value": 0},
        "shiftallowance4": {"count": 0, "rate": current_user.shiftallowance4, "value": 0},
        "shiftallowance5": {"count": 0, "rate": current_user.shiftallowance5, "value": 0},
        }
        

        for day_event in events:
            hours["base"]["count"] += day_event.base_count
            hours["overtimes1"]["count"] += day_event.overtimes1_count
            hours["overtimes2"]["count"] += day_event.overtimes2_count
            hours["holiday"]["count"] += day_event.holiday_count
            hours["sick"]["count"] += day_event.sick_count
            hours["shiftallowance1"]["count"] += day_event.shiftallowance1_count
            hours["shiftallowance2"]["count"] += day_event.shiftallowance2_count
            hours["shiftallowance3"]["count"] += day_event.shiftallowance3_count
            hours["shiftallowance4"]["count"] += day_event.shiftallowance4_count
            hours["shiftallowance5"]["count"] += day_event.shiftallowance5_count
        
        total_payment = 0

        for key, value in hours.items():
            hours[key]["value"] = value["count"] * value["rate"]
            total_payment += hours[key]["value"]
        
        total_payment_after_tax = total_payment * (1 - current_user.tax / 100)

        print(total_payment, total_payment_after_tax)
    return render_template("results.html", user=current_user, hours=hours, total_payment=total_payment, total_payment_after_tax=total_payment_after_tax)