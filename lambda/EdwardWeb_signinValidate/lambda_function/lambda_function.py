import json
from faceSearch import S3,Rekognition,FaceSearch,QueryGroup,QueryUsers#class
import config


def lambda_handler(event, context):
    dataModel = event
    s3 = S3(config.region_name,
            config.sourceBucketName,
            dataModel["agent"],
            config.aws_access_key_id,
            config.aws_secret_access_key)
    rekognition = Rekognition(config.region_name,
                              config.aws_access_key_id,
                              config.aws_secret_access_key,
                              dataModel["frame"]["openCV"]["imageBase64"])
                              
    iam = QueryGroup(config.region_name,
                              config.aws_access_key_id,
                              config.aws_secret_access_key,
                              config.groupName,
                              dataModel["agent"])      
                              
    users = QueryUsers(config.region_name,
                              config.aws_access_key_id,
                              config.aws_secret_access_key,
                              config.USER_POOL_ID,
                              config.attributeList)
                              
    faceSearch = FaceSearch(dataModel,
                            s3,
                            rekognition,
                            iam,
                            users,
                            config.collectionId)
                            
    faceSearch.signInFace()
    #faceSearch.facevalidate_redshift()
    #faceRekognition = FaceRekognition()
    #faceRekognition.rekognizeFace()

    return faceSearch.getModel()
