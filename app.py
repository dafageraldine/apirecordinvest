from flask import Flask,request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)
###dev
cred = credentials.Certificate('E:/Programming/apirecordinvest/recordinvest.json')
####server
# cred = credentials.Certificate('tokotelur.json')
firebase_admin.initialize_app(cred)
dbq = firestore.client()
tblproduct = dbq.collection('investment product')
tblrecord = dbq.collection('investment record')
tblsaldo = dbq.collection('investment saldo')
tbltype = dbq.collection('investment type')

@app.route('/gettype')
def gettype():
    data = tbltype.get()
    djson = []
    for i in range(len(data)):
        type = data[i].to_dict()['type']
        djson.append({"type" : type})
    return {"data":djson}

@app.route('/getproduct')
def getproduct():
    data = tblproduct.get()
    djson = []
    for i in range(len(data)):
        name = data[i].to_dict()['name']
        djson.append({"name" : name})
    return {"data":djson}

@app.route('/getsaldo')
def getsaldo():
    data = tblsaldo.get()
    djson = []
    for i in range(len(data)):
        date = data[i].to_dict()['date']
        saldo = data[i].to_dict()['saldo']
        djson.append({"date" : date, "saldo" : saldo})
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