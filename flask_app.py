from webportfolio import app, current_app,pd,request,redis_server,json,tbltype,tblproduct,tblrecord,firestore,datetime,timedelta,tbluser,Response
import apistockanalysis

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
    # ids = "1aby"
    key_data = "saldo" + ids
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        ## get lastest date
        dates = tblrecord.order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()
        date = ""
        datebefore = ""
        for i in range(len(dates)):
            if(ids == dates[i].to_dict()['id'] ):
                date = dates[i].to_dict()['date']
                break

        latestdate = datetime(date.year,date.month,date.day)
        ## get data before lattest date and getting latest data based on latest date
        data = tblrecord.where(u'date',u'>=',latestdate).get()
        databefore = tblrecord.where(u'date',u'<',latestdate).order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()
        for i in range(len(databefore)):
            if(ids == databefore[i].to_dict()['id'] ):
                datebefore = databefore[i].to_dict()['date']
                break

        before_date = datetime(datebefore.year,datebefore.month,datebefore.day)
        databefore_ = tblrecord.where(u'date',u'>=',before_date).where(u'date',u'<',latestdate).get()
        djson = []
        value = 0
        valuebefore = 0
        for i in range(len(databefore_)):
            if(ids == databefore_[i].to_dict()['id']):
                valuebefore = valuebefore + databefore_[i].to_dict()['value']
        for i in range(len(data)):
            if(ids == data[i].to_dict()['id']):
                date = data[i].to_dict()['date']
                value = value + data[i].to_dict()['value']
                bulan = str(date.month)
                days = str(date.day)
                if(date.month < 10):
                    bulan =  "0"+str(bulan)
                if(date.day < 10):
                    days = "0"+str(date.day)
                if(i == len(data)-1):
                    djson.append({"date" : str(date.year) + "-" + bulan + "-" + days, "saldo" : value, "saldobefore": valuebefore})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

@app.route('/getrecord',methods=["POST"])
def getrecord():
    post = request.form.to_dict(flat=False)
    ids = post["id"][0]
    # ids = "1aby"
    key_data = "getrecord" + ids + post["date"][0]
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        date_obj = datetime.strptime(post["date"][0], "%Y-%m-%d")

        # Extract the year, month, and day components
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # Create a new datetime object with the extracted components
        new_date_obj = datetime(year, month, day)
        next_day = date_obj + timedelta(days=1)
        data = tblrecord.where(u'date',u'>=',new_date_obj).where(u'date','<',next_day).get()
        djson = []
        for i in range(len(data)):
            if(data[i].to_dict()['id'] == ids):
                date = data[i].to_dict()['date']
                value = data[i].to_dict()['value']
                type = data[i].to_dict()['type']
                product = data[i].to_dict()['product']
                bulan = str(date.month)
                days = str(date.day)
                if(date.month < 10):
                    bulan =  "0"+str(bulan)
                if(date.day < 10):
                    days = "0"+str(date.day)
                djson.append({"date" : str(date.year) + "-" + bulan + "-" + days, "value" : value, "type" : type, "product" : product})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
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
    tblrecord.add({"type":data['type'][0],"product":data['product'][0], "value":float(data['value'][0]),"date":firestore.SERVER_TIMESTAMP,"id":data["id"][0]})
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
        dates = tblrecord.order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()
        datez = ""
        for i in range(len(dates)):
            if(post["id"][0] == dates[i].to_dict()['id'] ):
                datez = dates[i].to_dict()['date']
                break

        ## get data before lattest date and getting latest data based on latest date
        latestdate = datetime(datez.year,datez.month,datez.day)
        data = tblrecord.where(u'date',u'>=',latestdate).get()
        djson = []
        value = 0
        for i in range(len(data)):
            if(post["id"][0] == data[i].to_dict()['id']):
                date = data[i].to_dict()['date']
                value = data[i].to_dict()['value']
                product = data[i].to_dict()['product']
                bulan = str(date.month)
                days = str(date.day)
                if(date.month < 10):
                    bulan =  "0"+str(bulan)
                if(date.day < 10):
                    days = "0"+str(date.day)
                djson.append({"date" : str(date.year) + "-" + bulan + "-" + days, "product": product, "value" : value})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

