import json
import tarfile
import datetime
import uuid

import boto3
import pymongo
import panel as pn
from IPython.core.display import HTML

from ipyfilechooser import FileChooser

class mlops():
    

    # 패널
    P_USER_ID = None
    P_MODEL_INFO = None
    
    P_TRIAN_CONTAINER = None
    P_TRANSFORM_CONTAINER = None
    
    P_STEP_FUNCTION = None
    P_S3_NAME = None
    
    P_EXTRACT_FILE_PATH = None
    P_TRANSFORM_FILE_PATH = None
    P_TRAIN_FILE_PATH = None
    P_ENDPOINT_FILE_PATH = None
    
    P_MLOPS_STATUS = None
    P_DEPLOY_BUTTON = None
    P_DEPLOY_COMMENT = None
    P_DEPLOY_LOCKER = None
    

    
    
    
    # 데이터 
    G_USER_ID_DIST =  {}
    G_MODEL_LIST = []
    
    G_TRIAN_CONTAINER_LIST = []
    G_TRIAN_CONTAINER_FULL_DICT = {}
    
    
    G_MODEL_CONTAINER_LIST = []
    G_MODEL_CONTAINER_FULL_DICT = {}
    
#     [
#         ['autogluon', '0.6.2', 'cpu', 'py38'],
#         ['autogluon', '0.6.2', 'cpu', 'py39'],
#         ['autogluon', '0.7.0', 'cpu', 'py38'],
#         ['autogluon', '0.7.0', 'cpu', 'py39']
#     ]
    G_TRANSFORM_CONTAINER_LIST = []#['scikit-learn']
    G_TRANSFORM_CONTAINER_FULL_DICT = {}
    
    G_STEP_FUNCTION_DIST = {'물성실험예측' :  "sf_qa_mlops_labcut_full_piplines_step_job"}
    G_S3_NAME_LIST = ["dwe-mlops-hub-repository"]
    G_AWS_ACCESS_KEY = None
    G_AWS_SECRET_KEY = None
    G_ENVIRONMENT = None
    G_SSM_MONGO_PATH = None
    G_MATCH_JOB_DIST = {}
    
    G_FILE_EDITOR = 'PANEL'
    
    
    
    def __init__(self, environment, LOCAL_G_FILE_PATH = '.', aws_access_key_id = None, aws_secret_access_key = None): 
        pn.extension()
        
        self.G_AWS_ACCESS_KEY = aws_access_key_id
        self.G_AWS_SECRET_KEY = aws_secret_access_key
        
        self.LOCAL_G_FILE_PATH = LOCAL_G_FILE_PATH
        
            
        
        if 'PROD' in environment.upper():
            self.G_SSM_MONGO_PATH = '/mlops/prod/database/mongo'
            
            
        elif 'DEV' in environment.upper():
            
            if 'SIMPLE' in environment.upper(): 
                self.G_FILE_EDITOR = 'FileChooser'
                
            self.G_SSM_MONGO_PATH = '/mlops/dev/database/mongo'
            self.G_ENVIRONMENT = environment.lower().replace('_simple', '')
            self.G_ENVIRONMENT = self.G_ENVIRONMENT.replace('simple_', '')
            self.G_ENVIRONMENT = self.G_ENVIRONMENT.replace('simple', '')
            
                
            
            model_list = self.mongodb_connection('dev', 'list', self.G_AWS_ACCESS_KEY, self.G_AWS_SECRET_KEY, self.G_SSM_MONGO_PATH, '' )
            
            self.G_MODEL_LIST = []
            for row in model_list.find({}, {'_id' : 0}):
                job_name = row['job_name']
                job_id = row['job_id']
                self.G_MATCH_JOB_DIST[job_name] = row
                self.G_MODEL_LIST.append( job_name )
                
            
            model_user = self.mongodb_connection('dev', 'user', self.G_AWS_ACCESS_KEY, self.G_AWS_SECRET_KEY, self.G_SSM_MONGO_PATH, '' )
            for row in model_user.find({}, {'_id' : 0}):
                self.G_USER_ID_DIST = row
                
                
            
            # image_spec    
            model_image_spec = self.mongodb_connection('dev', 'image_spec', self.G_AWS_ACCESS_KEY, self.G_AWS_SECRET_KEY, self.G_SSM_MONGO_PATH, '' )
            for row in model_image_spec.find({},{'_id' : 0}) :
                container_id = '{0}-{1}-{2}-py{3}'.format(row['framework_name'],row['framework_version'], row['hardware'],row['python_version'] )
                if row['job_type'] == 'training' :
                    #G_TRIAN_CONTAINER_LIST
                    self.G_TRIAN_CONTAINER_LIST.append(container_id)
                    self.G_TRIAN_CONTAINER_FULL_DICT[container_id]= row
                elif row['job_type'] == 'transform' : 
                    #G_TRANSFORM_CONTAINER_LIST
                    self.G_TRANSFORM_CONTAINER_LIST.append(container_id)
                    self.G_TRANSFORM_CONTAINER_FULL_DICT[container_id]= row
                elif row['job_type'] == 'inference' :
                    #G_MODEL_CONTAINER_LIST
                    self.G_MODEL_CONTAINER_LIST.append(container_id)
                    self.G_MODEL_CONTAINER_FULL_DICT[container_id]= row

            
            
        
        
    
    
    # aws 통합 접속 정보이다. 
    def aws_connection(self, service_name, aws_access_key_id, aws_secret_access_key, region_name = "ap-northeast-2", endpoint_url = ""):
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
    
    
    
    
    # ssm에서 데이터를 가지고 온다. 
    def get_ssm(self, parameter_store_path, aws_access_key_id, aws_secret_access_key, endpoint_url, region_name ):
        client =  self.aws_connection('ssm', aws_access_key_id, aws_secret_access_key, region_name, endpoint_url  )

        if type(parameter_store_path) != list :
            parameter_store_path = [parameter_store_path]

        parameter = client.get_parameters(Names = parameter_store_path, WithDecryption=True)


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
        
        
    
    
    # 몽고디비를 접속해주는 함수이다. 
    def mongodb_connection( self, environment, collection_div, aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url, region_name = 'ap-northeast-2' ) : 

        SSM_PATH = ssm_path.format(environment)
        CONN_INFO = self.get_ssm( SSM_PATH,  aws_access_key_id, aws_secret_access_key, endpoint_url, region_name )
        MONGODB_HOST = CONN_INFO['host']
        MONGODB_PORT = CONN_INFO['port']
        DATABASE     = CONN_INFO['db_name']
        COLLECTION   = CONN_INFO['collection'][collection_div]
        conn = pymongo.MongoClient(MONGODB_HOST)
        db = conn[DATABASE]
        collection = db[COLLECTION]


        return collection
    
    
    
    

    
    
    # mlops의 config를 정리해서 만들어 준다. 
    def show_config(self) : 
        
        config_user_id   = self.P_USER_ID.value
        config_user_name = self.G_USER_ID_DIST[config_user_id]

        config_extract_script_path = 'pass'
        config_transform_script_path = 'pass'
        config_train_script_path = 'pass'
        config_endpoint_script_path = 'pass'
        
        if self.G_FILE_EDITOR == 'PANEL' : 
            if len(self.P_EXTRACT_FILE_PATH.value) != 0:
                config_extract_script_path = self.P_EXTRACT_FILE_PATH.value[0].replace('\\', '/')

            if len(self.P_TRANSFORM_FILE_PATH.value) != 0:
                config_transform_script_path = self.P_TRANSFORM_FILE_PATH.value[0].replace('\\', '/')

            if len(self.P_TRAIN_FILE_PATH.value) != 0:
                config_train_script_path = self.P_TRAIN_FILE_PATH.value[0].replace('\\', '/')

            if len(self.P_ENDPOINT_FILE_PATH.value) != 0:
                config_endpoint_script_path = self.P_ENDPOINT_FILE_PATH.value[0].replace('\\', '/')
                
        elif self.G_FILE_EDITOR == 'FileChooser' :
            if len(self.P_EXTRACT_FILE_PATH.value) != 0:
                config_extract_script_path = self.P_EXTRACT_FILE_PATH.value.replace('\\', '/')

            if len(self.P_TRANSFORM_FILE_PATH.value) != 0:
                config_transform_script_path = self.P_TRANSFORM_FILE_PATH.value.replace('\\', '/')

            if len(self.P_TRAIN_FILE_PATH.value) != 0:
                config_train_script_path = self.P_TRAIN_FILE_PATH.value.replace('\\', '/')

            if len(self.P_ENDPOINT_FILE_PATH.value) != 0:
                config_endpoint_script_path = self.P_ENDPOINT_FILE_PATH.value.replace('\\', '/')
                            
            
            

        config_trian_container     = self.P_TRIAN_CONTAINER.value
        config_transform_container = self.P_TRANSFORM_CONTAINER.value

        config_model_name = self.P_MODEL_INFO.value
        
        
        config_model_id   = self.G_MATCH_JOB_DIST[config_model_name]['job_id']
        ## 추론 Config 설정 부분
        config_endp_name  = self.G_MATCH_JOB_DIST[config_model_name]['endp_name']
