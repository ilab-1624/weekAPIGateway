from flask import Flask, render_template, session, request, redirect, url_for, jsonify, Response
from module import MemberRegisterController, ConfigController, CognitoApi
import json
from flask import Flask, request, g, render_template, jsonify, make_response, redirect, request, url_for, abort, session, flash
import requests
from module import agentConfig, fidoServerConfig, securityConfig, awsConfig
from werkzeug.http import parse_authorization_header
import boto3

application = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False
application = Flask(__name__, static_folder='static')



client = boto3.client('iam', region_name=awsConfig.regionName, aws_access_key_id=awsConfig.aws_access_key_id,
                      aws_secret_access_key=awsConfig.aws_secret_access_key)
cognitoApi = CognitoApi.CognitoApi()
agent = agentConfig.agent
fidoServerUrl = fidoServerConfig.fidoServerUrl
listPolicy=[]

# ========================== ↓↓↓↓ View ↓↓↓↓ ====================================

# ------------------------- ↓↓ home page ↓↓ ------------------------------------


@application.route("/", methods = ['GET','POST'])
def getMenu():
    if request.method == 'GET':
        return render_template('amsMenu.html' , agent=agent)
    if request.method == 'POST':
        choosedAgentName = agent
        securityStatus=securityConfig.securityStatus
        
        if  securityStatus=='enable':
            if request.form.get('成員註冊') == '成員註冊':
                btnValue = 'register'
                print("成員註冊")
                return redirect(url_for('memberRegister', _external=True, _scheme='https', btnName=btnValue,agentName=choosedAgentName))
            elif request.form.get('組態設定') == '組態設定':
                btnValue = 'config'
                print("組態設定")
                return redirect(url_for('login', _external=True, _scheme='https', btnName=btnValue,agentName = choosedAgentName))
            elif request.form.get('人流預測') == '人流預測':
                btnValue = 'forecast'
                print("人流預測")
                return redirect(url_for('login', _external=True, _scheme='https', btnName=btnValue,agentName = choosedAgentName))

            elif request.form.get('報表查詢') == '報表查詢':
                btnValue = 'report'
                print("報表查詢")
                return redirect(url_for('login', _external=True, _scheme='https', btnName=btnValue,agentName = choosedAgentName))
            else:
                print('unknown')
        else:
            if request.form.get('成員註冊') == '成員註冊':
                btnValue = 'register'
                return redirect(url_for('memberRegister', _external=True, _scheme='https', btnName=btnValue,agentName = choosedAgentName))
            elif request.form.get('組態設定') == '組態設定':
                btnValue = 'config'
                print("組態設定")
                return redirect("config")
            elif request.form.get('人流預測') == '人流預測':
                btnValue = 'forecast'
                print("人流預測")
                return redirect("forecastIndex")
    
            elif request.form.get('報表查詢') == '報表查詢':
                btnValue = 'report'
                print("報表查詢")
                return redirect("report")
            else:
                print('unknown')

#-------------------------------------------------------------------------------
@application.route("/login/<btnName>/<agentName>", methods=['GET', 'POST'])
def login(btnName,agentName):
    if request.method == 'GET':
        return render_template('webauthn.html', status=True,btnName=btnName,agentName=agentName, cognitoConfig={'userPoolId':awsConfig.userPoolId,'clientId': awsConfig.clientId})
    if request.method == 'POST':
        auth = request.headers.get('Authorization')
        # -----------------------get user data ----------------------------
        accessToken = request.get_data()
        decodeToken = accessToken.decode('utf-8')
        convertToJson = json.loads(decodeToken)
       
        # ------判斷user 是否在此agent群組中--------------------------------------------
        # getCognitoGroup = convertToJson['cognito:groups']

        getCognitoGroup = agentName
     
        clickAgentBehavior = agentName
        
        getUserName = convertToJson['username']
        name = getUserName
        # ------------------------------query user from IAM-------------------------------
        print(getUserName,name)
        # ---------------------- -------get user group -----------------------------------
        response = client.list_groups_for_user(
            UserName=name,
             MaxItems=123
        )
        print(response)
        print('--------------get user group-------- -----------------------------------')
        getGroup = response['Groups'][0]['GroupName']
        print(getGroup)
      
        
        # ----------------------------get group policy-----------------------------------
        print('get group policy')
        response = client.list_attached_group_policies(
            GroupName=getGroup,
            MaxItems=123
        )
        # print('---從群組連接--getGroup policy--------')
        for item in range(len(response['AttachedPolicies'])):
            getPolicyName = response['AttachedPolicies'][item]['PolicyName']
            listPolicy.append(getPolicyName)
        
        # ----------------------------get role policy------------------------------------------
        
        
        response = client.list_attached_role_policies(
            RoleName=getGroup,
            MaxItems=123
        )
       
        #-------------------------get role policy-------------------------------------------------
        
        for items in range(len(response['AttachedPolicies'])):
            getRolePolicy = response['AttachedPolicies'][items]['PolicyName']
           
            listPolicy.append(getRolePolicy)
            # print(listPolicy)
       

        #------------------------------ getUserPolicy----------------------------------------------- 
        response = client.list_attached_user_policies(
            UserName=name,
            MaxItems=123
        )
        # print('---直接連接---get user policy------')
        for policies in range(len(response['AttachedPolicies'])):
            getUserPolicy = response['AttachedPolicies'][policies]['PolicyName']
            listPolicy.append(getUserPolicy)
       
        #--------------------------------------get role policy---------------------------------------
        print('--------所有政策--------')
        print(listPolicy)
    # -----------authorization page-----判斷user policy有無在listpolicy中----------------------------
        userinfo=dict()
          
        getPersonalPolicy  = btnName+'_'+clickAgentBehavior

        print(getPersonalPolicy)
        print('====')

        # print('判斷此使用者行為btnName+此人選擇的agent')
        # print(getPersonalPolicy)
        if getPersonalPolicy in listPolicy:
            loginStatus = 'success'
            print(loginStatus)
            print("=====================")
        else:
            loginStatus = 'fail'
            print(loginStatus)
            print("=====================")
    
    # ------------  get information compose to  dict---return response to client----------------------
        userinfo['auth'] = auth
        userinfo['name'] = name
        userinfo['policy'] = listPolicy
        userinfo['loginStatus'] = loginStatus
        userinfo['behavior']=btnName
        userinfo['userAgent'] = getCognitoGroup
        userinfo['agentBehavior'] = clickAgentBehavior
       
        print(userinfo)
        return jsonify(userinfo)
# ------------------------ ↓↓ memberRegister ↓↓ --------------------------------

@application.route("/memberRegister", methods = ['GET', 'POST'])
def memberRegister():
    if request.method == 'GET':
        return render_template('memberRegisterRequest.html', agent=agent, fidoServerUrl=fidoServerUrl)
    
    if request.method == 'POST':
        daoModel = {
            'userData':{
                'username': request.values['username']
            }
        }

        attributesRetrieveList = [
            'sub',
            'custom:lineId',
            'custom:faceId'
        ]
        retrieveResult = cognitoApi.retrieveUsers(daoModel, 'username', attributesRetrieveList)

        print(retrieveResult)
        
        userModel = {
            'username': request.values['username'],
            'sub': retrieveResult['body']['Users'][0]['Attributes'][0]['Value'],
            'email': request.values['email'],
            'name': request.values['lineNickname'],
            'custom:lineId': retrieveResult['body']['Users'][0]['Attributes'][1]['Value'],
            'custom:faceId': retrieveResult['body']['Users'][0]['Attributes'][2]['Value'],
            'agent': agent
        }
        
        if request.values['role'] == 'customer':
            userModel['ch_role'] = '成員'
        elif request.values['role'] == 'staff':
            userModel['ch_role'] = '工程師'
        else:
            userModel['ch_role'] = '管理員'
        
        return render_template('memberRegisterResponse.html', userModel=userModel)

# --------------------------- ↓↓ config ↓↓ -------------------------------------

configController = ConfigController.ConfigController()
@application.route("/config",methods = ['GET'])
def getConfigMenu():
    if request.method == 'GET':
        return render_template('configMenu.html' , agent = agent)


@application.route("/config/objectDetect/update",methods = ['GET'])
def getConfigObject():
    if request.method == 'GET':
        aiConfigData = configController.retrieveAiConfig('objectDetection')
        return render_template('configObject.html', aiConfig = aiConfigData)

@application.route("/config/memberRecognition/update",methods = ['GET'])
def getConfigFace():
    if request.method == 'GET':
        aiConfigData = configController.retrieveAiConfig('faceRecognition')
        return render_template('configFace.html', aiConfig = aiConfigData)

@application.route("/config/ppeDetect/update",methods = ['GET'])
def getConfigPpe():
    if request.method == 'GET':
        aiConfigData = configController.retrieveAiConfig('ppeValidation')
        return render_template('configPpe.html', aiConfig = aiConfigData)

@application.route("/config/fraudDetect/update",methods = ['GET'])
def getConfigAnomaly():
    if request.method == 'GET':
        aiConfigData = configController.retrieveAiConfig('anomalyDetection')
        return render_template('configAnomaly.html', aiConfig = aiConfigData)

@application.route("/config/forecast/update",methods = ['GET'])
def getConfigForecast():
    if request.method == 'GET':
        aiConfigData = configController.retrieveAiConfig('forecast')
        return render_template('configForecast.html', aiConfig = aiConfigData)

# ======================= ↓↓↓↓ Controller ↓↓↓↓ ==================================
configController = ConfigController.ConfigController()
# --------------------------- ↓↓ config ↓↓ --------------------------------------

@application.route("/updateAiConfig",methods = ['POST'])
def updateAiConfig():
    aiConfigData = json.loads(request.get_data())
    configController.updateAiConfig(aiConfigData)

    return jsonify('ok')

# ------------------------ ↓↓ memberRegister ↓↓ ----------------------------------

memberRegisterController = MemberRegisterController.MemberRegisterController()
@application.route("/register/signUp", methods = ['POST'])
def signUp():
    userData = json.loads(request.get_data())
    result = memberRegisterController.signUp(userData)

    return jsonify(result)

@application.route("/register/confirm", methods = ['POST'])
def confirm():
    userData = json.loads(request.get_data())
    result = memberRegisterController.confirm(userData)

    return jsonify(result)

@application.route("/fido", methods = ['POST'])
def fido():
    viewData = json.loads(request.get_data())
    result = memberRegisterController.fido(viewData)

    return jsonify(result)

@application.route("/face", methods = ['POST'])
def face():
    viewData = json.loads(request.get_data())

    result = memberRegisterController.face(viewData)
    
    return jsonify(result)

@application.route("/line", methods = ['POST'])
def line():
    daoData = json.loads(request.get_data())
    print(daoData)
    result = memberRegisterController.line(daoData)
    return jsonify(result)





if __name__ == '__main__':
    application.config['TEMPLATES_AUTO_RELOAD'] = True      
    application.jinja_env.auto_reload = True
    application.run(debug=True)