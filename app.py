from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_datepicker import datepicker
from datetime import datetime
import pymysql

app = Flask(__name__, template_folder='templates')
app.secret_key = "super secret key"

# ========================= DATABASE CONNECTING ========================================
con = pymysql.connect(host="localhost", user="root",
                      password="", database="vaithigam")
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
        dt1 = f_dt
        tt1 = f_tm
        tktname = request.form['tktname']
        tktloc = request.form['tktloc']
        f_cli_id = session['clientID']
        stat = "B"
    cur.execute("INSERT INTO ems (tktdate,tkttime,tktname,tktloc,f_cli_id,stat)values(%s, %s, %s, %s, %s, %s)",
                (dt1, tt1, tktname, tktloc, f_cli_id, stat))
    con.commit()
    cur.close()
    return redirect("/")
# ========================= LOGIN PAGE ========================================


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['mobno'] = request.form['mobno']
        session['password'] = request.form['password']
        session.permanent = True
        cur=con.cursor()
        cur.execute('select * from clientmast where mobno=%s and password=%s',
                    (session['mobno'], session['password']))
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
                return redirect(url_for('admin'))
            elif session['utype'] == 'Client':
                return redirect(url_for('cli', success=True))
            elif session['utype'] == 'Vaithigar':
                return redirect(url_for('vai'))
    return render_template('login.html')


@app.route('/admin')
def admin():
    return render_template('adashboard.html')


@app.route('/cli', methods=['POST', 'GET'])
def cli():
    CID = session['clientID']
    with con.cursor():
        cur = con.cursor()
        cur.execute(
            "SELECT count(stat) from ems WHERE f_cli_id=%s AND stat='B'", (CID,))
        count = cur.fetchone()[0]
        cur.execute("SELECT * FROM ems WHERE f_cli_id=%s AND stat='B'", (CID,))
        # cur.execute("SELECT tktID, DATE_FORMAT(tktdate ,'%%d-%%b-%%Y'), DATE_FORMAT(tkttime, '%%H:%%i %%p'), tktname, tktloc FROM ems WHERE f_cli_id = %s AND stat='B'",(CID,))
        booked = cur.fetchall()
        cur.execute(
            "SELECT count(stat) from ems WHERE f_cli_id=%s AND stat='A'", (CID,))
        count1 = cur.fetchone()[0]
        cur.execute(
            "SELECT e.*, a.fname,a.lname AS fname,lname FROM ems e INNER JOIN clientmast a ON e.v_cli_id = a.clientID WHERE e.f_cli_id = %s AND e.stat = 'A'", (CID,))
        accept = cur.fetchall()
        cur.execute(
            "SELECT count(stat) from ems WHERE f_cli_id=%s AND stat='C'", (CID,))
        count2 = cur.fetchone()[0]
        cur.execute(
            "SELECT e.*, a.fname,a.lname AS fname,lname FROM ems e INNER JOIN clientmast a ON e.v_cli_id = a.clientID WHERE e.f_cli_id = %s AND e.stat = 'C'", (CID,))
        complete = cur.fetchall()
        cur.execute(
            "SELECT count(stat) from ems WHERE f_cli_id=%s AND stat='X'", (CID,))
        count3 = cur.fetchone()[0]
        cur.execute(
            "SELECT e.*, a.fname,a.lname AS fname,lname FROM ems e INNER JOIN clientmast a ON e.v_cli_id = a.clientID WHERE e.f_cli_id = %s AND e.stat = 'X'", (CID,))
        cancel = cur.fetchall()
        update = ''
        if request.method == 'POST':
            tktID = request.form['tktID']
            v_cli_id = session['clientID']
            cur.execute("SELECT stat FROM ems WHERE tktID=%s", (tktID,))
            row = cur.fetchone()
            stat = ''
            if row is not None and row[0] == 'B':
                stat = "X"
            elif row is not None and row[0] == 'A':
                stat = "X"
            cur.execute(
                """UPDATE ems SET v_cli_id=%s, stat=%s WHERE tktID=%s""", (v_cli_id, stat, tktID,))
            update = True
        con.commit()
        con.close
        return render_template('cdashboard.html', count=count, count1=count1, count2=count2, count3=count3, update=update, booked=booked, accept=accept, complete=complete, cancel=cancel)


@app.route('/vai', methods=['POST', 'GET'])
def vai():
    CID = session['clientID']
    update = ""
    with con.cursor():
        cur = con.cursor()
        cur.execute("SELECT count(*) from ems WHERE stat='B'")
        count = cur.fetchone()[0]
        cur.execute("SELECT * FROM ems WHERE stat='B'")
        # cur.execute("SELECT tktID, DATE_FORMAT(tktdate ,'%%d-%%b-%%Y'), DATE_FORMAT(tkttime, '%%H:%%i %%p'), tktname, tktloc FROM ems WHERE (stat=%s)='B'",(CID,))
        booked = cur.fetchall()
        cur.execute(
            "SELECT count(stat) from ems WHERE v_cli_id=%s AND stat='A'", (CID,))
        count1 = cur.fetchone()[0]
        cur.execute(
            "SELECT e.*, a.fname,a.lname AS fname,lname FROM ems e INNER JOIN clientmast a ON e.f_cli_id = a.clientID WHERE e.v_cli_id = %s AND e.stat = 'A'", (CID,))
        accept = cur.fetchall()
        cur.execute(
            "SELECT count(stat) from ems WHERE v_cli_id=%s AND stat='C'", (CID,))
        count2 = cur.fetchone()[0]
        cur.execute(
            "SELECT e.*, a.fname,a.lname AS fname,lname FROM ems e INNER JOIN clientmast a ON e.f_cli_id = a.clientID WHERE e.v_cli_id = %s AND e.stat = 'C'", (CID,))
        complete = cur.fetchall()
        cur.execute(
            "SELECT count(stat) from ems WHERE stat='X'")
        count3 = cur.fetchone()[0]
        cur.execute(
            "SELECT e.*, a.fname,a.lname AS fname,lname FROM ems e INNER JOIN clientmast a ON e.f_cli_id = a.clientID WHERE e.stat = 'X'")
        cancel = cur.fetchall()
        if request.method == 'POST':
            tktID = request.form['tktID']
            v_cli_id = session['clientID']
            cur.execute("SELECT stat FROM ems WHERE tktID=%s", (tktID,))
            row = cur.fetchone()
            stat = ''
            if row is not None and row[0] == 'B':
                stat = "A"
            elif row is not None and row[0] == 'A':
                stat = "C"
            cur.execute(
                """UPDATE ems SET v_cli_id=%s, stat=%s WHERE tktID=%s""", (v_cli_id, stat, tktID,))
            update = True
            con.commit()
        return render_template("vdashboard.html", count=count, count1=count1, count2=count2, count3=count3, booked=booked, update=update, accept=accept, complete=complete, cancel=cancel)

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
        dob1 = f_dt
        contno = request.form['contno']
        sakai = request.form['sakai']
        gothram = request.form['gothram']
        birthstar = request.form['birthstar']
        add1 = request.form['add1']
        city = request.form['city']
        pincode = request.form['pincode']
        cur.execute(
            "INSERT IGNORE INTO clientmast (utype,mobno,fname,lname,password,dob,contno,sakai,gothram,birthstar,add1,city,pincode)values(% s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s)",
            (utype, mobno, fname, lname, password, dob1, contno, sakai, gothram, birthstar, add1, city, pincode))
    con.commit()
    cur.close()
    return redirect("/")
# =========================  NEW USER SIGNUP PAGE ========================================
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
