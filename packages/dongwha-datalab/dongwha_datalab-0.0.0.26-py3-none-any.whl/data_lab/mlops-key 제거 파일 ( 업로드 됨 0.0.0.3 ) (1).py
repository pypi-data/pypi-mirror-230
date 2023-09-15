#!/usr/bin/env python
# coding: utf-8

# # job 만들기 

# # 분석가가 모델 올리기

# In[1]:


import boto3
import pymongo
import json


def aws_connection(service_name, aws_access_key_id, aws_secret_access_key):
    if service_name == 's3' : 
        if aws_access_key_id == '' or aws_secret_access_key == '': 
            cli = boto3.client('s3')
        else :
            cli = boto3.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key)
            
    if service_name == 'ssm' : 
        if aws_access_key_id == '' or aws_secret_access_key == '': 
            cli = boto3.client('ssm')
        else :
            cli = boto3.client('ssm', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key)
            
    
    if service_name == 'stepfunctions' : 
        if aws_access_key_id == '' or aws_secret_access_key == '': 
            cli = boto3.client('stepfunctions')
        else :
            cli = boto3.client('stepfunctions', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key)
            
    return cli   


# In[2]:


def get_ssm( parameter_store_path, aws_access_key_id, aws_secret_access_key):
#     client = boto3.client('ssm')
    client = aws_connection('ssm', aws_access_key_id, aws_secret_access_key )
    
    if type(parameter_store_path) != list :
        parameter_store_path = [parameter_store_path]
        
    parameter = client.get_parameters(Names = parameter_store_path, WithDecryption=True)
    #print( parameter )
        
    # 값을 뽑아온다. 
    parameter_result = []
    if len(parameter['Parameters']) == 0:
        pass
    elif len(parameter['Parameters']) != 0:
        for token_parameter in parameter['Parameters']:
            token_data = token_parameter['Value'].replace("'", '"') 
            parameter_value = json.loads( token_data )
            parameter_result.append(parameter_value)
    
    if len(parameter_result) == 1:
        return parameter_result[0]
    else :
        return parameter_result


# In[3]:


def mongodb_connection(  environment, collection_div, aws_access_key_id, aws_secret_access_key, ssm_path  ) : 
    
    
    print(  environment,  )
    print(  aws_access_key_id,  )
    print(  aws_secret_access_key,  )
    print( ssm_path )
    
    
    SSM_PATH = ssm_path.format(environment)
    print( SSM_PATH )
    CONN_INFO = get_ssm( SSM_PATH,  aws_access_key_id, aws_secret_access_key )
    MONGODB_HOST = CONN_INFO['host']
    MONGODB_PORT = CONN_INFO['port']
    DATABASE     = CONN_INFO['db_name']
    COLLECTION   = CONN_INFO['collection'][collection_div]
    conn = pymongo.MongoClient(MONGODB_HOST)
    db = conn[DATABASE]
    collection = db[COLLECTION]
    
    print( DATABASE )
    print( COLLECTION  )
    
    
    
    return collection


# In[4]:



def create_config_train_image( environment, model_id, aws_access_key_id = '', aws_secret_access_key = '', ssm_path = '/mlops/{0}/database/mongo' ) : 
    import datetime 
    
    print("""
    ###############################################
    ###############################################
    ############## create train image #############
    ###############################################
    ###############################################
    """)

    
    
    image_config = {
                        # 디폴트
                        'model_id' : 'uuid', 
                        'model_name' : 'mor_avg',
                        'endp_name' : "k121-qa-labcut-density-optimization-serverless-test111",
                        "endp_config_mode" : "serverless",
                        "max_concurrency" : 1,
                        "mem_size" : 2048,
        
                        'user_id' : 'D1234567',
                        'user_name' : '홍길동',
                        'comment' : '휨강도 평균 예측', 

                        'extract_local_script_path' : r'./script/sql.txt',
                        'transform_local_script_path' : r'./script/k121_transform.py',
                        'train_local_script_path' : r'./script/k121_density.py',
        
                        'endpoint_local_script_path' : r'./script/k121_sf_api.py',

                        # 학습 - 디폴트
                        'image_name' : 'autogluon',
                        'transform_image_name' : 'scikit-learn'
        
                        
        

                    }
    
    
    
    
    collection = mongodb_connection(environment, 'list', aws_access_key_id, aws_secret_access_key, ssm_path) 
    print( list( collection.find({}) ) ) 

    chk_model = ''
    for chk_model in collection.find({'job_id' : model_id}):
        print( chk_model )
        chk_model = chk_model
    
