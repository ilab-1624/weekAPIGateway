from datetime import datetime
import copy


class lineMessageFormate:
    def __init__(self,dataModel,messageType):
        
        self.dataModel = dataModel
        self.messageType = messageType
        self.ReceiverLineIdList = []
        self.messages = []
        self.content = []

    def Addcontent(self,imageUrl,title,text):
        
        data = {
            "imageUrl":imageUrl,
            "title":title,
            "text":text
        }
        
        self.content.append(data)
    
    
    def formate_member(self):
    
        for model in self.dataModel:
            
            print(model)

            self.ReceiverLineIdList.append(model["lineId"]) 
            
            self.Addcontent(model["sourceImage"]["imageUrl"],"來源影像","時間: {} \n 簽到結果:成功".format(datetime.fromtimestamp(int(model['sourceImage']['timestamp'] + 28800))))
            self.Addcontent(model["sourceFaceImage"]["imageUrl"],"來源人臉","信心指數:{} %".format(round(model["sourceFaceImage"]["confidence"],2)))
            self.Addcontent(model["registrationFaceImage"]["imageUrl"],"註冊影像","姓名:{}\nfaceId:{}\n相似度:{}%"
            .format(model["registrationFaceImage"]["memberId"],model["registrationFaceImage"]["faceId"][0:18],round(model["registrationFaceImage"]["similarity"],2)))
            

            
            message = {
                "messageType": self.messageType,
                "content": copy.deepcopy(self.content)
                
            }
            
            self.messages.append(message)
            
            self.content.clear()
        
    def formate_Notmember(self):
        
        counter = 0
        
        
        #for lineid in self.dataModel["notMemberAlertMessage"]["receiverLineIdList"]:
        self.ReceiverLineIdList = self.dataModel["receiverLineIdList"]
        
        for model in self.dataModel["notMemberFaceImageList"]:
            
            self.Addcontent(self.dataModel["sourceImage"]["imageUrl"],"來源影像","來源人數:{}\n非成員人數:{}\n時間:{}"
            .format(self.dataModel["sourceImage"]["personCount"],self.dataModel["sourceImage"]["notMemberCount"],datetime.fromtimestamp(int(self.dataModel['sourceImage']['timestamp'] + 28800))))
            self.Addcontent(model["imageUrl"],"非成員"+str(counter),"信心指數:{} %".format(round(model["confidence"],2)))

            message = {
                "messageType": self.messageType,
                "content": copy.deepcopy(self.content)
                
            }

            counter += 1
            
            self.messages.append(message)
            
            self.content.clear()
    
    def formate_quota(self):
        
        self.ReceiverLineIdList = self.dataModel["receiverLineIdList"]
        
        for model in self.dataModel["notMemberFaceImageList"]:
        
            message = {
                "messageType": self.messageType,
                "content": "流量已用盡，請聯絡供應服務商"
            
            }
            

            self.messages.append(message)
                
        
    def getdata(self):
        
        LinepushModel = {
                "receiverLineIdList" : self.ReceiverLineIdList,
                "messages" : self.messages
            }
            
        print(LinepushModel)
        
        return self.ReceiverLineIdList , self.messages