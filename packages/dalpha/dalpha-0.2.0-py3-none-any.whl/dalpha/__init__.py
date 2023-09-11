import requests, json, boto3, io, logging, sys, os, pkg_resources
import time
import sentry_sdk

def check_package_version(package_name):
    logging.basicConfig(level=logging.INFO)
    installed_version = pkg_resources.get_distribution(package_name).version
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)
        data = response.json()
        latest_version = data["info"]["version"]
        if latest_version != installed_version:
            logging.warning(" dalpha sdk 버전 -> " + installed_version + " / 최신 버전 -> " + latest_version)
        else:
            logging.info(" dalpha sdk 버전 -> " + installed_version + " (latest)")
    except Exception as e:
        logging.warning("dalpha sdk 버전 확인 중 오류가 발생했습니다:", e)
    logging.basicConfig(level=logging.WARNING)
    
check_package_version("dalpha")

class Agent:
    def __init__(self, api_id, use_sqs = False, dev_server=False):
        if not isinstance(api_id, int): raise TypeError('api_id is not a int')
        if not isinstance(use_sqs, bool): raise TypeError('use_sqs is not a bool')
        if not isinstance(dev_server, bool): raise TypeError('dev_server is not a bool')
        self.cfg_path = os.path.join(sys.path[0],'.dalphacfg')
        self.__load_config(self.cfg_path)
        self.token = os.environ['TOKEN']
        if dev_server:
            self.base_url = os.environ['DEV_BASE_URL']
            self.sentry_env = "exp"
        else:
            self.base_url = os.environ['BASE_URL']
            self.sentry_env = "production"
        self.queue_url = os.environ['QUEUE_URL']
        self.sentry_dsn = os.environ['SENTRY_DSN']
        self.evaluate_url = os.path.join(self.base_url, f"inferences/{api_id}/evaluate")
        self.api_id = api_id
        self.mock = {}
        self.s3 = boto3.client('s3')
        self.sqs = boto3.client('sqs', region_name='ap-northeast-2')
        self.evaluates = {}
        self.use_sqs = use_sqs

        sentry_sdk.init(
        dsn=self.sentry_dsn,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        environment = self.sentry_dsn
        )
        sentry_sdk.set_tag("api_id", api_id)

    def __load_config(self,file_path):
        if not os.path.isfile(file_path):
            logging.warning(f"{file_path} 파일을 찾을 수 없습니다.")
            return
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=")
                os.environ[key] = value

    def set_mock(self, mock):
        self.mock = mock

    def batch(self, iterable, n):
        # Yield successive n-sized chunks from iterable.
        for i in range(0, len(iterable), n):
            yield iterable[i:i + n]
    
    '''
        message_id를 10개씩 끊어서 sqs에 batch delete 요청으로 메세지 삭제
    '''
    def delete_messages(self, message_ids):
        entries = list(map(lambda message_id: {
            'Id': str(message_id),
            'ReceiptHandle': self.evaluates[message_id]
        }, message_ids))
        for group in self.batch(entries, 10):
            try:
                self.sqs.delete_message_batch(
                    QueueUrl = self.queue_url,
                    Entries = group
                )
            except Exception as e:
                logging.error("Error while deleting messages", e)
    
    '''
        evaluate이 유효한지 서버에 요청해서 유효하지 않은 메세지는 sqs에서 삭제
        유효한 메세지만 반환
    '''
    def filter_valid(self, messages):
        messages_to_delete = []
        messages_to_handle = []
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        for message in messages:
            endpoint = os.path.join(self.base_url, f"inferences/{self.api_id}/evaluate/id-poll/{message['id']}")
            try:
                response = requests.request("GET", endpoint, headers = headers)
                if response.status_code >= 400:
                    messages_to_delete.append(message)
                else:
                    messages_to_handle.append(message)
            except Exception as e:
                logging.error("Error while validating evaluate message", e)
        try:
            self.delete_messages(list(map(lambda x: x['id'], messages_to_delete)))
            return messages_to_handle
        except Exception as e:
            logging.error("Error while validating evaluate message", e)

    def poll(self, max_number_of_messages = 1, mock=True):
        if not isinstance(max_number_of_messages,int): TypeError("max_number_of_messages is not a int")
        if not isinstance(mock, bool): TypeError("mock is not a bool")

        if mock:
            return self.mock
        
        if self.use_sqs:
            response = self.sqs.receive_message(
                QueueUrl = self.queue_url,
                MaxNumberOfMessages = max_number_of_messages,  # 가져올 메시지의 최대 수 (1개 이상 설정 가능)
                WaitTimeSeconds = 0       # 긴 폴링을 위한 대기 시간 (초 단위)
            )
            ret = []
            messages = response.get('Messages', [])
            for message in messages:
                message_body = message['Body']
                try:
                    # message_body를 딕셔너리로 변환
                    message_dict = json.loads(message_body)
                except json.JSONDecodeError:
                    logging.error("유효한 JSON 형식이 아닙니다.")
                self.evaluates[message_dict['id']] = message['ReceiptHandle']
                ret.append(message_dict)
            
            ret = self.filter_valid(ret)

            if len(ret) == 0:
                return None
            elif len(ret) == 1:
                return ret[0]
            else:
                return ret

        time.sleep(0.2)
        url = f"{self.evaluate_url}/poll"

        headers = {
        'token': self.token
        }
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 422:
            return None
        elif response.status_code != 200:
            logging.WARNING(f'error from poll / response status_code {response.status_code}: {response.text} \n poll function will return None.')
            return None
        
        return response.json()
        
    def validate(self, evaluate_id, output, mock=True):
        if mock:
            logging.debug(output)
            return

        if self.use_sqs:
            try: 
                response = self.sqs.delete_message(
                    QueueUrl = self.queue_url,
                    ReceiptHandle = self.evaluates[evaluate_id]
                )
            except Exception as e:
                logging.error("error from sqs.delete_message\n",e)
                del self.evaluates[evaluate_id]

        payload = json.dumps({
            "id": evaluate_id,
            "json": output
        })

        url = f"{self.evaluate_url}/validate"

        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(f'error from validate / response status_code {response.status_code}: {response.text}')
        
    def validate_error(self, evaluate_id, output, mock=True):
        if not isinstance(evaluate_id, int): raise TypeError('evaluate_id is not a int')
        if not isinstance(output, dict): raise TypeError('output is not a dict')
        if not isinstance(mock, bool): raise TypeError('mock is not a bool')
        try:
            payload = json.dumps({
                "id": evaluate_id,
                "json": output
            })
        except Exception as e:
            Exception("failed to parse validate_error input : ", e)
        if mock:
            logging.debug(output)
            return

        if self.use_sqs:
            try: 
                response = self.sqs.delete_message(
                    QueueUrl = self.queue_url,
                    ReceiptHandle = self.evaluates[evaluate_id]
                )
            except Exception as e:
                logging.error("error from sqs.delete_message\n",e)
                del self.evaluates[evaluate_id]

        payload = json.dumps({
            "id": evaluate_id,
            "error": output
        })

        url = f"{self.evaluate_url}/error"

        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        if response.status_code != 200:
            logging.WARNING(f'error from validate_error / response status_code {response.status_code}: {response.text}')
            return  
        
    def download_from_url(self, url):
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise Exception(f"can't download from url {r.status_code} : {r.text}")
        else:
            return io.BytesIO(r.content)
            # return Image.open(io.BytesIO(r.content)).convert('RGB')

    def download_from_s3(self, bucket, key, download_path):
        try:
            self.s3.download_file(bucket, key, download_path)
        except Exception as e:
            logging.error(f"failed to download from s3\n{e}")

    def upload_s3(self, upload_path, bucket, key):
        try:
            self.s3.upload_file(upload_path, bucket, key)
        except Exception as e:
            logging.error(f"failed to upload s3\n{e}")

    def stop_instance(self):
        try:
            res = requests.request("GET", 'http://169.254.169.254/latest/meta-data/instance-id')
            if res.status_code != 200:
                raise Exception("get instance-id failed!")
            instance_id = res.text[2:]
            
            url = f"https://api.dalpha.so/instances/{instance_id}/stop/@sdk"

            headers = {
                'token': self.token,
                'Content-Type': 'application/json'
            }

            response = requests.request("PUT", url, headers=headers)
            if response.status_code != 200:
                raise Exception(f'error from stop_instance / response status_code {response.status_code}')

        except Exception as e:
            raise Exception(f"error from stop_instance\n{e}")