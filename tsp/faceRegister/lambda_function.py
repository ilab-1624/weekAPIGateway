import boto3
import json
import awsConfig
import base64

def lambda_handler(event, context):
    # inputData = json.loads(event)
    inputData = event
    print(type(event))
    client = boto3.client(
            'rekognition',
            region_name=awsConfig.regionName,
            aws_access_key_id=awsConfig.aws_access_key_id,
            aws_secret_access_key=awsConfig.aws_secret_access_key
        )
    response = client.index_faces(
                CollectionId=awsConfig.collectionId,
                Image={'Bytes': base64.b64decode(inputData['userData']['picture'])},
                MaxFaces=1,
                ExternalImageId=inputData['userData']['username'],
                QualityFilter="AUTO",
                DetectionAttributes=['ALL']
            )
    return {'statusCode': 200, 'body': response}