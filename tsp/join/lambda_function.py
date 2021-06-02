import json
import requests
import serviceRequesterConfig
from LineApi import LineApi


def lambda_handler(event, context):
    eventObject = {
        'body': event['body'],
        'signature': event['headers']['x-line-signature']
    }
    
    lineApi = LineApi()
    handleResult = lineApi.handleEvent(eventObject)
    
    if (handleResult['statusCode']==200 and handleResult['body']!=None):
        if (handleResult['body']['eventType'] == 'join'):
            content = '群組名稱：{}\n' \
                      '群組ID：{}\n'.format(handleResult['body']['group']['groupName'], handleResult['body']['group']['groupId'])
            joinMessage = lineApi.getTextTemplateMessage(content=content)
            lineApi.replyMessage(handleResult['body']['replyToken'], joinMessage)
        
        elif (handleResult['body']['eventType'] == 'memberJoined'):
            daoData = {
                'id':{
                    'custom:lineId': handleResult['body']['user']['userId']
                },
                'userData':{
                    'name': handleResult['body']['user']['displayName']
                }
            }
        
            for requester in serviceRequesterConfig.requesters:
                if (handleResult['body']['group']['groupName'] == requester['lineGroupName']):
                    response = requests.post( requester['url']+ '/line', data=json.dumps(daoData))
    
    print(handleResult)
    
    return handleResult