@app.route('/download_excel')
def download_excel():
    # create a pandas DataFrame
    data = {'Name': ['John', 'Mary', 'Bob'],
            'Age': [25, 30, 35],
            'Country': ['USA', 'Canada', 'UK']}
    df = pd.DataFrame(data)

    # create an Excel file from the DataFrame
    excel_file = pd.ExcelWriter('data.xlsx', engine='xlsxwriter')
    df.to_excel(excel_file, index=False)
    excel_file.save()

    # read the Excel file and return as a response
    with open('data.xlsx', 'rb') as excel:
        data = excel.read()

    return Response(data,headers={'Content-Disposition': 'attachment; filename=data.xlsx'},content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/get_record_by_range',methods=["POST"])
def get_record_by_range():
    post = request.form.to_dict(flat=False)
    djson = []
    ids = post["id"][0]
    # ids = "1aby"
    key_data = "get_record_by_range" + ids + post["datestart"][0] + post["datefinish"][0]
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        date_obj = datetime.strptime(post["datestart"][0], "%Y-%m-%d")
        date_obj_finish = datetime.strptime(post["datefinish"][0], "%Y-%m-%d")
        # date_obj = datetime.strptime("2023-01-01", "%Y-%m-%d")
        # date_obj_finish = datetime.strptime("2023-03-24", "%Y-%m-%d")

        # Extract the year, month, and day components
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        year_finish = date_obj_finish.year
        month_finish = date_obj_finish.month
        day_finish = date_obj_finish.day

        # Create a new datetime object with the extracted components
        datestart = datetime(year, month, day)
        datefinish = datetime(year_finish, month_finish, day_finish)
        data = tblrecord.where(u'date', u'>=', datestart).where(u'date',u'<=',datefinish).order_by(u'date', direction=firestore.Query.DESCENDING).get()

        listday = []
        listmoney = []
        for i in range(len(data)):
            value = data[i].to_dict()['value']
            date = data[i].to_dict()['date']
            bulan = str(date.month)
            days = str(date.day)
            if(date.month < 10):
                bulan =  "0"+str(bulan)
            if(date.day < 10):
                days = "0"+str(date.day)
            if(len(listday) == 0):
                if(ids == data[i].to_dict()['id']):
                    listday.append(str(date.year) + "-" + bulan + "-" + days)
                    listmoney.append(value)
            else:
                flag = 0
                for j in range(len(listday)):
                    if(ids == data[i].to_dict()['id']):
                        if(listday[j] == str(date.year) + "-" + bulan + "-" + days):
                            flag = 1
                            listmoney[j] = listmoney[j] + value
                if(flag == 0):
                    if(ids == data[i].to_dict()['id']):
                        listday.append(str(date.year) + "-" + bulan + "-" + days)
                        listmoney.append(value)

        for i in range(len(listday)):
            djson.append({"date":listday[i], "money":listmoney[i]})
        redis_server.set(key_data,json.dumps({"data":djson}))
        redis_server.expire(key_data,7200)
        return {"data":djson}

@app.route('/get_list_emiten')
def get_list_emiten():
    json_arr = []
    key_data = "shmindo"
    fromredis = redis_server.get(key_data)
    if(fromredis):
        return json.loads(fromredis)
    else:
        csv_path = current_app.open_resource('static/assets/csv/List Emiten/all.csv')
        df = pd.read_csv(csv_path)

        for i in range(len(df)):
            json_arr.append({"code" : df["code"][i], "name" : df["name"][i]})
        redis_server.set(key_data,json.dumps({"data":json_arr}))
        redis_server.expire(key_data,14400)
        return {"data":json_arr}

if __name__ == "__main__":
    app.run()