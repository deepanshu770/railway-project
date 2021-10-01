# Importing Necessary Library
import os 
from flask import Flask, render_template,jsonify, request, redirect, url_for, session, send_file, make_response
import mysql.connector as sql
from mysql.connector import cursor
import datetime
from werkzeug.wrappers import response

app = Flask(__name__)
app.secret_key = "hviuher89gee4387y7"

# Creating Classes with the help of multiple inhertitance
#
#              Train                 Passenger
#                 \                  /
#                  \                /
#                   \              /
#                        Ticket


class Train:

    def __init__(self, name, number, fare, total_seats, avai_seats, fr, to, departure, arrival):
        self.train_name = name
        self.train_number = number
        self.train_fare = fare
        self.total_seats = total_seats
        self.avai_seats = avai_seats
        self.train_from = fr
        self.train_to = to
        self.dep_t = departure
        self.arr_t = arrival

    def __str__(self):
        return f"Train object (name={self.train_name},number={self.train_number},fare={self.train_fare},total_seats={self.total_seats},avai_seats={self.avai_seats},train_from={self.train_from},train_to={self.train_to})"

    def bookTicket(self):
        if self.total_seats > 0:
            self.avai_seats = self.avai_seats-1
            mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                               passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
            cursor = mydb.cursor()
            cursor.execute(
                f"update train_info set avai_seats={self.avai_seats} where number={self.train_number}")
            mydb.commit()

    @property
    def trainInfo(self):
        return f'''name={self.train_name}
number={self.train_number}
fare={self.train_fare}
total_seats={self.total_seats}
avai_seats={self.avai_seats}'''


class Passenger:
    def __init__(self, name, age, gender):
        self.pass_name = name
        self.pass_age = age
        self.pass_gender = gender

    def __str__(self) -> str:
        return f"Passenger object (name={self.pass_name},age={self.pass_age},gender={self.pass_gender})"


class Ticket(Train, Passenger):

    def __init__(self, T, P):
        n = 0
        Train.__init__(self, T.train_name, T.train_number, T.train_fare, T.total_seats, T.avai_seats, T.train_from,
                       T.train_to,
                       T.dep_t,
                       T.arr_t)
        Passenger.__init__(self, P.pass_name, P.pass_age, P.pass_gender)

    def bookTicket(self, num, nooftick):
        if self.avai_seats == 0:

            mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                               passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
            cursor = mydb.cursor()
            cursor.execute(
                f"select pnr from ticket_info order by pnr desc limit 1")
            result = cursor.fetchone()
            self.pnr = (result[0]+1)-num

            self.status = "Waiting"
            self.seat_no = 000000
        else:
            mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                               passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
            cursor = mydb.cursor()
            cursor.execute(
                f"select pnr from ticket_info order by pnr desc limit 1")
            result = cursor.fetchone()
            self.pnr = (result[0]+1)-num

            total = set(range(1, self.total_seats+1))
            mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                               passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
            cursor = mydb.cursor()
            cursor.execute(
                f"Select seat_no from ticket_info where train ='{self.train_number}'")
            result = cursor.fetchall()
            booked_seat_no = [item for i in result for item in i]
            avai_seat_no = list(total-set(booked_seat_no))

            self.status = "Confirmed"
            self.seat_no = avai_seat_no[0]
            super().bookTicket()
        mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                           passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
        cursor = mydb.cursor()
        cursor.execute(
            f"insert into ticket_info (name,gender,age,train,seat_no,status,pnr) values('{self.pass_name}','{self.pass_gender}','{self.pass_age}','{self.train_number}','{self.seat_no}','{self.status}','{self.pnr}')")
        mydb.commit()


@app.route("/")
def entry():
    return render_template('entry.html')


@app.route("/", methods=['GET', 'POST'])
def logging():
    if request.method == "POST":
        hemail = request.form['hemail']
        hpasswd = request.form['hpasswd']
        print(hemail)
        print(hpasswd)
        mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                           passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
        cursor = mydb.cursor()
        cursor.execute(f"SELECT passwd from userdata WHERE email = '{hemail}'")
        passwd = cursor.fetchone()
        if hpasswd == passwd[0]:
            session["user"] = hemail
            return redirect(url_for("home"))
        else:
            return render_template('entry.html')


