import json
import tarfile
import datetime
import uuid
import time 

import boto3
import pymongo
import panel as pn
from IPython.core.display import HTML

class mlops():
    
    G_PLANT_CD = {
                      'K121' : {
                          
                                  'silo1' : { 
                                                'hyper_parameter' : {'batch_size': 2,'adam_learning': 0.001,'epochs': 10} ,
                                                'image_uri': ['mxnet-training:1.9.0-gpu-py38'],
                                                'instanceType': ['ml.p3.2xlarge'],
                                                'max_run_time': 360000,
                                                'instance_count': 1,
                                            } ,
                                  'silo2' : { 
                                                'hyper_parameter' : {'batch_size': 2,'adam_learning': 0.001,'epochs': 10} ,
                                                'image_uri': ['mxnet-training:1.9.0-gpu-py38'],
                                                'instanceType': ['ml.p3.2xlarge'],
                                                'max_run_time': 360000,
                                                'instance_count': 1,
                                            } ,
                                  'silo3' : { 
                                                'hyper_parameter' : {'batch_size': 2,'adam_learning': 0.001,'epochs': 10} ,
                                                'image_uri': ['mxnet-training:1.9.0-gpu-py38'],
                                                'instanceType': ['ml.p3.2xlarge'],
                                                'max_run_time': 360000,
                                                'instance_count': 1,
                                            } 
                              },
                     'K123' : {

                          'K_silo1' : { 
                                        'hyper_parameter' : {'batch_size': 2,'adam_learning': 0.001,'epochs': 10} ,
                                        'image_uri': ['mxnet-training:1.9.0-gpu-py38'],
                                        'instanceType': ['ml.p3.2xlarge'],
                                        'max_run_time': 360000,
                                        'instance_count': 1,
                                    } ,
                          'K_silo2' : { 
                                        'hyper_parameter' : {'batch_size': 2,'adam_learning': 0.001,'epochs': 10} ,
                                        'image_uri': ['mxnet-training:1.9.0-gpu-py38'],
                                        'instanceType': ['ml.p3.2xlarge'],
                                        'max_run_time': 360000,
                                        'instance_count': 1,
                                    } ,
                          'K_silo3' : { 
                                        'hyper_parameter' : {'batch_size': 2,'adam_learning': 0.001,'epochs': 10} ,
                                        'image_uri': ['mxnet-training:1.9.0-gpu-py38'],
                                        'instanceType': ['ml.p3.2xlarge'],
                                        'max_run_time': 360000,
                                        'instance_count': 1,
                                    } 
                      }
        
    }
        
    G_IMAGE_URL_NAME = None
                                
    
    G_USER_ID_DIST = None
    G_ACCESS_KEY = None
    G_SECRET_KEY = None
    
    P_PLANT_CD = None
    P_SILO_BUTTON = None
    P_SILO_TEXT = None
    
    
    P_HP_EPOCHS = None
    P_HP_ADAM_LEARNING = None
    P_PLANT_CD_TEXT = None
    

    P_MAX_RUN = None
    P_INSTANCE_CNT = None
    P_IMAGE_URL = None
    P_INSTANCE_TYPE = None
    
    P_S3_MODEL_PATH = None
    P_MLOPS_STATUS = None
    
    P_DEPLOY_BUTTON = None
    P_DEPLOY_COMMENT = None
    
    P_RESULT_VALUE = None
    P_SAGEMAKER_PROGRAM = None
    
    P_MAX_CONCURRENCY = None
    P_MEM_SIZE = None
    
    
    
    def __init__(self, aws_access_key_id = None, aws_secret_access_key = None): 
        pn.extension()
        
        self.G_ACCESS_KEY = aws_access_key_id
        self.G_SECRET_KEY = aws_secret_access_key
        model_user = self.mongodb_connection('dev', 'user', aws_access_key_id, aws_secret_access_key,  '/mlops/dev/database/mongo', '' )
        for row in model_user.find({}, {'_id' : 0}):
            self.G_USER_ID_DIST = row
        pass
    
    
    
    
    def get_file_list(self, silo = 'silo1'):

        # S3 버킷 및 공통 경로 설정
        bucket_name = 'silo-data-bucket'
        common_prefix = 'silo-model/{0}/'.format(silo)

        # Boto3 S3 클라이언트 생성

        s3_client = boto3.client('s3', aws_access_key_id=self.G_ACCESS_KEY,  aws_secret_access_key=self.G_SECRET_KEY)

        # 특정 경로 아래의 모든 파일 가져오기
