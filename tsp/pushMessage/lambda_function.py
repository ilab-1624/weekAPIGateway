from LineApi import LineApi


def lambda_handler(event, context):
    inputModel = event
    
    lineApi = LineApi()
    
    templateMessages = []
    for message in inputModel['messages']:
        if (message['messageType'] == 'imageTemplate'):
            templateMessage = lineApi.getImageTemplateMessage(message['content'])
        
        elif (message['messageType'] == 'textTemplate'):
            templateMessage = lineApi.getTextTemplateMessage(message['content'])
        
        templateMessages.append(templateMessage)
    
    pushResult = lineApi.pushMessage(inputModel['receiverLineIdList'], templateMessages)
    print(pushResult)
    
    return pushResult