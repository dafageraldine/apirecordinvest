from flask import Flask,render_template,request,flash,redirect,url_for,Response,current_app
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS
from datetime import datetime, timedelta
from redis import Redis
# from redislite import Redis
import pandas as pd
import json, smtplib

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)
# redis_server = Redis('/tmp/redis.db')
redis_server = Redis()

# https://apirecordinvest.herokuapp.com/
###dev
cred = credentials.Certificate('D:/Programming/apirecordinvest/recordinvest.json')
####server
# cred = credentials.Certificate('recordinvest.json')
# cred = credentials.Certificate('/home/dafageraldine/mysite/recordinvest.json')
firebase_admin.initialize_app(cred)
dbq = firestore.client()
tblproduct = dbq.collection('investment product')
tblrecord = dbq.collection('investment record')
tbltype = dbq.collection('investment type')
tbluser = dbq.collection('loginuser')

@app.route('/',methods=["GET","POST"])
def index():
    if request.method == 'POST':
        mails = request.form['email']
        from_ = request.form['name']
        msg = request.form['message']
        fromredis = redis_server.get(mails)
        if(fromredis):
            flash("mail server busy, try again later or whatsapp me instead !","warn")
            return redirect(url_for('index')+'#contact')
        else:
            if mails != '' and from_  != '' and msg != '':
                sender = "mybotmailer2023@gmail.com"
                rec = ["dafageraldine16@gmail.com",mails]
                pwd = "movsydghkpnxqiad"
                msg_embed = """From: <%s>
To: <%s>
Subject: Sended From Portfolio Web

<%s>
Pesan ini dikirim melalui smtplib dan diterima oleh modul SMTP Server Python.

""" %(from_,str(rec[0])+','+str(rec[1]),'Dari '+ str(from_) + ' untuk dafa geraldine, ' + str(msg))
                s = smtplib.SMTP('smtp.gmail.com',587)
                try:
                    s.starttls()
                    s.login(sender,pwd)
                    s.sendmail(sender,rec,msg_embed)
                    s.quit()
                    redis_server.set(mails,mails)
                    redis_server.expire(mails,7200)
                    flash("an email has been sent, check your mail box !","success")
                    return redirect(url_for('index')+'#contact')
                except:
                    try:
                        s.login(sender,pwd)
                        s.sendmail(sender,rec,msg_embed)
                        s.quit()
                        redis_server.set(mails,mails)
                        redis_server.expire(mails,7200)
                        flash("an email has been sent, check your mail box !","success")
                        return redirect(url_for('index')+'#contact')
                    except:
                        flash("error send email, please try again later or whatsapp instead !","danger")
                        return redirect(url_for('index')+'#contact')

    return render_template("index.html")

@app.route('/pomimonitoring')
def pomimonitoring():
    return render_template("pomimonitoring.html")

@app.route('/hydroponic')
def hydroponic():
    return render_template("hydroponic.html")

@app.route('/ansory')
def ansory():
    return render_template("ansory.html")

@app.route('/masuyaonline')
def masuyaonline():
    return render_template("masuyaonline.html")

@app.route('/masuyasalesapp')
def masuyasalesapp():
    return render_template("masuyasalesapp.html")

@app.route('/dynamicandstaticobjectdetection')
def dynamicandstaticobjectdetection():
    return render_template("dynamicandstatic.html")

@app.route('/masuyadesktop')
def masuyadesktop():
    return render_template("masuyadesktop.html")