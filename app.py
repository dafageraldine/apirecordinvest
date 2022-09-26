from flask import Flask,request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# https://apirecordinvest.herokuapp.com/
###dev
# cred = credentials.Certificate('E:/Programming/apirecordinvest/recordinvest.json')
####server
cred = credentials.Certificate('recordinvest.json')
firebase_admin.initialize_app(cred)
dbq = firestore.client()
tblproduct = dbq.collection('investment product')
tblrecord = dbq.collection('investment record')
tblsaldo = dbq.collection('investment saldo')
tbltype = dbq.collection('investment type')

@app.route('/')
def index():
    return ("welcome to record invest webserver")

@app.route('/gettype')
def gettype():
    # data = tbltype.order_by(u'type', direction=firestore.Query.DESCENDING).get().limit(1)
    data = tbltype.order_by(u'type', direction=firestore.Query.ASCENDING).get()
    djson = []
    for i in range(len(data)):
        type = data[i].to_dict()['type']
        djson.append({"type" : type})
    return {"data":djson}

@app.route('/getproduct')
def getproduct():
    data = tblproduct.order_by(u'name', direction=firestore.Query.ASCENDING).get()
    djson = []
    for i in range(len(data)):
        name = data[i].to_dict()['name']
        djson.append({"name" : name})
    return {"data":djson}

@app.route('/getsaldo')
def getsaldo():
    dates = tblrecord.order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()
    # data = tblrecord.where(u'date',u'==',).get()
    # djson = []
    # for i in range(len(data)):
    #     date = data[i].to_dict()['date']
    #     saldo = data[i].to_dict()['saldo']
    #     djson.append({"date" : date, "saldo" : saldo})
    djson = []
    for i in range(len(dates)):
        date = dates[i].to_dict()['date']
        djson.append({"date" : date})
    return {"data":djson}

@app.route('/getrecord')
def getrecord():
    data = tblrecord.get()
    djson = []
    for i in range(len(data)):
        date = data[i].to_dict()['date']
        value = data[i].to_dict()['value']
        type = data[i].to_dict()['type']
        product = data[i].to_dict()['product']
        djson.append({"date" : date, "value" : value, "type" : type, "product" : product})
    return {"data":djson}

@app.route('/inserttypenproduct',methods=["POST"])
def inserttypenproduct():
    data = request.form.to_dict(flat=False)
    if(data['type'][0] != ""):
        tbltype.add({"type":data['type'][0] })
    
    if(data['name'][0] != ""):
        tblproduct.add({"name" :data['name'][0] })
    
    return { "message" : "data has been added"}

@app.route('/insertrecord',methods=["POST"])
def insertrecord():
    data = request.form.to_dict(flat=False)
    # now = datetime.datetime.now(datetime.timezone.utc)
    tblrecord.add({"type":data['type'][0],"product":data['product'][0], "value":float(data['value'][0]),"date":datetime.utcnow().strftime("%Y-%m-%d")})
    return { "message" : "data has been added"}

@app.route('/insertsaldo',methods=["POST"])
def insertsaldo():
    data = request.form.to_dict(flat=False)
    now = datetime.datetime.now(datetime.timezone.utc)
    tblsaldo.add({ "saldo":float(data['saldo'][0]),"date":now})
    return { "message" : "data has been added"}

# @app.route('/insertdata',methods=["POST"])
# def insertdata():
#     jam = 0
#     data = request.form.to_dict(flat=False)
#     now = datetime.datetime.now(datetime.timezone.utc)
#     if ((int(now.hour)+7) > 24):
#         jam = int(now.hour) + 7 - 24
#     else:
#         jam = int(now.hour) + 7
#     tgl = str(now.year) + '-' + str(now.month) + '-' + str(now.day) + ' ' + str(jam) + ':' + str(now.minute)
#     doc_ref.add({"tanggal":tgl , "harga" : data['harga'][0] , "qty":data['qty'][0], "total" : data['total'][0] })
#     return {"tanggal":tgl , "harga" : data['harga'][0] , "qty":data['qty'][0], "total" : data['total'][0] }

if __name__ == "__main__":
    app.run(debug=True,)