from flask import Flask,render_template,request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS
from datetime import datetime
from redis import Redis
# from redislite import Redis
import json

app = Flask(__name__)
CORS(app)
# redis_server = Redis('/tmp/redis.db')
redis_server = Redis()

# https://apirecordinvest.herokuapp.com/
###dev
cred = credentials.Certificate('E:/Programming/apirecordinvest/recordinvest.json')
####server
# cred = credentials.Certificate('recordinvest.json')
# cred = credentials.Certificate('/home/dafageraldine/mysite/recordinvest.json')
firebase_admin.initialize_app(cred)
dbq = firestore.client()
tblproduct = dbq.collection('investment product')
tblrecord = dbq.collection('investment record')
tbltype = dbq.collection('investment type')
tbluser = dbq.collection('loginuser')

@app.route('/')
def index():
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

@app.route('/gettype',methods=["POST"])
def gettype():
    post = request.form.to_dict(flat=False)
    ids = post["id"][0]
    key_data = "type" + ids
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        data = tbltype.where(u'id',u'==',post["id"][0]).get()
        djson = []
        for i in range(len(data)):
            type = data[i].to_dict()['type']
            djson.append({"type" : type})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

@app.route('/getproduct',methods=["POST"])
def getproduct():
    post = request.form.to_dict(flat=False)
    ids = post["id"][0]
    key_data = "product" + ids
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        data = tblproduct.where(u'id',u'==',post["id"][0]).get()
        djson = []
        for i in range(len(data)):
            name = data[i].to_dict()['name']
            djson.append({"name" : name})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

@app.route('/getsaldo',methods=["POST"])
def getsaldo():
    post = request.form.to_dict(flat=False)
    ids = post["id"][0]
    key_data = "saldo" + ids
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        ## get lastest date
        dates = tblrecord.order_by(u'date', direction=firestore.Query.DESCENDING).get()
        date = ""
        datebefore = ""
        for i in range(len(dates)):
            if(post["id"][0] == dates[i].to_dict()['id'] ):
                date = dates[i].to_dict()['date']
                break

        ## get data before lattest date and getting latest data based on latest date
        data = tblrecord.where(u'date',u'==',date).get()
        databefore = tblrecord.where(u'date',u'<',date).order_by(u'date', direction=firestore.Query.DESCENDING).get()
        for i in range(len(databefore)):
            if(post["id"][0] == databefore[i].to_dict()['id'] ):
                datebefore = databefore[i].to_dict()['date']
                break

        databefore_ = tblrecord.where(u'date',u'==',datebefore).get()
        djson = []
        value = 0
        valuebefore = 0
        for i in range(len(databefore_)):
            if(post["id"][0] == databefore_[i].to_dict()['id']):
                valuebefore = valuebefore + databefore_[i].to_dict()['value']
        for i in range(len(data)):
            if(post["id"][0] == data[i].to_dict()['id']):
                date = data[i].to_dict()['date']
                value = value + data[i].to_dict()['value']
                if(i == len(data)-1):
                    djson.append({"date" : date, "saldo" : value, "saldobefore": valuebefore})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

@app.route('/getrecord',methods=["POST"])
def getrecord():
    post = request.form.to_dict(flat=False)

    # if(post['type'][0] != ""):

    # .order_by(u'date', direction=firestore.Query.ASCENDING)
    data = tblrecord.where(u'date',u'==',post['date'][0]).where(u'id',u'==',post["id"][0]).get()
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
        ids = data["id"][0]
        key_data = "type" + ids
        redis_server.delete(key_data)
        tbltype.add({"type":data['type'][0],"id":data["id"][0] })

    if(data['name'][0] != ""):
        ids = data["id"][0]
        key_data = "product" + ids
        redis_server.delete(key_data)
        tblproduct.add({"name" :data['name'][0],"id":data["id"][0] })

    return { "message" : "data has been added"}

@app.route('/insertrecord',methods=["POST"])
def insertrecord():
    data = request.form.to_dict(flat=False)
    ids = data["id"][0]
    key_data = "saldo" + ids
    key_asset = "asset" + ids
    redis_server.delete(key_data)
    redis_server.delete(key_asset)
    # now = datetime.datetime.now(datetime.timezone.utc)
    tblrecord.add({"type":data['type'][0],"product":data['product'][0], "value":float(data['value'][0]),"date":datetime.utcnow().strftime("%Y-%m-%d"),"id":data["id"][0]})
    return { "message" : "data has been added"}

@app.route('/login',methods=["POST"])
def login():
    post = request.form.to_dict(flat=False)
    data = tbluser.where(u'user',u'==',post["user"][0]).get()
    djson = []
    for i in range(len(data)):
        pwd = data[i].to_dict()['password']
        if(pwd == post["pwd"][0]):
            djson.append({"user" : data[i].to_dict()['user'],"id" :  data[i].to_dict()['id']})
            break
    return {"data":djson}

@app.route('/get_latest_asset',methods=["POST"])
def get_latest_asset():
    post = request.form.to_dict(flat=False)
    ids = post["id"][0]
    key_data = "asset" + ids
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        ## get lastest date
        dates = tblrecord.order_by(u'date', direction=firestore.Query.DESCENDING).get()
        date = ""
        for i in range(len(dates)):
            if(post["id"][0] == dates[i].to_dict()['id'] ):
                date = dates[i].to_dict()['date']
                break

        ## get data before lattest date and getting latest data based on latest date
        data = tblrecord.where(u'date',u'==',date).get()
        djson = []
        value = 0
        for i in range(len(data)):
            if(post["id"][0] == data[i].to_dict()['id']):
                date = data[i].to_dict()['date']
                value = data[i].to_dict()['value']
                product = data[i].to_dict()['product']
                djson.append({"date" : date, "product": product, "value" : value})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

if __name__ == "__main__":
    app.run(debug=True,)