@app.route("/home")
def home():

    if "user" in session:
        user = session["user"]
        return render_template("home.html", user=user)
    else:
        return redirect(url_for("logging"))


@app.route("/home", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session.pop("user")
        return redirect(url_for("entry"))


@app.route("/registration")
def register():
    return render_template("registration1.html")


@app.route("/registration", methods=["GET", "POST"])
def registeration():
    if request.method == "POST":
        name = request.form["rname"]
        email = request.form["remail"]
        country = request.form["cont"]
        d = request.form["dob"]
        gender = request.form["gender"]
        phno = request.form["phno"]
        passwd = request.form["passwd"]
        con_pssswd = request.form["con_passwd"]
        mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                           passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
        cursor = mydb.cursor()
        cursor.execute(f"select * from userdata where email='{email}'")
        result = cursor.fetchall()
        print(country)
        print(gender)

        if len(result) == 0:

            session["user"] = email
            dob = datetime.datetime.strptime(d, "%Y-%m-%d")
            if phno == "":
                mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                                   passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
                cursor = mydb.cursor()
                cursor.execute("insert into userdata (name,email,country,dob,gender,passwd,con_passwd) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(
                    name, email, country, dob, gender, passwd, con_pssswd))
                mydb.commit()
                return redirect(url_for("home"))
            else:
                mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                                   passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
                cursor = mydb.cursor()
                cursor.execute("insert into userdata (name,email,country,dob,gender,passwd,con_passwd,phno) VALUES ('{}','{}','{}','{}','{}','{}','{}',{})".format(
                    name, email, country, dob, gender, passwd, con_pssswd, int(phno)))
                mydb.commit()
                return redirect(url_for("home"))
        else:
            dob = datetime.datetime.strptime(d, "%Y-%m-%d")

            return render_template("registration2.html", result=result, name=name, country=country, gender=gender, phno=phno, passwd=passwd, dob=dob, con_pssswd=con_pssswd)


@app.route("/booking")
def booking():
    if "user" in session:
        mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                           passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
        cursor = mydb.cursor()
        cursor.execute("select start,end from train_info")
        result = cursor.fetchall()
        lis = [item for i in result for item in i]
        stations = []
        for i in lis:
            if i not in stations:
                stations.append(i)

        return render_template("bookticket.html", stations=stations)
    else:
        return redirect(url_for("entry"))


@app.route("/booking", methods=["GET", "POST"])
def traintable():
    if "user" in session:
        if request.method == "POST":
            fr = request.form["from"]
            to = request.form["to"]
            dt = request.form["date"]
            mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                               passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
            cursor = mydb.cursor()
            cursor.execute(
                f"select name,number,total_seats,avai_seats,fare,departure_dt,arrival_dt from train_info where start='{fr}' and end='{to}'")
            result = cursor.fetchall()
            l_res=len(result)
            print(dt)
            global ob
            ob = []
            today_date = datetime.datetime.now()
            for i in result:
                if i[5]<today_date:
                    result.remove(i)
            if dt != "":
                date = datetime.datetime.strptime(dt, "%Y-%m-%d")
                print(result[0][5].date())
                for i in range(len(result)):
                    if result[i][5].date() != date.date():
                        result.remove(result[i])
            for i in range(len(result)):
                name = result[i][0]
                num = result[i][1]
                total = result[i][2]
                remain = result[i][3]
                fare = result[i][4]
                d_t = result[i][5]
                a_t = result[i][6]
                tx = Train(name, num, fare, total, remain, fr, to, d_t, a_t)
                ob.append(tx)
            for i in range(len(ob)):
                print(ob[i])
            return render_template("traintable.html", ob=ob, fr=fr, to=to)


@app.route("/booking/<name>/<int:number>/<int:fare>/<int:total_seats>/<int:avai_seats>/<fr>/<to>/<departur>/<arriva>", methods=["GET"])
def getnotickets(name, number, fare, total_seats, avai_seats, fr, to, departur, arriva):
    departure = datetime.datetime.strptime(departur, "%Y-%m-%d %H:%M:%S")
    arrival = datetime.datetime.strptime(arriva, "%Y-%m-%d %H:%M:%S")
    booked_train = Train(name, number, fare, total_seats,
                         avai_seats, fr, to, departure, arrival)
    return render_template("traininfo.html", obj=booked_train)