#         config_endp_config_mode = self.G_MATCH_JOB_DIST[config_model_name]['endp_config_mode']
        
        ## 모델 이미지 설정 부분
        transform_container_id = self.P_TRANSFORM_CONTAINER.value
        transform_container_list = self.G_TRANSFORM_CONTAINER_FULL_DICT[transform_container_id]
        
        train_container_id = self.P_TRIAN_CONTAINER.value
        train_container_list = self.G_TRIAN_CONTAINER_FULL_DICT[train_container_id]
        
        inference_container_list = self.G_MODEL_CONTAINER_FULL_DICT[train_container_id]

        config_comment = self.P_DEPLOY_COMMENT.value


        config =  {
             'model_id': config_model_id,
             'model_name': config_model_name,
             'endp_name': config_endp_name,
#              'endp_config_mode': config_endp_config_mode,
#              'max_concurrency': 1,
#              'mem_size': 2048,
             'user_id': config_user_id,
             'user_name': config_user_name,
             'comment': config_comment,
             'extract_local_script_path': config_extract_script_path,
             'transform_local_script_path': config_transform_script_path,
             'train_local_script_path': config_train_script_path,
             'endpoint_local_script_path': config_endpoint_script_path,
             'image_name': config_trian_container,
             'transform_image_name': config_transform_container,
             'deploy': True,
             'mongo_ssm': self.G_SSM_MONGO_PATH,
             'train_image_spec' : train_container_list,
             'transform_image_spec' : transform_container_list,
             'inference_image_spec' : inference_container_list
            } 



        return config
    
    
    
    
    def create_init_maker(self, config, bucket, script_path, sourcedir_train_path,  environment):
        insert_info = {}


        current_time = datetime.datetime.now()
        job_date = str(current_time).replace("-", "").replace(" ", "/").replace(":", "").replace(".", "/")
        create_date, create_time, create_millisecond = job_date.split("/")

        model_id   = config['model_id']
        model_name = config['model_name']
        script_ver = config['script_ver']
        mongo_ssm  = config['mongo_ssm']
        transform_image_spec = config['transform_image_spec']
        train_image_spec = config['train_image_spec']
        inference_image_spec = config['inference_image_spec']

        # config copy
        insert_info['local'] = config.copy()

        # key 값 배정
        insert_info['model_id'] = model_id
        insert_info['model_name'] = model_name
        insert_info['script_ver'] = script_ver
        insert_info['org_script_ver'] = script_ver
        insert_info['transform_image_spec'] = transform_image_spec
        insert_info['train_image_spec'] = train_image_spec
        insert_info['inference_image_spec'] = inference_image_spec
        insert_info['endp_name'] = config['endp_name']
