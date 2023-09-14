#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

# # job 만들기 

# # 분석가가 모델 올리기

# In[1]:


import boto3
import pymongo
import json


def aws_connection(service_name, aws_access_key_id, aws_secret_access_key, region_name = "ap-northeast-2", endpoint_url = ""):
    if service_name == 's3' : 
        if aws_access_key_id == '' or aws_secret_access_key == '': 
            cli = boto3.client('s3', region_name=region_name)
        else :
            cli = boto3.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)
            
    if service_name == 'ssm' : 
        if aws_access_key_id == '' or aws_secret_access_key == '': 
            cli = boto3.client('ssm', endpoint_url= endpoint_url, region_name=region_name)
        else :
            cli = boto3.client('ssm', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)
            
    
    if service_name == 'stepfunctions' : 
        if aws_access_key_id == '' or aws_secret_access_key == '': 
            cli = boto3.client('stepfunctions', region_name=region_name)
        else :
            cli = boto3.client('stepfunctions', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)
            
    return cli   


# In[2]:


def get_ssm( parameter_store_path, aws_access_key_id, aws_secret_access_key, endpoint_url, region_name ):
#     client = boto3.client('ssm')
    client = aws_connection('ssm', aws_access_key_id, aws_secret_access_key, region_name, endpoint_url  )
    
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


def mongodb_connection(  environment, collection_div, aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url, region_name = 'ap-northeast-2' ) : 
    
    
    print(  environment  )
    
    SSM_PATH = ssm_path.format(environment)
    print( SSM_PATH )
    CONN_INFO = get_ssm( SSM_PATH,  aws_access_key_id, aws_secret_access_key, endpoint_url, region_name )
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



# # send_model_to_sagemaker():

# In[15]:

# In[ ]:





# In[ ]:





# # config 생성

# In[ ]:




def create_config_train_image( environment, model_id, endpoint_url,  aws_access_key_id = '', aws_secret_access_key = '', ssm_path = '/mlops/{0}/database/mongo', region_name = 'ap-northeast-2'  ) : 
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

                        'extract_local_script_path' : r'./script/k121/density/sql.txt',
                        'transform_local_script_path' : r'./script/k121/density/k121_density_transform.py',
                        'train_local_script_path' : r'./script/k121/density/k121_density.py',
        
                        'endpoint_local_script_path' : r'./script/k121/density/k121_sf_api.py',

                        # 학습 - 디폴트
                        'image_name' : 'autogluon',
                        'transform_image_name' : 'scikit-learn'
        
                        
        

                    }
    
    
    
    
    collection = mongodb_connection(environment, 'list', aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url ) 
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
        user_image_config['mongo_ssm'] = ssm_path.format( environment )
        return user_image_config


# # 배포

# In[36]:


def create_init_maker(config, bucket, script_path, sourcedir_train_path,  environment):
    insert_info = {}
    
    
    current_time = datetime.datetime.now()
    job_date = str(current_time).replace("-", "").replace(" ", "/").replace(":", "").replace(".", "/")
    create_date, create_time, create_millisecond = job_date.split("/")
    
    model_id   = config['model_id']
    model_name = config['model_name']
    script_ver = config['script_ver']
    mongo_ssm  = config['mongo_ssm']

    # config copy
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
    insert_info['init']['mongo_ssm'] = mongo_ssm

    # return step function value 
    insert_info['init']['tar_to_s3_bucket'] = bucket
    insert_info['init']['tar_to_s3_file_path'] = script_path

    insert_info['init']['script_ver'] = script_ver
    insert_info['init']['sourcedir_train_path']     = "./{0}/{1}".format( sourcedir_train_path, config['train_local_script_path'].split('/')[-1] )
    insert_info['init']['sagemaker_model_id']       = '{0}-{1}-{2}-{3}'.format( model_name, create_date, create_time, create_millisecond )
    insert_info['init']['bucket']                   = bucket
    insert_info['init']['======']                   = "###############추출###############"
    insert_info['init']['script_path']              = '{0}/{1}/{2}/script'.format( environment, model_name, str(script_ver) ) 
    insert_info['init']['extract_script_path']      =  config['extract_local_script_path'].split('/')[-1]
    insert_info['init']['transform_script_path']    =  config['transform_local_script_path'].split('/')[-1]
    insert_info['init']['create_model_script_path'] =  config['train_local_script_path'].split('/')[-1]
    insert_info['init']['endpoint_script_path']     =  config['endpoint_local_script_path'].split('/')[-1]

    insert_info['init']['endp_name'] = config['endp_name']
    insert_info['init']['endp_config_mode'] = config['endp_config_mode']
    insert_info['init']['max_concurrency'] = config['max_concurrency']
    insert_info['init']['mem_size'] = config['mem_size']
    
    return insert_info


