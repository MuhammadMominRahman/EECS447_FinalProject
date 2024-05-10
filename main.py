from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
import time

temp_string = ""

app = Flask(__name__)
app.secret_key = "test key"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICAITONS"] = False

database = SQLAlchemy(app)

class users(database.Model):
    _un = database.Column(database.String(100), primary_key=True)

    #addition 1
    custom_lists = database.relationship("CustomList", backref='users')

    def __init__(self, _un):
        self._un = _un

    def __repr__(self):
        return f"{self._un}"

class CustomList(database.Model):
    custom_name = database.Column(database.String(100), primary_key=True)
    creation_date = database.Column(database.String(100))

    #addition 2
    user_id = database.Column(database.String(100), database.ForeignKey('users._un'))


    car_customs = database.relationship('CarCustom', backref='custom_list', lazy=True)
    moto_customs = database.relationship('MotoCustom', backref='custom_list', lazy=True)
    plane_customs = database.relationship('PlaneCustom' , backref='custom_list', lazy=True)

    def __init__(self, custom_name, creation_date, user_id):
        self.custom_name = custom_name
        self.creation_date = creation_date
        self.user_id = user_id

class CarCustom(database.Model):
    identification = database.Column(database.Integer, primary_key=True)
    car_size = database.Column(database.String(100))
    car_trim = database.Column(database.String(100))
    car_cyl = database.Column(database.String(100))
    car_dt = database.Column(database.String(100))
    car_tr = database.Column(database.String(100))
    car_color = database.Column(database.String(100))
    custom_list_name = database.Column(database.String(100),database.ForeignKey('custom_list.custom_name'), nullable = False)

    def __init__(self, car_size, car_trim, car_cyl, car_dt, car_tr, car_color, custom_list_name):
        self.custom_list_name = custom_list_name
        self.car_size = car_size
        self.car_trim = car_trim
        self.car_cyl = car_cyl
        self.car_dt = car_dt
        self.car_tr = car_tr
        self.car_color = car_color

class MotoCustom(database.Model):
    identification = database.Column(database.Integer, primary_key=True)
    moto_type = database.Column(database.String(100))
    moto_cyl = database.Column(database.String(100))
    moto_color = database.Column(database.String(100))
    has_sidecar = database.Column(database.String(100))  # Corrected column name
    custom_list_name = database.Column(database.String(100), database.ForeignKey('custom_list.custom_name'), nullable=False)

    def __init__(self, moto_type, moto_cyl, moto_color, has_sidecar, custom_list_name):
        self.moto_type = moto_type
        self.moto_cyl = moto_cyl
        self.moto_color = moto_color
        self.has_sidecar = has_sidecar
        self.custom_list_name = custom_list_name

class PlaneCustom(database.Model):
    identification = database.Column(database.Integer, primary_key = True)
    wing_type = database.Column(database.String(100))
    plane_fuel = database.Column(database.String(100))
    engine_type = database.Column(database.String(100))
    num_engines = database.Column(database.String(100))
    plane_color = database.Column(database.String(100))
    custom_list_name = database.Column(database.String(100),database.ForeignKey('custom_list.custom_name'), nullable = False)

    def __init__(self, wing_type, plane_fuel, engine_type, num_engines, plane_color, custom_list_name):
        self.wing_type = wing_type
        self.plane_fuel = plane_fuel
        self.engine_type = engine_type
        self.num_engines = num_engines
        self.plane_color = plane_color
        self.custom_list_name = custom_list_name

@app.route("/home/<username>", methods=['GET', 'POST'])
def home(username):
    if request.method == 'POST':
        choice = request.form['choice']

        if choice == "Car":
            return redirect(url_for('car',username=username))
        elif choice == "Motorcycle":
            return redirect(url_for('mc', username=username))
        elif choice == "Airplane":
            return redirect(url_for('airplane', username=username))
        elif choice == "MyCustoms":
            return redirect(url_for('customs',username=username))
        elif choice == 'Logout':
            session.clear()
            return redirect(url_for('login'))
        else:
            return "Invalid choice"


    return render_template("home.html", content=username)

@app.route("/")
def login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_submit():
    username = None
    if request.method == 'POST':
        username = request.form['username']

        user = users.query.filter_by(_un=username).first()
        if user:
            session["username"] = username
            return redirect(url_for('home', username=username))
        else:
            un = users(_un=username)
            database.session.add(un)
            database.session.commit()

            session['username'] = username
            return redirect(url_for('home', username=username))



@app.route("/car/<username>", methods=['GET', 'POST'])
def car(username):
    user = users.query.filter_by(_un=username).first()
    if request.method == 'POST':

        car_name = request.form['carName']
        car_size = request.form['carSize']
        car_trim = request.form['carTrim']
        car_cyl = request.form['carCylinders']
        car_dt = request.form['carDrivetrain']
        car_tr = request.form['carTrans']
        car_color = request.form['carColor']


        try:
            if 'saveCar' in request.form:
                date_string = datetime.now().strftime("%Y-%m-%d")
                CustomInstance = CustomList(custom_name=car_name, creation_date=date_string, user_id=user._un)
                CarInstance = CarCustom(car_size, car_trim, car_cyl, car_dt, car_tr, car_color, custom_list_name=car_name)
                database.session.add(CustomInstance)
                database.session.add(CarInstance)
                database.session.commit()

                return render_template('dummy.html', username=username, car_name=car_name, car_size=car_size,
                                       car_trim=car_trim, car_cyl=car_cyl, car_dt=car_dt, car_tr=car_tr, car_color=car_color, user=user, date=date_string)
        except IntegrityError as e:
            database.session.rollback()
            return redirect(url_for('car',username=username))
    return render_template('car.html', username=username)