#         def list_all_files_in_prefix(bucket_name, prefix):
#             response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
#             files = []
#             for obj in response.get('Contents', []):
#                 files.append(obj['Key'])
#             return files
        
         # 특정 경로 아래의 모든 파일 가져오기
        def list_all_files_in_prefix(bucket_name, prefix):

            files = []


            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )

            for obj in response.get('Contents', []):
                files.append(obj['Key'])

            # 다음 페이지가 있는 경우 계속해서 가져옴
            while 'NextContinuationToken' in response:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    ContinuationToken=response['NextContinuationToken']
                )
                for obj in response.get('Contents', []):
                    files.append(obj['Key'])

            return files





        # 모든 파일 중에서 model.tar.gz 파일 경로 가져오기
        def find_model_tar_gz_paths(file_paths):
            model_tar_gz_paths = []
            for file_path in file_paths:
                if file_path.endswith('model.tar.gz'):
                    model_tar_gz_paths.append("s3://" + bucket_name + "/" + file_path)
            return model_tar_gz_paths

        # model.tar.gz 파일 경로 출력
        all_files = list_all_files_in_prefix(bucket_name, common_prefix)
        model_tar_gz_paths = find_model_tar_gz_paths(all_files)


        model_tar_gz_paths.reverse()

        return model_tar_gz_paths[:5]

    
    def get_silo_list(self ) : 
        silo_list = []
        for silo in self.G_PLANT_CD[ self.P_PLANT_CD_TEXT.value ]:
            silo_list.append( (silo, silo) )
        return silo_list
    
    def get_image_uri(self):
#         plant_cd = self.P_PLANT_CD_TEXT.value
#         silo_name= self.P_SILO_TEXT.value
#         return self.G_PLANT_CD[ plant_cd ][ silo_name ]['image_uri']
        
        image_dict = {}
        ml_image = self.mongodb_connection('dev', 'image_spec', self.G_ACCESS_KEY, self.G_SECRET_KEY,  '/mlops/dev/database/mongo', '' )
        for row in ml_image.find({  "framework_name" : "mxnet","job_type" : "training"}, {"_id" : 0, 'image' : 1}) : 
            key = row['image'].split( "/" )[1]
            value = row['image']
            image_dict = {key : value} 
        self.G_IMAGE_URL_NAME = image_dict
        return image_dict
            
        
        
        
        
    
    
    def get_instanceType(self) : 
        plant_cd = self.P_PLANT_CD_TEXT.value
        silo_name= self.P_SILO_TEXT.value
        return self.G_PLANT_CD[ plant_cd ][ silo_name ]['instanceType']
    
    
    def get_max_run_time(self) : 
        plant_cd = self.P_PLANT_CD_TEXT.value
        silo_name= self.P_SILO_TEXT.value
        return self.G_PLANT_CD[ plant_cd ][ silo_name ]['max_run_time']
    
    def get_instance_count(self) : 
        plant_cd = self.P_PLANT_CD_TEXT.value
        silo_name= self.P_SILO_TEXT.value
        return self.G_PLANT_CD[ plant_cd ][ silo_name ]['instance_count']
    
    def get_hyper_parameter(self) : 
        plant_cd = self.P_PLANT_CD_TEXT.value
        silo_name= self.P_SILO_TEXT.value
        return self.G_PLANT_CD[ plant_cd ][ silo_name ]['hyper_parameter']
    
    
    # 패널 선언 부분
    def main_display_config(self) : 
        

