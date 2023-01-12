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
# cred = credentials.Certificate('recordinvest.json')
cred = credentials.Certificate('/home/dafageraldine/mysite/recordinvest.json')
firebase_admin.initialize_app(cred)
dbq = firestore.client()
tblproduct = dbq.collection('investment product')
tblrecord = dbq.collection('investment record')
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
    date = ""
    datebefore = ""
    for i in range(len(dates)):
        date = dates[i].to_dict()['date']
    data = tblrecord.where(u'date',u'==',date).get()
    databefore = tblrecord.where(u'date',u'<',date).order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()
    for i in range(len(databefore)):
        datebefore = databefore[i].to_dict()['date']
    databefore_ = tblrecord.where(u'date',u'==',datebefore).get()
    djson = []
    value = 0
    valuebefore = 0
    for i in range(len(databefore_)):
        valuebefore = valuebefore + databefore_[i].to_dict()['value']
    for i in range(len(data)):
        date = data[i].to_dict()['date']
        value = value + data[i].to_dict()['value']
        if(i == len(data)-1):
            djson.append({"date" : date, "saldo" : value, "saldobefore": valuebefore})
    return {"data":djson}

@app.route('/getrecord',methods=["POST"])
def getrecord():
    post = request.form.to_dict(flat=False)

    # if(post['type'][0] != ""):

    # .order_by(u'date', direction=firestore.Query.ASCENDING)
    data = tblrecord.where(u'date',u'==',post['date'][0]).get()
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

if __name__ == "__main__":
    app.run(debug=True,)