@app.route("/moto/<username>", methods=['GET', 'POST'])
def moto(username):
    user = users.query.filter_by(_un=username).first()
    if request.method == 'POST':

        moto_name = request.form['motoName']
        moto_type = request.form['motoType']
        moto_cyl = request.form['motoCylinders']
        moto_col = request.form['motoColor']
        has_sidecar = request.form['motoSidecar']


        try:
            if 'saveMoto' in request.form:
                date_string = datetime.now().strftime("%Y-%m-%d")
                CustomInstance = CustomList(custom_name=moto_name, creation_date=date_string, user_id=user._un)
                MotoInstance = MotoCustom(moto_type, moto_cyl, moto_col, has_sidecar, moto_name)
                database.session.add(CustomInstance)
                database.session.add(MotoInstance)
                database.session.commit()

                return render_template('dummy2.html', username=username, name=moto_name, cylinders=moto_cyl,
                                       color=moto_col, type=moto_type, side_car = has_sidecar)
        except IntegrityError as e:
            database.session.rollback()
            return redirect(url_for('moto', username=username))
    return render_template('moto.html', username=username)

@app.route("/plane/<username>", methods=['GET', 'POST'])
def plane(username):
    user = users.query.filter_by(_un=username).first()
    if request.method == 'POST':

        wing_type = request.form['planeWing']
        plane_fuel = request.form['planeFuel']
        engine_type = request.form['planeType']
        num_engines = request.form['planeEngines']
        plane_color = request.form['planeColor']
        plane_name = request.form['planeName']


        try:
            if 'savePlane' in request.form:
                date_string = datetime.now().strftime("%Y-%m-%d")
                CustomInstance = CustomList(custom_name=plane_name, creation_date=date_string, user_id=user._un)
                PlaneInstance = PlaneCustom(wing_type, plane_fuel, engine_type, num_engines, plane_color, plane_name)
                database.session.add(CustomInstance)
                database.session.add(PlaneInstance)
                database.session.commit()

                return render_template('dummy3.html', username=username, name=plane_name, wing_type=wing_type,
                                       color=plane_color, engine_type=engine_type, num_engines=num_engines)
        except IntegrityError as e:
            database.session.rollback()
            return redirect(url_for('plane', username=username))
    return render_template('plane.html', username=username)

@app.route("/dummy/<username>", methods=['GET', 'POST'])
def dummy(username):
    if request.method == "POST":
        return redirect(url_for('home',username=username))
    return render_template('dummy.html')

@app.route("/dummy2/<username>", methods=['GET', 'POST'])
def dummy2(username):
    if request.method == "POST":
        return redirect(url_for('home', username=username))
    return render_template('dummy2.html')

@app.route("/dummy3/<username>", methods=['GET', 'POST'])
def dummy3(username):
    if request.method == "POST":
        return redirect(url_for('home', username=username))
    return render_template('dummy3.html')

@app.route("/motorcycle/<username>")
def mc(username):
    return render_template('moto.html', username=username)

@app.route("/airplane/<username>")
def airplane(username):
    return render_template('plane.html', username=username)

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

@app.route("/customs/<username>", methods=['GET','POST'])
def customs(username):
    user = users.query.filter_by(_un=username).first()

    if user:
        custom_lists = CustomList.query.filter_by(user_id=user._un).options(joinedload(CustomList.car_customs), joinedload(CustomList.moto_customs), joinedload(CustomList.plane_customs)).all()

        all_car_customs = []
        all_moto_customs = []
        all_plane_customs = []

        # Loop through each custom list and retrieve car customs and moto customs
        for custom_list in custom_lists:
            all_car_customs.extend(custom_list.car_customs)
            all_moto_customs.extend(custom_list.moto_customs)
            all_plane_customs.extend(custom_list.plane_customs)

        if 'clear' in request.form:
            # Delete car customs associated with the user
            for car_custom in all_car_customs:
                database.session.delete(car_custom)

            # Delete moto customs associated with the user
            for moto_custom in all_moto_customs:
                database.session.delete(moto_custom)

            # Delete plane customs associated with the user
            for plane_custom in all_plane_customs:
                database.session.delete(plane_custom)

            # Commit the changes to the database
            database.session.commit()
            flash("Customs cleared successfully", "success")
            return redirect(url_for('customs', username=user._un))
        elif 'return' in request.form:
            return redirect(url_for('home', username=username))

        return render_template('customs.html', car_customs=all_car_customs, moto_customs=all_moto_customs, plane_customs=all_plane_customs, username=user)
    else:
        flash("User not found", "error")
        return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        database.drop_all()
        database.create_all()
    app.run(debug=True)

