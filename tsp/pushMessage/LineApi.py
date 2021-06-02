import chatBotConfig
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import JoinEvent, MemberJoinedEvent, TextSendMessage, TemplateSendMessage, CarouselColumn, CarouselTemplate, PostbackAction


class LineApi:
    def __init__(self):
        self.__channelSecret = chatBotConfig.channelSecret
        self.__channelAccessToken = chatBotConfig.channelAccessToken
        self.__handler = WebhookHandler(self.__channelSecret)
        self.__lineBotApi = LineBotApi(self.__channelAccessToken)
    
    def handleEvent(self, event):
        try:
            response = None
            
            @self.__handler.add(JoinEvent)
            def handle_join(event):
                getGroupSummaryResponse = self.getGroupSummary(event.source.group_id)

                nonlocal response
                response = {
                    'eventType': 'join',
                    'replyToken': event.reply_token,
                    'group': getGroupSummaryResponse['body']
                }

            @self.__handler.add(MemberJoinedEvent)
            def handle_memberJoined(event):
                getGroupSummaryResponse = self.getGroupSummary(event.source.group_id)
                getGroupMemberProfileResponse = self.getGroupMemberProfile(event.source.group_id, event.joined.members[0].user_id)
                
                nonlocal response
                response = {
                    'eventType': 'memberJoined',
                    'replyToken': event.reply_token,
                    'group': getGroupSummaryResponse['body'],
                    'user': getGroupMemberProfileResponse['body']
                }
            
            self.__handler.handle(event['body'], event['signature'])
            
            return {'statusCode': 200, 'body': response}
            
        except InvalidSignatureError:
            return {'statusCode': 400, 'body': 'InvalidSignature'}
        
        except LineBotApiError as e:
            print(e.error.message)
            return {'statusCode': 500, 'body': e.error.message}
    
    def getGroupSummary(self, groupId):
        try:
            summary = self.__lineBotApi.get_group_summary(groupId)
            response = {
                'groupId': summary.group_id,
                'groupName': summary.group_name,
                'pictureUrl': summary.picture_url
            }
            
            return {'statusCode': 200, 'body': response}
        
        except LineBotApiError as e:
            print(e.error.message)
            return {'statusCode': 500, 'body': e.error.message}
    
    def getGroupMemberProfile(self, groupId, userId):
        try:
            profile = self.__lineBotApi.get_group_member_profile(groupId, userId)
            response = {
                'userId': profile.user_id,
                'displayName': profile.display_name,
                'pictureUrl': profile.picture_url
            }
            
            return {'statusCode': 200, 'body': response}
        
        except LineBotApiError as e:
            print(e.error.message)
            return {'statusCode': 500, 'body': e.error.message}
    
    def getImageTemplateMessage(self, content):
        carouselColumns = []
        for carouselColumnModel in content:
            carouselColumn = CarouselColumn(
                thumbnail_image_url=carouselColumnModel['imageUrl'],
                title=carouselColumnModel['title'],
                text=carouselColumnModel['text'],
                actions=[
                    PostbackAction(
                        label=' ',
                        data='doNothing'
                    )
                ]
            )
            carouselColumns.append(carouselColumn)
        
        carouselTemplate = TemplateSendMessage(
            alt_text='收到新訊息，請查看！！',
            template=CarouselTemplate(
                columns=carouselColumns
            )
        )
        
        return carouselTemplate
    
    def getTextTemplateMessage(self, content):
        textTemplate = TextSendMessage(text=content)
        return textTemplate
    
    def replyMessage(self, replyToken, messages):
        try:
            self.__lineBotApi.reply_message(replyToken, messages)
            return {'statusCode': 200, 'body': 'Success'}
        
        except LineBotApiError as e:
            print(e.error.message)
            return {'statusCode': 500, 'body': e.error.message}
            
    def pushMessage(self, receiverLineIdList, messages):
        try:
            self.__lineBotApi.multicast(receiverLineIdList, messages)
            return{'statusCode': 200, 'body': 'Success'}
            
        except LineBotApiError as e:
            print(e.error.message)
            return {'statusCode': 500, 'body': e.error.message}