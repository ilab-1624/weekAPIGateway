import json
import base64
import boto3
import awsConfig

def lambda_handler(event, context):
    # TODO implement
    # faceImage = json.loads(event['base64string'])
    faceImage = event['base64string']
    client = boto3.client('rekognition',aws_access_key_id=awsConfig.aws_access_key_id, aws_secret_access_key=awsConfig.aws_secret_access_key,region_name=awsConfig.regionName)
    response = client.search_faces_by_image(CollectionId=awsConfig.collectionId,
                                    Image={'Bytes':base64.b64decode(faceImage)},
                                    FaceMatchThreshold=70,
                                    MaxFaces=1)
                                    
    return response