import json
import tarfile
import datetime
import uuid

import boto3
import pymongo
import panel as pn
from IPython.core.display import HTML
import pandas as pd
from collections import OrderedDict
import os


# from ipyfilechooser import FileChooser
pn.extension('tabulator')
pn.extension(notifications=True)

class mlops():
    

    G_DEPLOY_TARGET = ['DATALAB', 'SF', 'SB']
    G_MANAGER_ID_DIST = {}
    G_EVALUATE_DF = None
    
    G_ENDP_CONFIG_MODE = ['serverless']
    G_ENDP_MEM_SIZE = [2048, 1024, 3072, 4096, 5120, 6144]
    
   
    P_DEPLOY_TARGET = None
    P_MANGER_ID = None
    
    P_EVALUATE = None
    P_EVALUATE_DTL = None
    P_CHK = None
    P_DEPLOY_BUTTON = None
    P_MLOPS_STATUS = None
    
    P_ENDP_CONFIG_MODE = None
    P_ENDP_MAX_CONCURRENCY = None
    P_ENDP_MEM_SIZE = None
    
    
    
    G_STAT_MACHINE = None
    
    
    
    def __init__(self, aws_access_key_id = None, aws_secret_access_key = None): 
        pn.extension()
        
        self.G_AWS_ACCESS_KEY = aws_access_key_id
        self.G_AWS_SECRET_KEY = aws_secret_access_key
        
            
                
        self.G_SSM_MONGO_PATH = '/mlops/dev/database/mongo'
        
        
        deploy_collection = self.mongodb_connection('dev', 'depoly', self.G_AWS_ACCESS_KEY, self.G_AWS_SECRET_KEY, self.G_SSM_MONGO_PATH )
        for row in deploy_collection.find({'target' : 'labcut_autogluon'}) : 
            self.G_STAT_MACHINE = row['step_function']

        model_list = self.mongodb_connection('dev', 'log', self.G_AWS_ACCESS_KEY, self.G_AWS_SECRET_KEY, self.G_SSM_MONGO_PATH)


        match_filter  =  {'$match' : {'acc' : {'$ne' : None}, 'train.status' : 'Completed'}}
        project_filter = {'$project' : {    
                             '_id' : 0, 
#                              'latest' : {'$cond' : {'if' : {'$eq' : ['$latest', True]}, 'then' : '배포', 'else' : '미배포'}}, #1,
                             'dev_deploy' : {'$cond' : {'if' : {'$eq' : ['$dev_deploy', True]}, 'then' : '배포', 'else' : '-'}}, #1,
                             'dev_latest' : {'$cond' : {'if' : {'$eq' : ['$dev_latest', True]}, 'then' : '사용', 'else' : '-'}}, #1,
                             'prod_deploy' : {'$cond' : {'if' : {'$eq' : ['$prod_deploy', True]}, 'then' : '배포', 'else' : '-'}}, #1,
                             'prod_latest' : {'$cond' : {'if' : {'$eq' : ['$prod_latest', True]}, 'then' : '사용', 'else' : '-'}}, #1,
                             'train_status' : '$train.status',
                             'user_id' : '$local.user_id',
                             'user_name' : '$local.user_name',
                             'script_ver' :1,
                             'model_name' : 1,   
                             'train_total_time' : {'$ifNull' : ['$train.train_total_time', '0']},
                             'dev_deploy_time' : {'$ifNull' : ['$dev_deploy_time', '-']},
                             'prod_deploy_time' : {'$ifNull' : ['$prod_deploy_time', '-']},
                             'acc' : 1, 
                             'model' : 1,
                             'root_mean_squared_error' : 1, 
                             'mean_squared_error' : 1, 
                             'mean_absolute_error' : 1,
                             'median_absolute_error' : 1, 
                             'r2' :1 ,
                             'model_path' : '$train.model_tar_path',
                             'model_id' : 1,
                             'comment' : 1
            
                        }}
        
        sort_filter = {'$sort' : {'_id' : -1}}
            
        
        
        tmp_model_list = []

        
        for row in model_list.aggregate([match_filter, project_filter, sort_filter]):
            ordered_dict = OrderedDict()
            for key in project_filter['$project']:  
                if key != '_id' :
                    ordered_dict[key] = row[key]
            
            tmp_model_list.append( ordered_dict )
        self.G_EVALUATE_DF = pd.DataFrame( tmp_model_list )
                
        
        
        model_user = self.mongodb_connection('dev', 'user', self.G_AWS_ACCESS_KEY, self.G_AWS_SECRET_KEY, self.G_SSM_MONGO_PATH)
        for row in model_user.find({}, {'_id' : 0}):
            self.G_MANAGER_ID_DIST = row
            
        
    
    
    # aws 통합 접속 정보이다. 
    def aws_connection(self, service_name, aws_access_key_id, aws_secret_access_key, region_name = "ap-northeast-2"):
        if service_name == 's3' : 
            if aws_access_key_id == '' or aws_secret_access_key == '': 
                cli = boto3.client('s3', region_name=region_name)
            else :
                cli = boto3.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)

        if service_name == 'ssm' : 
            if aws_access_key_id == '' or aws_secret_access_key == '': 
                cli = boto3.client('ssm', region_name=region_name)
            else :
                cli = boto3.client('ssm', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)


        if service_name == 'stepfunctions' : 
            if aws_access_key_id == '' or aws_secret_access_key == '': 
                cli = boto3.client('stepfunctions', region_name=region_name)
            else :
                cli = boto3.client('stepfunctions', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)

        return cli   
    
    
    
    
    # ssm에서 데이터를 가지고 온다. 
    def get_ssm(self, parameter_store_path, aws_access_key_id, aws_secret_access_key, region_name ):
        client =  self.aws_connection('ssm', aws_access_key_id, aws_secret_access_key, region_name  )

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
    def mongodb_connection( self, environment, collection_div, aws_access_key_id, aws_secret_access_key, ssm_path, region_name = 'ap-northeast-2' ) : 
        
        SSM_PATH = ssm_path.format(environment)
        CONN_INFO = self.get_ssm( SSM_PATH,  aws_access_key_id, aws_secret_access_key, region_name )
        MONGODB_HOST = CONN_INFO['host']
        MONGODB_PORT = CONN_INFO['port']
        DATABASE     = CONN_INFO['db_name']
        COLLECTION   = CONN_INFO['collection'][collection_div]
        conn = pymongo.MongoClient(MONGODB_HOST)
        db = conn[DATABASE]
        collection = db[COLLECTION]

        return collection
    
    
    # S3 모델 다운로드 
    def download_s3_model_file(self, s3_path, local_path = "./tmp.tar.gz", bucket_name = "dwe-mlops-hub-repository") : 
        # AWS S3 클라이언트 생성
        s3_client = self.aws_connection('s3', aws_access_key_id = self.G_AWS_ACCESS_KEY , aws_secret_access_key = self.G_AWS_SECRET_KEY)        

        s3_path = s3_path.format('dev')

        # tar.gz 파일 다운로드
        s3_client.download_file(bucket_name, s3_path, local_path)

        return local_path
    
    # 접속 키 정보 호출
    def get_sf_key_info(self, deploy_type):
        collection = self.mongodb_connection( 'dev', 
                                         'key', 
                                          aws_access_key_id = self.G_AWS_ACCESS_KEY, 
                                          aws_secret_access_key = self.G_AWS_SECRET_KEY, 
                                          ssm_path = self.G_SSM_MONGO_PATH
                                        )

        result = list(collection.find({'domain' : deploy_type}))[0]

        return result['aws_access_key_id'], result['aws_secret_access_key'], result['s3_bucket_name']
    
    
    def upload_s3_file(self, local_path, deploy_type , s3_path = "mlops"):
        try :
            # 업로드 할 계정 정보값 호출
            diff_aws_access_key, diff_aws_secret_key, diff_bucket_name = self.get_sf_key_info(deploy_type)
            s3_client = boto3.client('s3', 
                              aws_access_key_id = diff_aws_access_key, 
                              aws_secret_access_key = diff_aws_secret_key)

            s3_path = s3_path.format('prod')

            res = s3_client.upload_file(local_path, diff_bucket_name, r'{0}'.format( s3_path ) , ExtraArgs={'ContentType': 'application/x-gzip'})   
        except :
            pn.state.notifications.error( '파일 복제중 에러 발생')
            print('error upload_s3_file')
        finally :
            # 임시 파일 삭제
            os.remove(local_path)
            
    

    
    # 패널 선언 부분
    def main_display_config(self) : 
        
        self.P_DEPLOY_TARGET       = pn.widgets.Select(name='배포 목적지', options = self.G_DEPLOY_TARGET ) 

        self.P_MANGER_ID           = pn.widgets.Select(name='매니저 사번', options = list(self.G_MANAGER_ID_DIST.keys()) ) 
        
        self.P_EVALUATE                 = pn.widgets.Tabulator(self.G_EVALUATE_DF,  selectable=True,hidden_columns  = ['index'],  disabled = True,  pagination='remote', page_size=10, header_filters=True)

        
        self.P_MLOPS_STATUS   = pn.pane.Alert("배포 준비과 완료되면, 아래 버튼을 클릭해 주세요", alert_type='primary')
        
        self.P_CHK                      =  pn.widgets.input.TextAreaInput( disabled = True, placeholder='배포 모델을 선택해주세요..')
        self.P_DEPLOY_BUTTON            =  pn.widgets.Button(name='배포', button_type='primary', min_height = 40, width=200)
        
        
        
        #P_ENDP_CONFIG_MODE = None
        #P_ENDP_MAX_CONCURRENCY = None
        #P_ENDP_MEM_SIZE = None
        self.P_ENDP_CONFIG_MODE = pn.widgets.Select(name='유형', options = self.G_ENDP_CONFIG_MODE )
        self.P_ENDP_MAX_CONCURRENCY = pn.widgets.IntInput(name='최대 동시성' , value=1, step=1, start=1, end=10)
        self.P_ENDP_MEM_SIZE = pn.widgets.Select(name='메모리 크기', options = self.G_ENDP_MEM_SIZE )
        
    

    
    G_DEPLOY_MODEL_INFO = {}

    # mlops 메인 화면이다. 
    # 해당 화면의 역할은 show_config의 들어갈 데이터를 만들어 낸다. 
    def main_display(self) :
        
        def selected_callback(obj,event):
            
            if len(self.P_EVALUATE.selection) != 0 :