#     print( chk_model )
    
    if len(chk_model) == 0 : 
        return {'error' : '등록된 모델이 없습니다.'}
    else : 
        user_image_config = {}
        for key, val in image_config.items():
            if key == 'model_id': 
                user_image_config[key] = chk_model['job_id']
                print( "'model_id': ", user_image_config[key] )
            elif key == 'model_name': 
                user_image_config[key] = chk_model['job_name']
                print( "'model_name' : ", user_image_config[key] )
                
                
            elif key == 'endp_name': 
                user_image_config[key] = chk_model['endp_name']
                print( "'endp_name' : ", user_image_config[key] )
            elif key == 'endp_config_mode': 
                user_image_config[key] = chk_model['endp_config_mode']
                print( "'endp_config_mode' : ", user_image_config[key] )
            elif key == 'max_concurrency': 
                user_image_config[key] = chk_model['max_concurrency']
                print( "'max_concurrency' : ", user_image_config[key] )
            elif key == 'mem_size': 
                user_image_config[key] = chk_model['mem_size']
                print( "'mem_size' : ", user_image_config[key] )
                
            else : 
                change_value = input( '{0} : {1} '.format(key, val) )
                if change_value == '':
                    user_image_config[key] = val
                else : 
                    user_image_config[key] = change_value
        user_image_config['deploy'] = True
        return user_image_config


# # send_model_to_sagemaker():

# In[1]:


import boto3
import tarfile
import os.path
import pymongo
import datetime
import uuid



def upload_s3_ml_script(environment, config, aws_access_key_id = '', aws_secret_access_key = '', ssm_path = '/mlops/{0}/database/mongo'  ):
        
    
    if config['deploy'] == False : 
        print( "야! 꺼져!")
        return {'state': '꺼져' }

    
    print("Make Tar File")
    
    file_list  = [config['extract_local_script_path'], config['transform_local_script_path'], config['train_local_script_path'], config['endpoint_local_script_path']]
    model_name = config['model_name']
    model_id   = config['model_id']
    user_id    = config['user_id']
    
    try :
        
        # bucket = 'sagemaker-ap-northeast-2-646967793880'
        
        tmp_path = './sourcedir.tar.gz'
        sourcedir_train_path = 'script'
        with tarfile.open(tmp_path, 'w:gz') as script_tar:
            for path_file in file_list :
                if path_file == 'pass':
                    pass
                else : 
                    print( path_file )
                    file_name = path_file.split("/")[-1]
                    print( file_name )
                    script_tar.add(path_file, arcname='/{0}/{1}'.format(sourcedir_train_path, file_name))
          
        print("Fin Tar File")
        
        insert_chk = False 

        chk_model = ''
        
        
        collection = mongodb_connection(environment, 'log', aws_access_key_id, aws_secret_access_key, ssm_path ) 
        
        for chk_model in collection.find({'model_id' : model_id}, {'_id' : 0}).sort([("_id", pymongo.DESCENDING)]).limit(1):
            chk_model = chk_model
            print( "안타??")
        
        # 스크립트 버전을 관리한다. ( 최초 실행은 if문, 그외는 else)
        if len(chk_model) == 0:
            script_ver = 1
            config['script_ver'] = script_ver
            insert_chk = True 
            
        else : 
            # 정상 배포면 스크립트 버전을 올린다.
            if 'script_ver' not in config.keys():
                script_ver = chk_model['script_ver'] + 1
                config['script_ver'] = script_ver
                insert_chk = True 
            # 실패한 부분만 배포
            else : 
                script_ver = config['script_ver'] 
        
            
            
        current_time = datetime.datetime.now()
        job_date = str(current_time).replace("-", "").replace(" ", "/").replace(":", "").replace(".", "/")
        create_date, create_time, create_millisecond = job_date.split("/")
        
        
        # # S3 Client 생성
