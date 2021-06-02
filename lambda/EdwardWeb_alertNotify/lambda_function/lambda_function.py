import requests
import json
import config
import boto3
import thirdPartyServiceProviderConfig
from dataFormated import lineMessageFormate



client = boto3.client('lambda',aws_access_key_id = config.aws_access_key_id,aws_secret_access_key = config.aws_secret_access_key,region_name = config.region_name)

def lambda_handler(event, context):
    # TODO implement
    print(event)
    
    dataModel = event
    
    if len(dataModel["signInMemberList"]) != 0:
        print("memberPUSH")
        linemessage = lineMessageFormate(dataModel["signInMemberList"],"imageTemplate")
        linemessage.formate_member()
        receiverLineIdList , messages = linemessage.getdata()
        
        response = requests.post(thirdPartyServiceProviderConfig.Line_TSP_Url, data = json.dumps({
        "receiverLineIdList":receiverLineIdList,
        "messages":messages,
        "Content-Type":"application/json"
        }), headers={
            "x-api-key" : thirdPartyServiceProviderConfig.Line_Api_Key
        })
        
        print(response)
        
        if str(response) ==  "<Response [429]>":
            print("no quota")
            noquataMessage = lineMessageFormate(dataModel["notMemberAlertMessage"],"textTemplate")
            noquataMessage.formate_quota()
            receiverLineIdList , messages = noquataMessage.getdata()
            
            response = client.invoke(FunctionName='cloud9-tsp2NoQuotaAlert-tsp2NoQuotaAlert-npOYXNQC5Yxd',
                     InvocationType='RequestResponse',
                     Payload=json.dumps({
                        "receiverLineIdList":receiverLineIdList,
                        "messages":messages,                     
                     }))
            print(response)

    if len(dataModel["notMemberAlertMessage"]["notMemberFaceImageList"]) != 0:
        
        print("managerPUSH")
        linemessage = lineMessageFormate(dataModel["notMemberAlertMessage"],"imageTemplate")
        linemessage.formate_Notmember()
        receiverLineIdList , messages = linemessage.getdata()
        
        response = requests.post(thirdPartyServiceProviderConfig.Line_TSP_Url, data = json.dumps({
            "receiverLineIdList" : receiverLineIdList,
            "messages" : messages,
            "Content-Type":"application/json"
            }), headers={
                "x-api-key" : thirdPartyServiceProviderConfig.Line_Api_Key
            })
        print(response)
        if str(response) ==  "<Response [429]>":
            print("no quota")
            noquataMessage = lineMessageFormate(dataModel["notMemberAlertMessage"],"textTemplate")
            noquataMessage.formate_quota()
            receiverLineIdList , messages = noquataMessage.getdata()

            response = client.invoke(FunctionName='cloud9-tsp2NoQuotaAlert-tsp2NoQuotaAlert-npOYXNQC5Yxd',
                     InvocationType='RequestResponse',
                     Payload=json.dumps({
                        "receiverLineIdList":receiverLineIdList,
                        "messages":messages,
                     }))
            print(response)

        
    return 'suceess'