# In[32]:




import boto3
import tarfile
import os.path
import pymongo
import datetime
import uuid





def upload_s3_ml_script(environment, config, endpoint_url = None, aws_access_key_id = '', aws_secret_access_key = '', stepfunction_job = 'mlops_test_step_01',  bucket = 'dwe-mlops-hub-repository',  ssm_path = '/mlops/{0}/database/mongo', region_name = 'ap-northeast-2'   ):
        
    
    if config['deploy'] == False : 
        print( "야! 꺼져!")
        return {'state': '꺼져' }

    
    print("Make Tar File")
    
    file_list  = [config['extract_local_script_path'], config['transform_local_script_path'], config['train_local_script_path'], config['endpoint_local_script_path']]
    model_name = config['model_name']
    model_id   = config['model_id']
    user_id    = config['user_id']
    
    try :
        
        
        # local 소스 코드를 tar로 묶어 준다
        tmp_path = './sourcedir.tar.gz'
        sourcedir_train_path = 'script'
        with tarfile.open(tmp_path, 'w:gz') as script_tar:
            for path_file in file_list :
                if path_file == 'pass':
                    # 과거 이력을 가지고 와야 함. 
                    pass
                else : 
                    print( path_file )
                    file_name = path_file.split("/")[-1]
                    print( file_name )
                    script_tar.add(path_file, arcname='/{0}/{1}'.format(sourcedir_train_path, file_name))
          
        print("Fin Tar File")
        
        insert_chk = False 

        chk_model = ''
        
        # 해당 버전을 가지고 온다. 
        collection = mongodb_connection(environment, 'log', aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url ) 
        
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

        
        
        # config chk 한다. 
        
        
        
        
        # # S3 Client 생성
        s3 = aws_connection('s3', aws_access_key_id, aws_secret_access_key, region_name )
        script_path = '{0}/{1}/{2}/local/{3}'.format(environment, model_name, script_ver,'sourcedir.tar.gz')
        ###
        print("Start Upload S3")
        
        
        # 파일을 올린다
        res = s3.upload_file(tmp_path, bucket, script_path, ExtraArgs={'ContentType': 'application/x-gzip'})
        print("Fin upload S3")
        
        os.remove(tmp_path)
        
        
        insert_info = create_init_maker(config, bucket, script_path, sourcedir_train_path, environment)
       
        
        print( insert_info )
        
        # Step Functions 클라이언트 생성
        client = aws_connection('stepfunctions', aws_access_key_id, aws_secret_access_key, region_name)

        # Step Function 함수 ARN 가져오기
        response = client.list_state_machines()
        state_machines = response['stateMachines']
        for state_machine in state_machines:
            if state_machine['name'] == stepfunction_job:
                state_machine_arn = state_machine['stateMachineArn']

        print( state_machine_arn ) 
        
        response = client.start_execution(
            stateMachineArn = state_machine_arn,
            name = str(uuid.uuid1()),
            input = json.dumps(insert_info)
        )
        
        
        print( response['executionArn'] ) 
        
        
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
            
    
    if user_image_config['extract_local_script_path'] == 'pass'  and user_image_config['transform_local_script_path'] == 'pass' and user_image_config['train_local_script_path'] == 'pass' and user_image_config['endpoint_local_script_path'] == 'pass': 
        print("\x1b[31m\"{0}\"\x1b[0m".format( "전부 extract, transform, train, endpoint를 전부 패스하시면, 배포가 불필요합니다. "))
        status = False
    
    
    user_image_config['deploy'] = status
    return user_image_config
    