#         insert_info['endp_config_mode'] = config['endp_config_mode']
#         insert_info['max_concurrency'] = config['max_concurrency']
#         insert_info['mem_size'] = config['mem_size']



        # 압축 해지 경로 관리
        insert_info['init'] = {}
        insert_info['init']['model_id'] = model_id
        insert_info['init']['model_name'] = model_name
        insert_info['init']['mongo_ssm'] = mongo_ssm
        insert_info['init']['transform_image_spec'] = transform_image_spec
        insert_info['init']['train_image_spec'] = train_image_spec
        insert_info['init']['inference_image_spec'] = inference_image_spec

        # return step function value 
        insert_info['init']['tar_to_s3_bucket'] = bucket
        insert_info['init']['tar_to_s3_file_path'] = script_path

        insert_info['init']['script_ver'] = script_ver
        insert_info['init']['org_script_ver'] = script_ver
        insert_info['init']['sourcedir_train_path']     = "./{0}/{1}".format( sourcedir_train_path, config['train_local_script_path'].split('/')[-1] )
        insert_info['init']['sagemaker_model_id']       = '{0}-{1}-{2}-{3}'.format( model_name, create_date, create_time, create_millisecond )
        insert_info['init']['bucket']                   = bucket
        insert_info['init']['======']                   = "###############추출###############"
        insert_info['init']['script_path']              = '{0}/{1}/{2}/script'.format( environment, model_name, str(script_ver) ) 
        insert_info['init']['extract_script_path']      =  config['extract_local_script_path'].split('/')[-1]
        insert_info['init']['transform_script_path']    =  config['transform_local_script_path'].split('/')[-1]
        insert_info['init']['create_model_script_path'] =  config['train_local_script_path'].split('/')[-1]
        insert_info['init']['endpoint_script_path']     =  config['endpoint_local_script_path'].split('/')[-1]