#         self.P_PLANT_CD = pn.widgets.Select(name = 'plant_cd', options = list(self.G_PLANT_CD.keys()))
        
        self.P_PLANT_CD = pn.widgets.MenuButton(name='plant_cd', items=list(self.G_PLANT_CD.keys()), button_type='primary')
        self.P_PLANT_CD_TEXT = pn.widgets.TextInput(value='K121')
        
        self.P_SILO_BUTTON = pn.widgets.MenuButton(name='silo_select', items=self.get_silo_list(), button_type='primary')
        self.P_SILO_TEXT = pn.widgets.TextInput(value='silo1')
        
        
        self.P_PROD_VS_DEV = pn.widgets.Select(name='Select', options=['DATALAB', 'SF', 'SB'])
        
        self.P_USER_ID = pn.widgets.Select(name='user', options=list(self.G_USER_ID_DIST.keys()))
        
        
        
        # s3 모델 리스트 
        model_s3_list = self.get_file_list()
        self.P_S3_MODEL_PATH     = pn.widgets.MultiSelect( options=model_s3_list, value = [model_s3_list[0]], size=8,  width=700)
        
        
        
        # 하이퍼 파라미터 
        hyper_parameter = self.get_hyper_parameter()
        epochs        = hyper_parameter['epochs']
        adam_learning = hyper_parameter['adam_learning']
        batch_size    = hyper_parameter['batch_size']
        
        self.P_HP_EPOCHS        = pn.widgets.FloatInput(name='epochs', value=epochs, step=1, start=0, end=1000)
        self.P_HP_ADAM_LEARNING = pn.widgets.FloatInput(name='adam_learning', value=adam_learning, step=0.001, start=0, end=1000)
        self.P_HP_BATCH_SIZE    = pn.widgets.FloatInput(name='batch_size', value=batch_size, step=1, start=0, end=1000)

        
        # 인스턴스 스팩 
        self.P_MAX_RUN           = pn.widgets.FloatInput(name='max_run', value=self.get_max_run_time(),   step=1, start=0, end=3600000)
        self.P_INSTANCE_CNT      = pn.widgets.FloatInput(name='instance_count', value=self.get_instance_count(), step=1, start=0, end=1000)
        
        self.P_IMAGE_URL         = pn.widgets.Select(name='image_uri', options=list(self.get_image_uri().keys()) )
        self.P_INSTANCE_TYPE     = pn.widgets.Select(name='instance_type', options=self.get_instanceType() )
        

        
        # 배포
        self.P_MLOPS_STATUS   = pn.pane.Alert("배포 준비과 완료되면, 아래 버튼을 클릭해 주세요", alert_type='primary')
        self.P_DEPLOY_BUTTON  = pn.widgets.Button(name='Click me', button_type='primary')
        self.P_DEPLOY_COMMENT = pn.widgets.TextInput(value='comment')
        
        self.P_RESULT_VALUE = pn.widgets.JSONEditor(value={'hello' : 'world'}, width=800)
        
        
        self.P_SAGEMAKER_PROGRAM =  pn.widgets.TextInput(value='transfer_learning.py')
        
        
        self.P_MAX_CONCURRENCY     = pn.widgets.FloatInput(name='max_concurrency', value=10, step=1, start=1, end=100)
        self.P_MEM_SIZE            = pn.widgets.FloatInput(name='mem_size', value=4096, step=1024, start=1024, end=10240)
        
        
    def step_function_deploy(self, stepfunction_job ) : 
        # Step Functions 클라이언트 생성
        client =  self.aws_connection('stepfunctions', self.G_ACCESS_KEY, self.G_SECRET_KEY, 'ap-northeast-2')

        # Step Function 함수 ARN 가져오기
        response = client.list_state_machines()
        state_machines = response['stateMachines']


        for state_machine in state_machines:
            if state_machine['name'] == stepfunction_job:
                state_machine_arn = state_machine['stateMachineArn']


        response = client.start_execution(
            stateMachineArn = state_machine_arn,
            name = str(uuid.uuid1()),
            input = json.dumps(self.P_RESULT_VALUE.value)
        )

            
            
        
        
    def create_init(self) : 
        pn.extension('ace', 'jsoneditor')
        
        
        model_list = self.mongodb_connection('dev', 'list', self.G_ACCESS_KEY, self.G_SECRET_KEY,  '/mlops/dev/database/mongo', '' )
        
        # 모델 job id를 가지고 온다.
        silo_model_info = ''
        for row in model_list.find({'subtitle' : str(self.P_SILO_TEXT.value) }, {'_id' : 0}):
            silo_model_info = row
            
        # 버전을 갱신한다. 
        silo_model_log_info = None
        ml_log = self.mongodb_connection('dev', 'log', self.G_ACCESS_KEY, self.G_SECRET_KEY,  '/mlops/dev/database/mongo', '' )
        for row in ml_log.find({'model_id' : silo_model_info['job_id']}) : 
            silo_model_log_info = row 
        
        if silo_model_log_info == None : 
            silo_model_info['script_ver'] = 1
            silo_model_info['org_script_ver'] = 1
        else : 
            silo_model_info['script_ver'] = silo_model_log_info['script_ver'] + 1
            silo_model_info['org_script_ver'] = silo_model_log_info['org_script_ver']
            

        silo_model_info['model_id']   = silo_model_info['job_id']
        silo_model_info['model_name'] = silo_model_info['job_name']
        
        del silo_model_info['job_id']
        del silo_model_info['job_name']
        
        
        hyper_parameter = self.get_hyper_parameter()
        epochs        = hyper_parameter['epochs']
        adam_learning = hyper_parameter['adam_learning']
        batch_size    = hyper_parameter['batch_size']
        
        # 값을 매칭한다. 
        print("-------------------")
        silo_model_info['plant_cd']         = self.P_PLANT_CD_TEXT.value
        silo_model_info['silo']             = self.P_SILO_TEXT.value
        silo_model_info['train_image_path'] = 's3://dwe-mlops-hub-repository/dev/{0}/{1}/train_ready'.format(silo_model_info['model_name'], silo_model_info['script_ver']) 
        # 이거 가지고 오는 방법 찾아야 함
        silo_model_info['train_model_path'] = self.P_S3_MODEL_PATH.value[0]
        silo_model_info['output_model_path']= 's3://dwe-mlops-hub-repository/dev/{0}/{1}/train'.format(silo_model_info['model_name'], silo_model_info['script_ver']) 
        silo_model_info['image_uri']        = self.G_IMAGE_URL_NAME[ self.P_IMAGE_URL.value ]
        silo_model_info['instance_type']    = self.P_INSTANCE_TYPE.value
        silo_model_info['max_run_time']     = self.P_MAX_RUN.value
        
        silo_model_info['mem_size']         = self.P_MEM_SIZE.value
        silo_model_info['max_concurrency']  = self.P_MAX_CONCURRENCY.value
        
        silo_model_info['instance_count']   = self.P_INSTANCE_CNT.value
        silo_model_info['hyperparameters']  = {'max_run' : str(self.P_MAX_RUN.value), 'adam_learning' : str(adam_learning), 'epochs' : str(epochs), 'sagemaker_submit_directory' : 's3://silo-data-bucket/scripts/train-source-uri/sourcedir.tar.gz', "sagemaker_program" : self.P_SAGEMAKER_PROGRAM.value }
        
        silo_model_info['user']             = self.P_USER_ID.value
        silo_model_info['system_domain']    = self.P_PROD_VS_DEV.value
        silo_model_info['endp_config_mode'] = "serverless"
        
        
        

        
        self.P_RESULT_VALUE.value = silo_model_info

                                        
        
        pass
    
    def main_display(self) :
        def b(event):
            
            self.P_PLANT_CD_TEXT.value = event.new
            silo_list  = self.get_silo_list()
            self.P_SILO_BUTTON.items = list( silo_list )
            self.P_SILO_TEXT.value = list( silo_list )[0][0]
            
            model_s3_list = self.get_file_list(self.P_SILO_TEXT.value)
            self.P_S3_MODEL_PATH.options = model_s3_list
            self.P_S3_MODEL_PATH.value = [model_s3_list[0]]
            
            hyper_parameter = self.get_hyper_parameter()

            self.P_HP_EPOCHS.value        = hyper_parameter['epochs']
            self.P_HP_ADAM_LEARNING.value = hyper_parameter['adam_learning']
            self.P_HP_BATCH_SIZE.value    = hyper_parameter['batch_size']
            
        def e(event):
            
            self.P_SILO_TEXT.value = event.new
            model_s3_list = self.get_file_list(self.P_SILO_TEXT.value)
            self.P_S3_MODEL_PATH.options = model_s3_list
            self.P_S3_MODEL_PATH.value = [model_s3_list[0]]
            
            hyper_parameter = self.get_hyper_parameter()

            self.P_HP_EPOCHS.value        = hyper_parameter['epochs']
            self.P_HP_ADAM_LEARNING.value = hyper_parameter['adam_learning']
            self.P_HP_BATCH_SIZE.value    = hyper_parameter['batch_size']
            
            
        def f(event):
            
            self.P_DEPLOY_BUTTON.disabled = True

            # 클릭 이벤트 시 대기 상태 표시 
            self.P_MLOPS_STATUS.object = """[실행횟수 : {0}] \n 재클릭 하지 마세요. 배포 작업을 진행중입니다. """.format(self.P_DEPLOY_BUTTON.clicks)
            self.P_MLOPS_STATUS.alert_type = 'warning'

            import time
            time.sleep(2)

            # 실패 시 해당 에러 메시지 전송
            chk_upload_s3_ml_script =  {'msg' : "알수없는 에러가 발생했습니다.", 'status' : 'danger' }

            try : 
                self.create_init()
                self.step_function_deploy('sf_qa_mlops_silo_rate_full_piplines_step_job')
                self.P_MLOPS_STATUS.object = "[실행횟수 : {0}] \n 배포가 성공했습니다.".format(self.P_DEPLOY_BUTTON.clicks)
                self.P_MLOPS_STATUS.alert_type = 'success'
                
            except  Exception as e: 
                self.P_MLOPS_STATUS.object = '[문법에러 추정] : ' + str(e)
                self.P_MLOPS_STATUS.alert_type = 'danger'
                
            finally : 
                self.P_DEPLOY_BUTTON.disabled = False
            

            

        
        self.main_display_config()
        
        
        display( pn.pane.HTML("""<h1>배포 목적지</h1>""") ) 