#                 model_name = self.P_EVALUATE.selected_dataframe.to_dict('recode')[0]['model_name']
#                 script_ver = self.P_EVALUATE.selected_dataframe.to_dict('recode')[0]['script_ver']
                
                row_idx = self.P_EVALUATE.selection[0]
                model_id = self.G_EVALUATE_DF.loc[row_idx]['model_id']
                model_name = self.G_EVALUATE_DF.loc[row_idx]['model_name']
                script_ver = self.G_EVALUATE_DF.loc[row_idx]['script_ver']
                dev_deploy_time = self.G_EVALUATE_DF.loc[row_idx]['dev_deploy_time']
                model_path = self.G_EVALUATE_DF.loc[row_idx]['model_path']
                
                
                
                
                self.P_CHK.value = "{0}의 {1}버전을 배포하시겠습니까?".format( model_name, str( script_ver ) )
                
                self.G_DEPLOY_MODEL_INFO['model_id'] = model_id
                self.G_DEPLOY_MODEL_INFO['model_name'] = model_name
                self.G_DEPLOY_MODEL_INFO['model_version'] = int(script_ver)
                self.G_DEPLOY_MODEL_INFO['manager_id'] = self.P_MANGER_ID.value
                self.G_DEPLOY_MODEL_INFO['dev_deploy_time'] = dev_deploy_time
                self.G_DEPLOY_MODEL_INFO['model_path'] = model_path
                

            
        def deploy_endpoint(event):
            
            
            self.P_DEPLOY_BUTTON.disabled = True
            
            
            ###
            
            # 클릭 이벤트 시 대기 상태 표시 
            self.P_MLOPS_STATUS.object = """[실행횟수 : {0}] \n 재클릭 하지 마세요. 배포 작업을 진행중입니다. """.format(self.P_DEPLOY_BUTTON.clicks)
            self.P_MLOPS_STATUS.alert_type = 'warning'
            
            
            # 실패 시 해당 에러 메시지 전송
            chk_upload_s3_ml_script =  {'msg' : "알수없는 에러가 발생했습니다.", 'status' : 'danger' }
            ###
            
            try : 
                
                deploy_target = self.P_DEPLOY_TARGET.value

                if deploy_target != 'DATALAB' :
                    if self.G_DEPLOY_MODEL_INFO['dev_deploy_time'] == '-' :
                        pn.state.notifications.error( 'Data Lab에 먼저 배포 하세요')
                        return 'Error'
                    # 배포로 간주
                    else :
                        pn.state.notifications.success( '모델 복사를 시작합니다')
                        s3_file_path = '{0}/'+self.G_DEPLOY_MODEL_INFO['model_path']
                        print(s3_file_path)
                        self.upload_s3_file( self.download_s3_model_file(s3_file_path), deploy_target ,  s3_file_path)
                        pn.state.notifications.success( '도메인 {0} 복사를 완료 하였습니다'.format(deploy_target))


                # 배포 구간 설정
                self.G_DEPLOY_MODEL_INFO['system_domain'] = deploy_target
                self.G_DEPLOY_MODEL_INFO['endp_config_mode'] = self.P_ENDP_CONFIG_MODE.value
                self.G_DEPLOY_MODEL_INFO['endp_max_concurrency'] = self.P_ENDP_MAX_CONCURRENCY.value
                self.G_DEPLOY_MODEL_INFO['endp_mem_size'] = self.P_ENDP_MEM_SIZE.value
                


                excute_id = str(uuid.uuid1())

                cli = boto3.client('stepfunctions', aws_access_key_id = self.G_AWS_ACCESS_KEY, aws_secret_access_key = self.G_AWS_SECRET_KEY, region_name='ap-northeast-2')

                response = cli.start_execution(  
                                                stateMachineArn=self.G_STAT_MACHINE,
                                                name=excute_id, 
                                                input= json.dumps(self.G_DEPLOY_MODEL_INFO)
                                              )

                pn.state.notifications.success( '배포가 시작됩니다.')
    
    
                chk_upload_s3_ml_script =  {'msg' : "파일 업로드가 성공했습니다. 모델 배포를 시작합니다", 'status' : 'success' }
            
            except  Exception as e: 
                chk_upload_s3_ml_script =  {'msg' : '[문법에러 추정] : ' + str(e), 'status' : 'danger' }
            finally :
                # 상태 업데이트
                self.P_MLOPS_STATUS.object = chk_upload_s3_ml_script['msg']
                self.P_MLOPS_STATUS.alert_type = chk_upload_s3_ml_script['status']

                self.P_DEPLOY_BUTTON.disabled = False

            
            
        
        
        self.main_display_config()
        
        display(HTML('<h1>1. 배포 타겟 선택</h1>'))
        display( self.P_DEPLOY_TARGET ) 
  
        display(HTML('<h1>1. 배포자 입력 </h1>'))
        display( self.P_MANGER_ID ) 
        
        display(HTML('<h1>2. 모델 버전 선택 </h1>'))
        
        self.P_EVALUATE.link(self.P_CHK, callbacks={'selection': selected_callback})    
        display( self.P_EVALUATE )
        
        display(HTML('<h1>3. 배포버전 선택 </h1>'))
        
        
        endp_config = pn.Row(self.P_ENDP_CONFIG_MODE, self.P_ENDP_MAX_CONCURRENCY, self.P_ENDP_MEM_SIZE )
        display(endp_config)
        
        display( self.P_MLOPS_STATUS )
        deploy_button = pn.Row( self.P_CHK, self.P_DEPLOY_BUTTON )
        display( deploy_button )
        
        self.P_DEPLOY_BUTTON.on_click( deploy_endpoint )
        
        

        