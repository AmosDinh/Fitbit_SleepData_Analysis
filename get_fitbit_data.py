
import json
import pandas as pd 
import datetime
#https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23B273&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fauthorized&scope=user%3Aemail
j = json.load(open('creds.json'))
client_secret = j['client_secret']
client_id = j['client_id']

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from flask import request
import requests
import base64
import json

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

fitbit = oauth.remote_app(
    'fitbit',
    consumer_key='23B273',
    consumer_secret='af150b0cf28a127234a1be99d329de2f',
    request_token_params={'scope': ['activity','sleep','profile','location','heartrate','weight','location']},
    base_url='https://api.fitbit.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.fitbit.com/oauth2/token',
    authorize_url='https://www.fitbit.com/oauth2/authorize'
)
code = None
def change_fitbit_header(uri, headers, body):
    global code
    auth = headers.get('user')
    if auth:
        """ auth = auth.replace('Bearer', 'OAuth2') """
        headers['Authorization'] = auth
        headers['grant_type'] = 'authorization_code'
        headers['code'] = code

    return uri, headers, body

fitbit.pre_request = change_fitbit_header



def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


#yyyy-MM-dd
def getHeartrate(user_id,startdate,enddate,headers):
    url = f'https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{startdate}/{enddate}.json'
    r = requests.get(url,headers=headers)
    return r

def getSleepstages(user_id,startdate,headers,enddate=None):
    #url=f'https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{date}.json'
    if enddate != None:
        url=f'https://api.fitbit.com/1.2/user/-/sleep/date/{startdate}/{enddate}.json'
    else:
        url=f'https://api.fitbit.com/1.2/user/-/sleep/date/{startdate}.json'

    print(url)
    req = requests.Request('GET',url,headers=headers)
    prepared = req.prepare()
    pretty_print_POST(prepared)
    return requests.get(url,headers=headers)


def getProfile(user_id,headers):
    url = f'https://api.fitbit.com/1/user/{user_id}/profile.json'
    r = requests.get(url,headers=headers)
    return r

def parse_sleepdata(j)->pd.DataFrame:
    dfs,names = [],[]
    
    for entry in j['sleep']:
      
        data =[]
        tdata = {}
        for longdata in entry['levels']['data']:
            #2021-07-12T07:13:30.000
            t = datetime.datetime.strptime(longdata['dateTime'],"%Y-%m-%dT%H:%M:%S.%f")
            lastt = t+ datetime.timedelta(seconds=int(longdata['seconds']))
            while t<=lastt:
                tdata[str(t)]=longdata['level']
                t +=datetime.timedelta(seconds=30)
        if entry['infoCode'] == 0 or entry['infoCode']==3:
            for shortdata in entry['levels']['shortData']:
                #2021-07-12T07:13:30.000
                t = datetime.datetime.strptime(shortdata['dateTime'],"%Y-%m-%dT%H:%M:%S.%f")
                lastt = t+ datetime.timedelta(seconds=int(shortdata['seconds']))
                while t<=lastt:
                    tdata[str(t)]=shortdata['level']
                    t +=datetime.timedelta(seconds=30)
        """         "logId": 32941186233,
        "minutesAfterWakeup": 0,
        "minutesAsleep": 455,
        "minutesAwake": 96,
        "minutesToFallAsleep": 0,
        "startTime": "2021-07-11T23:22:30.000",
        "timeInBed": 551,
        "type": "stages" """
        
        for k,v in tdata.items():
            data.append([k,v,entry['type'],entry['efficiency'],entry['isMainSleep'],
            entry['dateOfSleep'],entry['startTime'],entry['endTime'],entry['duration'],entry['timeInBed'],entry['minutesAsleep'],
            entry['minutesAwake'],entry['minutesToFallAsleep'],entry['minutesAfterWakeup']])
        
        df = pd.DataFrame(data=data,columns=["dt","stage","type",'efficiency','isMainSleep','dateOfSleep','startTime','endTime','duration','timeInBed',
        'minutesAsleep','minutesAwake','minutesToFallAsleep','minutesAfterWakeup'])
        df['dt'] = pd.to_datetime(df['dt'])
        
        df['weekday'] = datetime.datetime.strptime(entry['dateOfSleep'],"%Y-%m-%d").strftime('%A')
        df = df.sort_values(by='dt')
        dfs.append(df)
        name = ''
        
        if entry['infoCode'] == 0:
            name ='stages_main'
            df['hasSleepStages'] = True
            
        elif entry['infoCode'] == 1:
            name = 'nostages_main'
            df['hasNoSleepStages'] = True
        elif entry['infoCode'] == 2:
            name = 'nostages_nomain'
            df['hasNoSleepStages'] = True
        elif entry['infoCode'] == 3:
            name = 'stages_nomain'
            df['hasSleepStages'] = True

        df['sleep_type'] = name
        names.append(name+'_'+datetime.datetime.strftime(datetime.datetime.strptime(entry['dateOfSleep'],"%Y-%m-%d"),'%Y_%m_%d'+'.csv'))#+entry['type']

    return dfs, names


@app.route('/')
def index():
    """ if 'fitbit_token' in session:
        resp = request.args
        print(resp)
        me = fitbit.get('user')
        return me.data """
  
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return fitbit.authorize(callback='http://127.0.0.1:5000/authorized')#url_for('authorized', _external=True)


@app.route('/logout')
def logout():
    session.pop('fitbit_token', None)
    return redirect(url_for('index'))


@app.route('/authorized')
def authorized():
    global client_id
    global client_secret
    resp = request.args
    
    if resp is None or resp.get('code') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['fitbit_token'] = (resp['code'], '')
    code = resp['code']
    headers = {
        'Authorization': 'Basic '+base64.b64encode(('23B273:af150b0cf28a127234a1be99d329de2f').encode('ascii')).decode('ascii'),


    }
    data = {
          'client_id':'23B273',
    #'request_token_params':{'scope': ['activity','sleep','profile','location','heartrate','weight','location']},
    'grant_type':'authorization_code',
    'redirect_uri':'http://127.0.0.1:5000/authorized',
    'code':code,
 
    }
    
    """ me = fitbit.get('user') """
    r=requests.post('https://api.fitbit.com/oauth2/token',headers=headers,data=data)

    print(r.text)
    token  = json.loads(r.text)['access_token']
    print(r.headers,r.text,'toooken',token)
    #r =getHeartrate(user_id='23B273',date='today',period='1d',headers={'Authorization':'Bearer '+token})
    #r = getProfile('23B273',headers={'Authorization':'Bearer '+token})
    #r = getSleepstages(user_id=client_id,startdate='2021-09-20',enddate='2021-10-20',headers={'Authorization':'Bearer '+token})

    r= getHeartrate(user_id=client_id,startdate='2021-09-20',enddate='2021-10-20',headers={'Authorization':'Bearer '+token})
    print(r.text)
    return ' '
    exit()

    print('testt',r.headers,r.text)
    print('test')
    j = json.loads(r.text)
    """ if 'stages' in j['summary'].keys():
        with open() """
    dfs,names = parse_sleepdata(j)
    for i in range(0,len(dfs)):
        dfs[i].to_csv('sleepdata/'+names[i])
   
    return ' '
    

@app.route('/authorized2')
def authorized2():
    print(request.args,'testy',request,request.headers)
    return ' '

@fitbit.tokengetter
def get_fitbit_oauth_token():
    return session.get('fitbit_token')


if __name__ == '__main__':
    app.run()
