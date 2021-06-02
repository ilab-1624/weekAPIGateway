import boto3
import uuid
import json
import numpy as np
import cv2
import base64
import requests
from datetime import datetime
import copy
import psycopg2
import thirdPartyServiceProviderConfig

class S3:
    def __init__(self,regionName,bucketName,agentName,aws_access_key_id,aws_secret_access_key):
        self.__regionName = regionName
        self.__bucketName = bucketName
        self.__webname = agentName
        self.__aws_access_key_id = aws_access_key_id
        self.__aws__secret_access_key = aws_secret_access_key
        self.__client = boto3.client('s3',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=regionName)
    """def storeJson(self,key,body):
        self.__client.put_object(Body=str(json.dumps(body)),
                                Bucket = self.__bucketName,
                                Key = key)
    def readJson(self,key):
        body = self.__client.get_object(Bucket = self.__bucketName,
                                          Key = key)['Body']
        jsonString = body.read().decode('utf-8')
        jsonData = json.loads(jsonString) #{"imageData":[],memberIdList}
        body.close()
        return jsonData"""
    def listObjects(self,keyword):
        print(keyword)
        newkeyword = '/registration-faces/' + keyword
        print(newkeyword)
        
        listObjectsResponse = self.__client.list_objects_v2(Bucket=self.__bucketName,
                                                                #Prefix = keyword
                                                                StartAfter=keyword,
                                                                MaxKeys = 1)
        return listObjectsResponse
    def storeImage(self,image,dirname,fileName):
        self.__client.put_object(ACL='public-read',
                                 Body=image,
                                 Bucket=self.__bucketName,
                                 Key=fileName ,
                                 ContentEncoding='base64',
                                 ContentType='image/jpeg')
        imageUrl = ['https://' + self.__bucketName + '.s3-'+self.__regionName + '.amazonaws.com/'+fileName]
        return imageUrl
    def getWebName(self):
        return self.__webname
    def getBucketName(self):
        return self.__bucketName
    def getRegionName(self):
        return self.__regionName
class Rekognition:
    def __init__(self,regionName,aws_access_key_id,aws_secret_access_key,image):
        self.__regionName = regionName
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__client = boto3.client('rekognition',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=regionName)
        self.__image = image
        self.__rekognitionModel = {}
    def faceDetect(self):
        binaryImage = base64.b64decode(self.__image)
        faceDetectResponse = self.__client.detect_faces(Image={'Bytes': binaryImage})
        return faceDetectResponse
    def faceSearch(self,collectionId,image,threshold):
        faceMatchResponse = {}
        try:
            faceMatchResponse = self.__client.search_faces_by_image(CollectionId = collectionId,
                                                                    Image={'Bytes':image},
                                                                    FaceMatchThreshold=threshold,
                                                                    MaxFaces=1)
        except:
            faceMatchResponse["FaceMatches"] = []
        return faceMatchResponse
    def faceCreate(self,collectionId,image,uid):
        faceCreateResponse=self.__client.index_faces(CollectionId=collectionId,
                                                    Image={'Bytes':image},
                                                    MaxFaces=3,
                                                    ExternalImageId=uid,
                                                    QualityFilter="AUTO",
                                                    DetectionAttributes=['ALL'])
        return faceCreateResponse
    def getModel(self):
        return self.__rekognitionModel

class QueryGroup:
    def __init__(self,regionName,aws_access_key_id,aws_secret_access_key,groupName,agentName):
        self.__regionName = regionName
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__groupName = groupName
        self.__agentName = agentName
        self.__client = boto3.client('iam',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=regionName)

    def listGroupUsers(self):
        
        listUsersResponse = self.__client.get_group(
            GroupName = self.__groupName
        )
    
        usernameList = []
        
        for user in listUsersResponse['Users']:
            usernameList.append(user['UserName'])
        
        print('list is below:\n{}\n\n'.format(usernameList))
        
        return usernameList
        
    def signInAuthrization(self,userName):

        listPolicy = []
        listGroupResponse = self.__client.list_groups_for_user(
            UserName=userName
        )
        for group in listGroupResponse['Groups']:
            listGroupPoliciesResponse = self.__client.list_attached_group_policies(
                GroupName=group['GroupName'],
                MaxItems=123
            )
            for item in range(len(listGroupPoliciesResponse['AttachedPolicies'])):
                getPolicyName = listGroupPoliciesResponse['AttachedPolicies'][item]['PolicyName']
                listPolicy.append(getPolicyName)
    
        listUserPoliciesResponse = self.__client.list_attached_user_policies(
            UserName=userName,
            MaxItems=123
        )
    
        for policies in range(len(listUserPoliciesResponse['AttachedPolicies'])):
            getUserPolicy = listUserPoliciesResponse['AttachedPolicies'][policies]['PolicyName']
            listPolicy.append(getUserPolicy)
    
        if ('signIn_' + self.__agentName in listPolicy):
            print('you are authorize to sign in.')
            return True
        else:
            print('you are not authorize to sign in.')
            return False
    