#         prod_dev = pn.widgets.Select(name='Select', options=['DATALAB', 'SF', 'SB'])
        display( self.P_PROD_VS_DEV )
        
        
        display( pn.pane.HTML("""<h1>사용자 지정</h1>""") ) 
#         user_list = pn.widgets.Select(name='user', options=list(self.G_USER_ID_DIST.keys()))
        display( self.P_USER_ID )
        
        display( pn.pane.HTML("""<h1>공장코드</h1>""") ) 
        display( pn.Row(self.P_PLANT_CD, self.P_PLANT_CD_TEXT, height=150 ) )
        
        display( pn.pane.HTML("""<h1>사일로</h1>""") ) 
        
        display( pn.Column(  pn.Row(self.P_SILO_BUTTON, self.P_SILO_TEXT, self.P_SAGEMAKER_PROGRAM ), pn.Row(self.P_S3_MODEL_PATH , height=150)  ) ) 
        
#         display( pn.Row(self.P_SILO_BUTTON, self.P_SILO_TEXT, ) )
        
        display( pn.pane.HTML("""<h1>하이퍼 파라미더</h1>""") ) 
        display( pn.Row(self.P_HP_EPOCHS, self.P_HP_ADAM_LEARNING, self.P_HP_BATCH_SIZE ) ) 
        
        display( pn.pane.HTML("""<h1>인스턴스 타입</h1>""") ) 
        display( pn.Row(self.P_IMAGE_URL, self.P_INSTANCE_TYPE )  ) 
        display( pn.Row(self.P_MAX_RUN, self.P_INSTANCE_CNT )  ) 
        
        display(HTML('<h1>8. 실행</h1>'))
        
        
        display( self.P_MLOPS_STATUS )
        display( pn.Row(self.P_MAX_CONCURRENCY, self.P_MEM_SIZE  ) ) 
        display( pn.Row( self.P_SILO_TEXT,  self.P_DEPLOY_COMMENT, self.P_DEPLOY_BUTTON  ) )
        

        display( self.P_RESULT_VALUE ) 
        
        self.P_PLANT_CD.on_click(b)
        self.P_SILO_BUTTON.on_click(e)
        self.P_DEPLOY_BUTTON.on_click(f)
        
        
        
    
    
    
    
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
    
    
        
        

        