#         insert_info['init']['endp_name'] = config['endp_name']
#         insert_info['init']['endp_config_mode'] = config['endp_config_mode']
#         insert_info['init']['max_concurrency'] = config['max_concurrency']
#         insert_info['init']['mem_size'] = config['mem_size']

        return insert_info

    
    

    def upload_s3_ml_script(self, environment, config, endpoint_url = None, aws_access_key_id = '', aws_secret_access_key = '', stepfunction_job = 'mlops_test_step_01',  bucket = 'dwe-mlops-hub-repository',  ssm_path = '/mlops/{0}/database/mongo', region_name = 'ap-northeast-2'   ):


        if config['deploy'] == False : 
            return {'msg' : '현재 config는 배포가 불가능 조건입니다.', 'status' : 'danger' } 


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
                        script_tar.add(path_file, arcname='/{0}/{1}'.format(sourcedir_train_path, file_name))


            insert_chk = False 

            chk_model = ''

            # 해당 버전을 가지고 온다. 
            collection = self.mongodb_connection(environment, 'log', aws_access_key_id, aws_secret_access_key, ssm_path, endpoint_url ) 

            for chk_model in collection.find({'model_id' : model_id}, {'_id' : 0}).sort([("_id", pymongo.DESCENDING)]).limit(1):
                chk_model = chk_model


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

                    if config['extract_local_script_path'].upper() == "PASS":
                        return {'msg' : "extract_script_path 의 값이 누락 되었습니다.", 'status' : 'danger' } 

                    if config['transform_local_script_path'].upper() == "PASS":
                        return {'msg' : "transform_script_path 의 값이 누락 되었습니다.", 'status' : 'danger' } 

                    if config['train_local_script_path'].upper() == "PASS":
                        return {'msg' : "train_script_path 의 값이 누락 되었습니다.", 'status' : 'danger' } 

                    if config['endpoint_local_script_path'].upper() == "PASS":
                        return {'msg' : "endpoint_script_path 의 값이 누락 되었습니다.", 'status' : 'danger' } 


                # 실패한 부분만 배포
                else : 
                    script_ver = config['script_ver'] 


            # # S3 Client 생성
            s3 = self.aws_connection('s3', aws_access_key_id, aws_secret_access_key, region_name )
            script_path = '{0}/{1}/{2}/local/{3}'.format(environment, model_name, script_ver,'sourcedir.tar.gz')
        

            # 파일을 올린다
            res = s3.upload_file(tmp_path, bucket, script_path, ExtraArgs={'ContentType': 'application/x-gzip'})
            print("Fin upload S3")


            insert_info = self.create_init_maker(config, bucket, script_path, sourcedir_train_path, environment)

            # Step Functions 클라이언트 생성
            client =  self.aws_connection('stepfunctions', aws_access_key_id, aws_secret_access_key, region_name)

            # Step Function 함수 ARN 가져오기
            response = client.list_state_machines()
            state_machines = response['stateMachines']
            print( stepfunction_job )
            for state_machine in state_machines:
                if state_machine['name'] == stepfunction_job:
                    state_machine_arn = state_machine['stateMachineArn']


            response = client.start_execution(
                stateMachineArn = state_machine_arn,
                name = str(uuid.uuid1()),
                input = json.dumps(insert_info)
            )

            if insert_chk == True : 
                collection.insert_one( insert_info ) 
    #         else :
    #             collection.update_one({'model_id' : model_id, 'script_ver' : script_ver}, {'$set' : {'endp_name' : insert_info['endp_name'] , 'endp_config_mode' : insert_info['endp_config_mode'], 'max_concurrency' : insert_info['max_concurrency'], 'mem_size' : insert_info['mem_size'], 'init' : insert_info['init']} } )

            return {'msg' : "sagemaker로 해당 파일을 전송했습니다.", 'status' : 'success' ,'executionArn' :  response['executionArn']} 

        except Exception  as e:
            return {'msg' : '[문법에러 추정] : ' + str(e), 'status' : 'danger' } 
    
    
    
    
    
    # 패널 선언 부분
    def main_display_config(self) : 
        
        self.P_USER_ID             = pn.widgets.Select(name='사번', options = list(self.G_USER_ID_DIST.keys()) ) 
        self.P_MODEL_INFO          = pn.widgets.Select( options = self.G_MODEL_LIST )
        
        
        self.P_TRIAN_CONTAINER     = pn.widgets.Select(name='학습 컨터이너', options = self.G_TRIAN_CONTAINER_LIST )
        self.P_TRANSFORM_CONTAINER = pn.widgets.Select(name='전처리 컨테이너', options = self.G_TRANSFORM_CONTAINER_LIST )
        
        self.P_STEP_FUNCTION       = pn.widgets.Select(name='mlops 선택', options=list(self.G_STEP_FUNCTION_DIST.keys()) )
        self.P_S3_NAME             = pn.widgets.Select(name='버킷 이름', options= self.G_S3_NAME_LIST )
        
        
        
        
        if self.G_FILE_EDITOR == 'PANEL' : 
            self.P_EXTRACT_FILE_PATH   = pn.widgets.FileSelector(self.LOCAL_G_FILE_PATH )
            self.P_TRANSFORM_FILE_PATH = pn.widgets.FileSelector(self.LOCAL_G_FILE_PATH )
            self.P_TRAIN_FILE_PATH     = pn.widgets.FileSelector(self.LOCAL_G_FILE_PATH )
            self.P_ENDPOINT_FILE_PATH  = pn.widgets.FileSelector(self.LOCAL_G_FILE_PATH )
        elif self.G_FILE_EDITOR == 'FileChooser' : 
            self.P_EXTRACT_FILE_PATH   = FileChooser('.')
            self.P_TRANSFORM_FILE_PATH = FileChooser('.')
            self.P_TRAIN_FILE_PATH     = FileChooser('.')
            self.P_ENDPOINT_FILE_PATH  = FileChooser('.')
        
        
        
        self.P_MLOPS_STATUS   = pn.pane.Alert("배포 준비과 완료되면, 아래 버튼을 클릭해 주세요", alert_type='primary')
        
        
        self.P_DEPLOY_BUTTON  = pn.widgets.Button(name='Click me', button_type='primary')
        
        
        self.P_DEPLOY_COMMENT = pn.widgets.TextInput(value='comment')
