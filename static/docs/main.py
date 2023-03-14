from flask import Flask, render_template, redirect, request, url_for, session, flash, jsonify
from flask_datepicker import datepicker
from datetime import datetime
import pymysql

app = Flask(__name__, template_folder='templates')
app.secret_key = "super secret key"

# ========================= DATABASE CONNECTING ========================================
con = pymysql.connect(host="localhost", user="root", password="", database="vaithigam")
cur = con.cursor()


# ========================= MAIN PAGE ========================================
@app.route('/')
def first():
    return render_template("login.html")


# ========================= EVENT INSERT PAGE ========================================
@app.route('/eveins')
def eveins():
    return render_template('events.html')


@app.route('/eins', methods=['GET', 'POST'])
def eins():
    dt = request.form['tktdate']
    tm = request.form['tkttime']
    f_dt = datetime.strptime(dt, '%Y-%m-%d').date()
    f_tm = datetime.strptime(tm, '%I:%M %p').time()
    if request.method == 'POST':
        tktdate = dt
        tkttime = tm
        tktname = request.form['tktname']
        tktloc = request.form['tktloc']
        f_cli_id = session['clientID']
        stat = "B"
    cur.execute("INSERT INTO ems (tktdate,tkttime,tktname,tktloc,f_cli_id,stat)values(%s, %s, %s, %s, %s, %s)",
                (f_dt, f_tm, tktname, tktloc, f_cli_id, stat))
    con.commit()
    con.close()
    return render_template("login.html")


# ========================= LOGIN PAGE ========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['mobno'] = request.form['mobno']
        session['password'] = request.form['password']
        session.permanent = True
        cur.execute('select * from clientmast where mobno=%s and password=%s', (session['mobno'], session['password']))
        row = cur.fetchone()
        if row:
            session['loggedin'] = True
            session['mobno'] = row[2]
            session['fname'] = row[3]
            session['lname'] = row[4]
            session['clientID'] = row[0]
            session['utype'] = row[1]
            session['sakai'] = row[8]
            session['gothram'] = row[9]
            if session['utype'] == 'admin':
                flash('Logged-IN Successfully', 'success')
                return redirect(url_for('admin'))
            elif session['utype'] == 'Client':
                flash('Logged-IN Successfully', 'success')
                return redirect(url_for('cli'))
            elif session['utype'] == 'Vaithigar':
                flash('Logged-IN Successfully', 'success')
                return redirect(url_for('vai'))
        error = flash('Invalid User or Password')
    return render_template('login.html', error=error)

@app.route('/admin')
def admin():
    return render_template('adashboard.html')

@app.route('/cli', methods=['POST', 'GET'])
def cli():
    CID = session['clientID']
    with con.cursor() as cursor:
        cur = con.cursor()
        cur.execute("SELECT COUNT(stat) from ems WHERE f_cli_id = %s AND stat='B'", (CID,))
        count = cur.fetchone()[0]
        cur.execute(
            "SELECT tktID, DATE_FORMAT(tktdate ,'%%d-%%m-%%Y'), DATE_FORMAT(tkttime, '%%H:%%i %%p'), tktname, tktloc FROM ems WHERE f_cli_id = %s AND stat='B'",
            (CID,))
        booked = cur.fetchall()
        con.commit()
        con.close
        return render_template('cdashboard.html', count=count, booked=booked)

@app.route('/vai')
def vai():
    return render_template("vdashboard.html")


# ========================= CLIENT RECORD DISPLAY  ========================================
# @app.route('/disprec', methods=['GET', 'POST'])
# def disprec():
#     CID = session['clientID']
#     cur.execute(
#         "SELECT tktID, DATE_FORMAT(tktdate ,'%%d-%%m-%%Y'), DATE_FORMAT(tkttime, '%%H:%%i %%p'), tktname, tktloc FROM ems WHERE f_cli_id = %s AND stat='B'", (CID,))
#     result = cur.fetchall()
#     print(result)
#     return render_template('cdashboard.html', result=result)


# ========================= CLIENT INSERT PAGE ========================================
@app.route('/uins', methods=['GET', 'POST'])
def uins():
    dt = request.form['dob']
    f_dt = datetime.strptime(dt, '%Y-%m-%d').date()
    if request.method == 'POST':
        utype = request.form['utype']
        mobno = request.form.get("mobno")
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['pwd']
        dob = dt
        contno = request.form['contno']
        sakai = request.form['sakai']
        gothram = request.form['gothram']
        birthstar = request.form['birthstar']
        add1 = request.form['add1']
        city = request.form['city']
        pincode = request.form['pincode']
        cur.execute(
            "INSERT IGNORE INTO clientmast (utype,mobno,fname,lname,password,dob,contno,sakai,gothram,birthstar,add1,city,pincode)values(% s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s)",
            (utype, mobno, fname, lname, password, f_dt, contno, sakai, gothram, birthstar, add1, city, pincode))
    con.commit()
    con.close()
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


# ========================= LOGOUT PAGE ========================================
@app.route("/logout")
def logout():
    session["mobno"] = None
    return redirect("/")


# ========================= DEBUGGING ========================================
if __name__ == "__main__":
    app.run(debug=True)