@app.route("/booking/<name>/<int:number>/<int:fare>/<int:total_seats>/<int:avai_seats>/<fr>/<to>/<departur>/<arriva>/<int:no>", methods=["GET"])
def getdetails(name, number, fare, total_seats, avai_seats, fr, to, departur, arriva, no):
    print(departur)
    print(arriva)
    departure = datetime.datetime.strptime(departur, "%Y-%m-%d %H:%M:%S")
    arrival = datetime.datetime.strptime(arriva, "%Y-%m-%d %H:%M:%S")
    train = Train(name, number, fare, total_seats,
                  avai_seats, fr, to, departure, arrival)
    noft = no
    session["num"] = 0
    if noft == 1:
        return render_template("detail1.html", obj=train, noft=noft)
    else:

        return render_template("detail2.html", obj=train, noft=noft, no=noft-(noft-1))


@app.route("/bookingTicket/<name>/<int:number>/<int:fare>/<int:total_seats>/<int:avai_seats>/<fr>/<to>/<departur>/<arriva>/<int:no>", methods=["GET", "POST"])
def bookticketfor1(name, number, fare, total_seats, avai_seats, fr, to, departur, arriva, no,):
    departure = datetime.datetime.strptime(departur, "%Y-%m-%d %H:%M:%S")
    arrival = datetime.datetime.strptime(arriva, "%Y-%m-%d %H:%M:%S")
    booked_train = Train(name, number, fare, total_seats,
                         avai_seats, fr, to, departure, arrival)
    noft = no
    print(noft)
    num = session.get("num")
    if request.method == "POST":
        if noft == 1:
            print("past1")
            pas_name = request.form['fname']+" "+request.form['lname']
            pas_gen = request.form['exampleRadios']
            pas_age = request.form['pas_age']
            Pass = Passenger(pas_name, pas_age, pas_gen)
            booked_t = Ticket(booked_train, Pass)
            booked_t.bookTicket(num, noft)

            print(booked_t)
            print("booked")

            return render_template("ticket1.html", tic=booked_t)

        if noft > 1:
            print("past")
            pas_name = request.form['fname']+" "+request.form['lname']
            pas_gen = request.form['exampleRadios']
            pas_age = request.form['pas_age']
            Pass = Passenger(pas_name, pas_age, pas_gen)
            print(Pass)

            Tick2 = Ticket(booked_train, Pass)
            Tick2.bookTicket(num, noft)

            num += 1
            session["num"] = num
            print(noft)
            if num == noft:
                mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                                   passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
                cursor = mydb.cursor()
                cursor.execute(
                    f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{Tick2.pnr}' ")
                result = cursor.fetchall()

                return render_template("ticket2.html", ticket=result)
            else:
                return render_template("detail2.html", obj=booked_train, no=num+1, noft=noft)


@app.route("/ticket/<int:pnr>", methods=["GET"])
def showticket(pnr):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(
        f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{pnr}' ")
    result = cursor.fetchall()
    return render_template("ticket2.html", ticket=result)
# Ticket
# This feature is not working in Heroku Only. It is wokring on Local Host Properly


@app.route("/ticketpdf/<int:pnr>")
def pdfticket(pnr):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(
        f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{pnr}' ")
    ticket = cursor.fetchall()
    try:
        return render_template("ticketpdf.html",ticket=ticket)
    except:
        return render_template("maintain.html")



@app.route("/status", methods=["GET", "POST"])
def checkstatus():
    return render_template("getpnrstatus.html")


@app.route("/status/<int:pnr>", methods=["GET"])
def status(pnr):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(
        f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{pnr}' ")
    result = cursor.fetchall()
    print(result)
    l = len(result)
    if l > 0:
        dep_delta = result[0][14]-datetime.datetime.now()
        arr_delta = result[0][15]-datetime.datetime.now()
        if dep_delta.days > 0:
            gap = f"{dep_delta.days} Days to go"
        elif dep_delta.days <= 0 and arr_delta.days > 0:
            gap = "Running OnTime"
        elif arr_delta.days <= 0:
            gap = "Arrived"
        return render_template("status.html", result=result, gap=gap, l=l)
    else:
        return render_template("status.html", l=l)


@app.route("/cancel", methods=["GET", "POST"])
def getpnr():
    return render_template("getpnrcancel.html")


@app.route("/cancel/<int:pnr>", methods=["GET"])
def select_cancel(pnr):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(
        f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{pnr}' ")
    result = cursor.fetchall()
    print(result)
    l = len(result)
    return render_template("cancel.html", result=result, l=l)


@app.route("/cancel/<int:pnr>/<int:n>", methods=["GET"])
def cancel(pnr, n):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(
        f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{pnr}' ")
    result = cursor.fetchall()
    l = len(result)
    if n == 0:
        mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                           passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
        cursor = mydb.cursor()
        cursor.execute(f"delete from ticket_info where pnr ='{pnr}'")
        cursor.execute(
            f"update train_info set avai_seats ='{result[0][10] + l}' where number='{result[0][8]}'")
        mydb.commit()
        return render_template("cancel1.html")
    if n != 0:
        mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                           passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
        cursor = mydb.cursor()
        cursor.execute(
            f"delete from ticket_info where pnr ='{pnr}' and age='{result[n-1][2]}'")
        cursor.execute(
            f"update train_info set avai_seats ='{result[n-1][10] + 1}' where number='{result[n-1][8]}'")
        mydb.commit()
        result.pop(n-1)
        ls = len(result)
        return render_template("cancel.html", result=result, l=ls)

# REST APIs 

# From station1 to station2 | endpoint ---> /api/station1/station2
@app.route("/api/<start>/<end>", methods=["GET"])
def api_start_end(start, end):
    s = start.title()
    e = end.title()
    res = []
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(f"select name,number,timetaken,avai_seats,fare,departure_dt,arrival_dt from train_info where start='{s}' and end='{e}'")
    result = cursor.fetchall()
    l_result = len(result)
    for i in range(l_result):
        tt = result[i][2].split(":")
        js_ob ={
            'train_name' : result[i][0],
            "time_taken":f"{tt[0]} hour ,{tt[1]} mins",
            'train_number' : result[i][1],
            'availble_seats' : result[i][3],
            'fare' : result[i][4],
            'departure_date' : result[i][5].strftime("%Y-%m-%d"),
            'departure_time' : result[i][5].strftime("%H:%M:%S"),
            'arrival_date' : result[i][6].strftime("%Y-%m-%d"),
            'arrival_time' : result[i][6].strftime("%H:%M:%S")
        }
        res.append(js_ob)

    return jsonify(res)

# for Passenger Details using pnr | endpoint --->/api/passenger/pnr
@app.route("/api/passenger/<int:pnr>", methods=["GET"])
def api_passenger(pnr):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(
        f"select * from ticket_info join train_info on ticket_info.train=train_info.number where pnr='{pnr}' ")
    result = cursor.fetchall()
    res=[]
    for ticket in result:
        js_ob={
            "train_Name" : ticket[7],
            'train_number':ticket[8],
            'departure_date':ticket[14].strftime("%b %d, %Y"),
            'departure_time':ticket[15].strftime("%H : %M"),
            'arrival_date':ticket[14].strftime("%b %d, %Y"),
            'arrival_time':ticket[15].strftime("%H : %M"),
            'pass_name':ticket[0],
            'pass_age':ticket[3],
            'pass_gender':ticket[1],
            'pnr':ticket[6],
            'seat_no':ticket[2],
            'status':ticket[5]
        }
        res.append(js_ob)
    return jsonify(res)




# for a train_number of a specific Train | endpoint ---> /api/train_number
@app.route("/api/<int:number>", methods=["GET"])
def api_number(number):
    mydb = sql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                       passwd=os.environ["DB_PASS"], database=os.environ["DB_DATABASE"])
    cursor = mydb.cursor()
    cursor.execute(f"select name,start,timetaken,avai_seats,fare,departure_dt,arrival_dt,end from train_info where number='{number}'")
    result = cursor.fetchone() 
    tt = result[2].split(":")
    js_ob ={
        'train_name' : result[0],
        "time_taken":f"{tt[0]} hour ,{tt[1]} mins",
        'train_number' : number,
        'availble_seats' : result[3],
        'fare' : result[4],
        'departure_date' : result[5].strftime("%Y-%m-%d"),
        'departure_time' : result[5].strftime("%H:%M:%S"),
        'arrival_date' : result[6].strftime("%Y-%m-%d"),
        'arrival_time' : result[6].strftime("%H:%M:%S"),
        'start':result[1],
        'end':result[7]
    }


    return jsonify(js_ob)


if __name__ == "__main__":
    app.run()