#         self.P_DEPLOY_LOCKER = pn.widgets.TextInput(value='Ready')
        
        

    
    
    

    
    
    
    # mlops 메인 화면이다. 
    # 해당 화면의 역할은 show_config의 들어갈 데이터를 만들어 낸다. 
    def main_display(self) :
        def d(event):
            
            # 중복 배포 장금장치


            self.P_DEPLOY_BUTTON.disabled = True



            # 클릭 이벤트 시 대기 상태 표시 
            self.P_MLOPS_STATUS.object = """[실행횟수 : {0}] \n 재클릭 하지 마세요. 배포 작업을 진행중입니다. """.format(self.P_DEPLOY_BUTTON.clicks)
            self.P_MLOPS_STATUS.alert_type = 'warning'

            import time
            time.sleep(2)


            # 실패 시 해당 에러 메시지 전송
            chk_upload_s3_ml_script =  {'msg' : "알수없는 에러가 발생했습니다.", 'status' : 'danger' }

            try : 
                config = self.show_config()
                chk_upload_s3_ml_script = self.upload_s3_ml_script(
                                                            environment = self.G_ENVIRONMENT,
                                                            config = config,
                                                            endpoint_url = None, 
                                                            aws_access_key_id = self.G_AWS_ACCESS_KEY,
                                                            aws_secret_access_key = self.G_AWS_SECRET_KEY, 

                                                            stepfunction_job = self.G_STEP_FUNCTION_DIST[ self.P_STEP_FUNCTION.value ],  
                                                            bucket = self.P_S3_NAME.value,  
                                                            ssm_path = self.G_SSM_MONGO_PATH, 
                                                            region_name = 'ap-northeast-2'   
                                                           )

                ###
                ###
            except  Exception as e: 
                chk_upload_s3_ml_script = {'msg' : '[문법에러 추정] : ' + str(e), 'status' : 'danger' }


            # 상태 업데이트
            self.P_MLOPS_STATUS.object = chk_upload_s3_ml_script['msg']
            self.P_MLOPS_STATUS.alert_type = chk_upload_s3_ml_script['status']


            self.P_DEPLOY_BUTTON.disabled = False
            
        
        self.main_display_config()
        
        display(HTML('<h1>1. 사용자 정보</h1>'))
        display( pn.Row( self.P_USER_ID ) ) 

        display(HTML('<h1>2. 모델 이름 선택</h1>'))
        display( pn.Row( self.P_MODEL_INFO ) ) 

        display(HTML('<h1>3. MLOPS 정보 선택</h1>'))
        display( pn.Row( self.P_TRANSFORM_CONTAINER, self.P_TRIAN_CONTAINER ) ) 
        display( pn.Row( self.P_STEP_FUNCTION, self.P_S3_NAME ) ) 

        display(HTML('<h1>4. 추출</h1>'))
        display( self.P_EXTRACT_FILE_PATH )
        display(HTML('<h1>5. 전처리</h1>'))
        display( self.P_TRANSFORM_FILE_PATH )
        display(HTML('<h1>6. 학습</h1>'))
        display( self.P_TRAIN_FILE_PATH )
        display(HTML('<h1>7. endpoint api</h1>'))
        display( self.P_ENDPOINT_FILE_PATH )
        display(HTML('<h1>8. 실행</h1>'))
        
        
        display( self.P_MLOPS_STATUS )
        display( pn.Row( self.P_MODEL_INFO, self.P_DEPLOY_COMMENT,  self.P_DEPLOY_BUTTON  ) )
        
        self.P_DEPLOY_BUTTON.on_click(d)
        

        