# In[39]:


def get_config_train_image(environment, model_id, script_ver, endpoint_url = None, aws_access_key_id = '', aws_secret_access_key = '', ssm_path = '/mlops/{0}/database/mongo' ) : 

    collection = mongodb_connection(environment, 'log', aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url ) 
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
            
            if key in ['model_id', 'model_name', 'endp_name', 'endp_config_mode',  'max_concurrency', 'mem_size', 'script_ver', 'deploy', 'mongo_ssm']:  
                user_image_config[key] = val
            else :
                change_value = input( '{0} : {1} '.format(key, val) )
                if change_value == '':
                    user_image_config[key] = val
                else : 
                    user_image_config[key] = change_value
                    
        user_image_config = job_excute_msg( job_flow, user_image_config )

        return user_image_config

     


# # 자동으로 돌리기

# In[44]:


# 배포 여부를 업데이트 해줘야 함

def auto_excute(environment, model_id, endpoint_url = None, aws_access_key_id = '', aws_secret_access_key = '', stepfunction_job = 'mlops_test_step_01',  bucket = 'dwe-mlops-hub-repository',  ssm_path = '/mlops/{0}/database/mongo', region_name = 'ap-northeast-2'  ):

    collection = mongodb_connection(environment, 'log', aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url, region_name ) 
    print( {'model_id' : model_id } )
    data = list( collection.find({'model_id' : model_id , 'latest' : True}, { '_id' : 0}).sort([("_id", pymongo.DESCENDING)]).limit(1) )  
    
    if len( data ) == 0 :
        print( "해당 작업의 버전은 존재하지 않습니다.")
        return []
    else : 
        
        job_flow = job_flow_meg( data )
        
        image_config = data[0]['local']
#         print( image_config )
      
#         image_config['script_ver'] = image_config['script_ver'] 
        image_config['user_id']    = 'auto'
        image_config['user_name']  = 'auto'
                    
        image_config = job_excute_msg( job_flow, image_config )
        
        
        #############
        
        get_last_version_list = list( collection.find({'model_id' : model_id }, {'script_ver' : 1, '_id' : 0}).sort([("_id", pymongo.DESCENDING)]).limit(1) )
        get_last_version = get_last_version_list[0]['script_ver'] + 1 
        
        
        script_path = '{0}/{1}/{2}/local/{3}'.format(environment, image_config['model_name'], get_last_version, 'sourcedir.tar.gz')
        
        get_deploy_version = image_config['script_ver'] 
        image_config['script_ver']  = get_last_version
        
        insert_info = create_init_maker(image_config, bucket, script_path, 'script',  environment)
        
        
        
        print( insert_info )
        
        ###############################################
        
        
        s3 = aws_connection('s3', aws_access_key_id, aws_secret_access_key, region_name)
        src_key = '{0}/{1}/{2}/local/sourcedir.tar.gz'.format( environment, image_config['model_name'], str(get_deploy_version) ) 
        print( src_key )
        dst_key = '{0}/{1}/{2}/local/sourcedir.tar.gz'.format( environment, image_config['model_name'], str(get_last_version) ) 
        print( dst_key )
        s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': src_key}, Key=dst_key)
        
        
        
        
        
        # Step Functions 클라이언트 생성
        client = aws_connection('stepfunctions', aws_access_key_id, aws_secret_access_key, region_name)

        # Step Function 함수 ARN 가져오기
        response = client.list_state_machines()
        state_machines = response['stateMachines']
        for state_machine in state_machines:
            if state_machine['name'] == stepfunction_job:
                state_machine_arn = state_machine['stateMachineArn']

        print( state_machine_arn ) 

        response = client.start_execution(
            stateMachineArn = state_machine_arn,
            name = str(uuid.uuid1()),
            input = json.dumps(insert_info)
        )
        
#         collection.insert_one( insert_info ) 
        
        collection.insert_one( insert_info ) 
        
        

        return insert_info

     