#         s3 = boto3.client('s3')
        s3 = aws_connection('s3', aws_access_key_id, aws_secret_access_key)
        
        script_path = '{0}/{1}/{2}/{3}'.format(environment, model_name, script_ver,'sourcedir.tar.gz')
        ###
        print("Start Upload S3")
        bucket = 'dwe-mlops-hub-repository'
        #ExtraArgs={'ContentType': 'text/x-python'} application/x-gzip"
        res = s3.upload_file(tmp_path, bucket, script_path, ExtraArgs={'ContentType': 'application/x-gzip'})
        print("Fin upload S3")
        
        os.remove(tmp_path)
        
        
        insert_info = {}
        
        insert_info['local'] = config.copy()
        
        # key 값 배정
        insert_info['model_id'] = model_id
        insert_info['model_name'] = model_name
        insert_info['script_ver'] = script_ver
        insert_info['endp_name'] = config['endp_name']
        insert_info['endp_config_mode'] = config['endp_config_mode']
        insert_info['max_concurrency'] = config['max_concurrency']
        insert_info['mem_size'] = config['mem_size']
        
        
        # 압축 해지 경로 관리
        insert_info['init'] = {}
        insert_info['init']['model_id'] = model_id
        insert_info['init']['model_name'] = model_name
        
        # return step function value 
        insert_info['init']['tar_to_s3_bucket'] = bucket
        insert_info['init']['tar_to_s3_file_path'] = script_path
        
        
        insert_info['init']['script_ver'] = script_ver
        insert_info['init']['sagemaker_model_id']       = '{0}-{1}-{2}-{3}'.format( model_name, create_date, create_time, create_millisecond )
        insert_info['init']['bucket']                   = bucket
        insert_info['init']['======']                   = "###############추출###############"
        insert_info['init']['script_path']              = '{0}/script/{1}/{2}'.format( environment, model_name, str(script_ver) ) 
        insert_info['init']['extract_script_path']      =  config['extract_local_script_path'].split('/')[-1]
        insert_info['init']['transform_script_path']    =  config['transform_local_script_path'].split('/')[-1]
        insert_info['init']['create_model_script_path'] =  config['train_local_script_path'].split('/')[-1]
        insert_info['init']['endpoint_script_path']     =  config['endpoint_local_script_path'].split('/')[-1]
        
        insert_info['init']['sourcedir_train_path'] =  "/{0}/{1}".format( sourcedir_train_path, config['train_local_script_path'].split('/')[-1] ) 
        
        insert_info['init']['endp_name'] = config['endp_name']
        insert_info['init']['endp_config_mode'] = config['endp_config_mode']
        insert_info['init']['max_concurrency'] = config['max_concurrency']
        insert_info['init']['mem_size'] = config['mem_size']
        
#         insert_info = config.copy()
        
        print( insert_info )
        
        
        client = aws_connection('stepfunctions', aws_access_key_id, aws_secret_access_key)
        response = client.start_execution(
            stateMachineArn='arn:aws:states:ap-northeast-2:646967793880:stateMachine:mlops_test_step_01',
            name=str(uuid.uuid1()),
            input=json.dumps(insert_info)
        )
        
        
        
        if insert_chk == True : 
            collection.insert_one( insert_info ) 