class QueryUsers:
    def __init__(self,regionName,aws_access_key_id,aws_secret_access_key,USER_POOL_ID,attributeList):
        self.__regionName = regionName
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__USER_POOL_ID = USER_POOL_ID
        self.__attributeList = attributeList
        self.__client = boto3.client('cognito-idp',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=regionName)
                                     
    def getUserData(self,username):
        #userDataList = []
        try:
            searchResponse = self.__client.list_users(
                UserPoolId = self.__USER_POOL_ID,
                AttributesToGet = self.__attributeList,
                Filter="username=\"" + username + "\""
            )
            
            userData = {
                'username': searchResponse['Users'][0]['Username'],
                'attributes': searchResponse['Users'][0]['Attributes']
            }
            
            print(userData)
            #userDataList.append(userData)
        except Exception as e:
            print(e)
            return None
            
        return userData
        
    def listallUsers(self):
        searchResponse = self.__client.list_users(
                UserPoolId = self.__USER_POOL_ID,
                AttributesToGet = self.__attributeList
            )
        
        return searchResponse
            
class FaceSearch:
    def __init__(self,dataModel,s3,rekognition,group,users,collectionId):
        self.__dataModel = dataModel
        self.__s3 = s3
        self.__rekognition = rekognition
        self.__iam = group
        self.__cognito = users
        self.__collectionId = collectionId
    def signInFace(self):
        image = self.__dataModel["frame"]["openCV"]["imageBase64"]
        binaryImage = base64.b64decode(self.__dataModel["frame"]["openCV"]["imageBase64"])
        #print(type(binaryImage))
        fileName = self.__dataModel['agent'] + '/sourceImage'+'/image_' + str(self.__dataModel["frame"]["captureResult"]["timestamp"]) + '.jpg'
        dirname = self.__dataModel['agent'] + '/' + 'sourceImage/'
        sourceImageURL = self.__s3.storeImage(binaryImage,dirname,fileName) 
        faceDetectResponse = self.__rekognition.faceDetect()
        
        print(faceDetectResponse)
        
        faceBoundingBoxList = []
        faceImageIdList = []
        memberCount = 0
        notmemberCount = 0

        threshold = 80
        serialNo = 0
        self.__dataModel["signInMemberList"] = [] #成員
       # self.__dataModel["notMemberAlertMessage"] #非成員
        #print(self.__iam.listGroupUsers())
        mamngers = []
        mangerlineId = None
        for manger in self.__iam.listGroupUsers():
            mangerlineId = self.__cognito.getUserData(manger)
            #print("aaa")
            print(mangerlineId["attributes"][1]["Value"])
            mamngers.append(mangerlineId["attributes"][1]["Value"])
        #print(self.__cognito.getUserData(manger)["attributes"][0]["Value"])
        self.__dataModel["notMemberAlertMessage"] = {
            "receiverLineIdList" : mamngers,
            "sourceImage" : {
                    "imageUrl":sourceImageURL[0],
                    "personCount":len(faceDetectResponse["FaceDetails"]),
                    "notMemberCount":None,
                    "timestamp":self.__dataModel["frame"]["captureResult"]["timestamp"]
                },
            "notMemberFaceImageList" : [] #非成員
        }
        
        if len(faceDetectResponse["FaceDetails"]) >= 1: #source中有複數人臉
            for face in faceDetectResponse["FaceDetails"]:
                faceBoundingBoxList.append(face["BoundingBox"])
            faceImageList = self.spliteImage(faceBoundingBoxList) #切割
            for image in faceImageList: #儲存切割下來的所有人臉,不需要特殊處理,命名規則為face+時間+編號.jpg
                fileName = self.__dataModel['agent'] + '/face' + str(self.__dataModel["frame"]["captureResult"]["timestamp"]) + str(serialNo) + '.jpg'
                dirname = self.__dataModel['agent']
                faceImageUrl = self.__s3.storeImage(image,dirname,fileName)
                serialNo += 1
            serialNo = 0
            ##############################
            print(len(faceImageList))
            
            for faceImage in faceImageList: #一張一張人臉慢慢找
                # searchFaceResponse=self.__rekognition.faceSearch(self.__collectionId, #成員與簽到人臉匹配
                #                                                 faceImage,
                #                                                 threshold)
                                                                
                searchFaceResponse = requests.post(thirdPartyServiceProviderConfig.Rekognition_TSP_Url, data = json.dumps({
                    "base64string" : base64.b64encode(faceImage).decode(),
                    "Content-Type":"application/json"
                    }), headers={
                        #"x-api-key" : thirdPartyServiceProviderConfig.Rekognition_TSP_Api_Key
                    })
            
                searchFaceResponse = json.loads(searchFaceResponse.text)
                print(searchFaceResponse)
                
                fileName = self.__dataModel['agent'] + '/face' + str(self.__dataModel["frame"]["captureResult"]["timestamp"]) + str(serialNo) + '.jpg' #切割的臉檔案名稱
                
                faceImageIdList = [] #清空
                
                if len(searchFaceResponse["FaceMatches"]) != 0:
                    
                    #memberFaceListResponse = self.__s3.listObjects(searchFaceResponse["FaceMatches"][0]["Face"]["ExternalImageId"]) #從s3找出以成員名稱(ExternalImageId)開頭的image檔案

                    #faceImageIdList = self.getMemberFaceIdList(searchFaceResponse["FaceMatches"][0]["Face"]["ExternalImageId"],memberFaceListResponse["Contents"])
                    
                    #memberFileName =  searchFaceResponse["FaceMatches"][0]["Face"]["ExternalImageId"] + '_' + str(faceImageIdList[0])
                    
                    if(self.__iam.signInAuthrization(searchFaceResponse["FaceMatches"][0]["Face"]["ExternalImageId"])):
                        
                        user = self.__cognito.getUserData(searchFaceResponse["FaceMatches"][0]["Face"]["ExternalImageId"])
                    
                    
                        self.__dataModel["signInMemberList"].append({
                            "lineId":user["attributes"][1]["Value"],
                            "sourceImage":{
                                "imageUrl":sourceImageURL[0],
                                "timestamp":self.__dataModel["frame"]["captureResult"]["timestamp"]
                            },
                            "sourceFaceImage":{
                                "imageUrl":'https://' + self.__s3.getBucketName() + '.s3-'+self.__s3.getRegionName() + '.amazonaws.com/' + fileName,
                                "confidence":searchFaceResponse["SearchedFaceConfidence"]
                                
                            },
                            "registrationFaceImage":{
                                "imageUrl":user["attributes"][3]["Value"],
                                "memberId":user["username"],
                                "faceId":user["attributes"][2]["Value"],
                                "similarity":searchFaceResponse["FaceMatches"][0]["Face"]["Confidence"]
                            }
                            })
                            
                        
                        memberCount += 1
                        print("memberCount:" )
                        print(memberCount)
                        
                    else:
                        print("IAM not member")
                    
                elif len(searchFaceResponse["FaceMatches"]) == 0:
                    self.__dataModel["notMemberAlertMessage"]["notMemberFaceImageList"].append({
                            "imageUrl":'https://' + self.__s3.getBucketName() + '.s3-' + self.__s3.getRegionName() + '.amazonaws.com/' +fileName ,
                            "confidence":faceDetectResponse["FaceDetails"][notmemberCount]["Confidence"]
                        })
                        
                    notmemberCount +=1
                    print("notmemberCount:" )
                    print(notmemberCount)
                    pass #非成員人臉
                
                serialNo += 1
                
        self.__dataModel["notMemberAlertMessage"]["sourceImage"]["notMemberCount"] = notmemberCount
        
    def getMemberFaceIdList(self,memberName,faceImageFileList):
        faceImageIdList = []
        for face in faceImageFileList: #成員所有已註冊的人臉數,現在一個人只有一張人臉
            print(face)
            try:
                name,faceImageId = face["Key"].split('_')[0],face["Key"].split('_')[1]
                #name = name.split('/')[1]
                if name == memberName: #根據對應的成員id將對應成員的人臉加入list
                    faceImageIdList.append(faceImageId)
            except Exception as e:
                print(e)
                #break
        return faceImageIdList
        
    def getMemberFaceURl(self,memberName,faceImageFileList):
        faceImageIdList = []
        for face in faceImageFileList: #成員所有已註冊的人臉數,現在一個人只有一張人臉
            print(face)
            try:
                name,faceImageId = face["Key"].split('_')[0],face["Key"].split('_')[1]
                #name = name.split('/')[1]
                if name == memberName: #根據對應的成員id將對應成員的人臉加入list
                    faceImageIdList.append(faceImageId)
            except Exception as e:
                print(e)
                #break
        return faceImageIdList

    def spliteImage(self,boundingboxes):
        imagelist = []
        image = np.fromstring(base64.b64decode(self.__dataModel["frame"]["openCV"]["imageBase64"]),np.uint8)
        image = cv2.imdecode(image,cv2.IMREAD_COLOR)
        size = image.shape
        height , width = size[0],size[1]
        for BBox in boundingboxes:
            upperLeftPointX = int(BBox['Left']*width)
            upperLeftPointY = int(BBox['Top']*height)
            lowerRightPointX = int((BBox['Left']+BBox['Width'])*width)
            lowerRightPointY = int((BBox['Top']+BBox['Height'])*height)
            cut_image = copy.deepcopy(image)[upperLeftPointY:lowerRightPointY,upperLeftPointX:lowerRightPointX]
            cut_image = base64.b64encode(cv2.imencode('.jpg', cut_image)[1]).decode()
            cut_image = base64.b64decode(cut_image)

            imagelist.append(cut_image)
            
        return imagelist
        
    def getModel(self):
        self.__dataModel["frame"]["openCV"]["imageBase64"] = ""
        print(self.__dataModel)
        return self.__dataModel