#         else :
#             collection.update_one({'model_id' : model_id, 'script_ver' : script_ver}, {'$set' : {'endp_name' : insert_info['endp_name'] , 'endp_config_mode' : insert_info['endp_config_mode'], 'max_concurrency' : insert_info['max_concurrency'], 'mem_size' : insert_info['mem_size'], 'init' : insert_info['init']} } )
        
        return {'state' : 'success', 'script_path' : script_path}
    
        
        
    except ValueError as e:
        print(e)
        return {'state' : 'error', 'explain' : e}


# # 이어 달리기

# In[37]:


def job_flow_meg( data ) : 
    job_flow = '아무것도 수행한 적이 없습니다.'
    if 'extract' in data[0] : 
        job_flow = '추출까지 성공했습니다.'

    if 'transform' in data[0] : 
        job_flow = '전처리까지 성공했습니다.'

    if 'train' in data[0] : 
        job_flow = '학습까지 성공했습니다.'


#     print( "현재 해당 작업은 " + job_flow )
    print("\x1b[31m\"{0}\"\x1b[0m".format(job_flow))
    print( "--------------------------------------------------------" )
    print( "--------------------------------------------------------" )
    print( "--------------------------------------------------------" )
    

    
    return job_flow


# In[38]:


def job_excute_msg( job_flow, user_image_config ) : 
    print( "--------------------------------------------------------" )
    print( "--------------------------------------------------------" )
    print( "--------------------------------------------------------" )
    
    
    
    status = True 
    if job_flow == '아무것도 수행한 적이 없습니다.':
        if user_image_config['extract_local_script_path'] == 'pass' : 
            print( 'extract_local_script_path 작업을 pass 할 수 없습니다.')
            status = False 

        if user_image_config['transform_local_script_path'] == 'pass' : 
            print( 'transform_local_script_path 작업을 pass 할 수 없습니다.')
            status = False 

        if user_image_config['train_local_script_path'] == 'pass' : 
            print( 'train_local_script_path 작업을 pass 할 수 없습니다.')
            status = False 


    elif job_flow == '추출까지 성공했습니다.' :
        if user_image_config['transform_local_script_path'] == 'pass' : 
            print( 'transform_local_script_path 작업을 pass 할 수 없습니다.')
            status = False 

        if user_image_config['train_local_script_path'] == 'pass' : 
            print( 'train_local_script_path 작업을 pass 할 수 없습니다.')
            status = False 


    elif job_flow == '전처리까지 성공했습니다.' :
        if user_image_config['train_local_script_path'] == 'pass' : 
            print( 'train_local_script_path 작업을 pass 할 수 없습니다.')
            status = False 
            
    user_image_config['deploy'] = status
    return user_image_config
    


# In[39]:


def get_config_train_image(environment, model_id, script_ver, aws_access_key_id = '', aws_secret_access_key = '', ssm_path = '/mlops/{0}/database/mongo' ) : 

    collection = mongodb_connection(environment, 'log', aws_access_key_id, aws_secret_access_key, ssm_path ) 
    print( {'model_id' : model_id, 'script_ver' : script_ver} )
    data = list( collection.find({'model_id' : model_id, 'script_ver' : script_ver}, { '_id' : 0}) ) 
    
    if len( data ) == 0 :
        print( "해당 작업의 버전은 존재하지 않습니다.")
        return []
    else : 
        
        job_flow = job_flow_meg( data )
        
        image_config = data[0]['local']
#         print( image_config )
      
        user_image_config = {}
        for key, val in image_config.items():
            
            if key in ['model_id', 'model_name', 'endp_name', 'endp_config_mode',  'max_concurrency', 'mem_size', 'endpoint_local_script_path', 'script_ver', 'deploy']:  
                user_image_config[key] = val
            else :
                change_value = input( '{0} : {1} '.format(key, val) )
                if change_value == '':
                    user_image_config[key] = val
                else : 
                    user_image_config[key] = change_value
                    
        user_image_config = job_excute_msg( job_flow, user_image_config )

        return user_image_config

     


# In[ ]:





# In[ ]:




