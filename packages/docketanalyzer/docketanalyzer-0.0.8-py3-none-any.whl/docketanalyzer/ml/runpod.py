import time
from pathlib import Path
import requests
import simplejson as json
from toolz import partition_all
from docketanalyzer.utils import (
    RUNPOD_API_KEY,
    RUNPOD_INFERENCE_ENDPOINT_ID,
)


class RunPodAPI:
    def __init__(self, api_key=None, jobs=[]):
        if api_key is None:
            api_key = RUNPOD_API_KEY
        if api_key is None:   
            raise ValueError('You must either pass an api_key or set the RUNPOD_API_KEY environment variable')
        self.api_key = api_key
        self.jobs = jobs
    
    def _make_request(
        self, endpoint_id, data={}, endpoint_type='runsync',
        job_id=None, request_type='post', return_json=True,
    ):
        url = f"https://api.runpod.ai/v2/{endpoint_id}/{endpoint_type}"
        if job_id:
            url += f"/{job_id}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        if request_type == 'post':
            r = requests.post(url, json=data, headers=headers)
        elif request_type == 'get':
            r = requests.get(url, headers=headers)
        else:
            raise ValueError('request_type must be either "post" or "get"')
        if return_json:
            r = r.json()
        return r

    def _get_endpoint_id(self, endpoint_id, default_endpoint_id, env_var_name):
        if endpoint_id is None:
            endpoint_id = default_endpoint_id
        if endpoint_id is None:
            raise ValueError(f'You must either pass an endpoint_id or set the {env_var_name} environment variable')
        return endpoint_id

    def save_jobs(self, path):
        Path(path).write_text(json.dumps(self.jobs))
    
    def load_jobs(self, path):
        self.jobs = json.loads(Path(path).read_text())

    def predict(self, prompts, endpoint_id=None, endpoint_type='run', **args):
        endpoint_id = self._get_endpoint_id(endpoint_id, RUNPOD_INFERENCE_ENDPOINT_ID, 'RUNPOD_INFERENCE_ENDPOINT_ID')
        data = {
            'input': {
                'prompt': prompts, 
                'args': args,
            },
        }
        job = self._make_request(endpoint_id, data, endpoint_type)
        job['endpoint_id'] = endpoint_id
        self.jobs.append(job)
        return job

    def batch_predict(self, prompts, batch_size, pause=3, endpoint_id=None, **args):
        for batch in partition_all(batch_size, prompts):
            self.predict(batch, endpoint_id, **args)

        while 1:
            time.sleep(pause)
            self.update_status()
            if all(job['status'] in ['COMPLETED', 'FAILED'] for job in self.jobs):
                results = []
                for job in self.jobs:
                    if job['status'] == 'COMPLETED':
                        results.extend(job['output']['generated_text'])
                return results
        
    def update_status(self, job_id=None):
        statuses = []
        for i in range(len(self.jobs)):
            job = self.jobs[i]
            if job_id is None or job['id'] == job_id:
                if job['status'] not in ['COMPLETED', 'FAILED']:
                    job = self._make_request(
                        job['endpoint_id'],
                        job_id=job['id'],
                        endpoint_type='status',
                        request_type='get',
                    )
                    self.jobs[i] = job
                statuses.append(job)
        if job_id is not None:
            return statuses[0]
        return statuses

    def create_pod(
        self,
        image_name='nadahlberg/tgi-runpod:pod',
        volume_id='fhalsnm798',
    ):
        url = f'https://api.runpod.io/graphql?api_key={self.api_key}'
        data = {'query': 
            f"""mutation {{
                podFindAndDeployOnDemand(
                    input: {{
                        name: "TGI"
                        imageName: "{image_name}"
                        networkVolumeId: "{volume_id}"
                        dataCenterId: "US-KS-1"
                        gpuTypeId: "NVIDIA RTX A6000"
                        cloudType: ALL
                        gpuCount: 1
                        volumeInGb: 40
                        containerDiskInGb: 40
                        minVcpuCount: 2
                        minMemoryInGb: 15
                        dockerArgs: ""
                        ports: "8888/http"
                        volumeMountPath: "/workspace"
                        env: [{{ key: "JUPYTER_PASSWORD", value: "rn51hunbpgtltcpac3ol" }}]
                    }}
                ) {{
                    id
                    imageName
                    env
                    machineId
                    machine {{
                    podHostId
                    }}
                }}
            }}"""
        }
        r = requests.post(url, json=data)
        return r.json()

    def get_pods(self):
        url = f'https://api.runpod.io/graphql?api_key={self.api_key}'
        data = {'query': 
            """query Pods {
                myself {
                    pods {
                        id
                        name
                        runtime {
                            uptimeInSeconds
                            ports {
                                ip
                                isIpPublic
                                privatePort
                                publicPort
                                type
                            }
                            gpus {
                                id
                                gpuUtilPercent
                                memoryUtilPercent
                            }
                            container {
                                cpuPercent
                                memoryPercent
                            }
                        }
                    }
                }
            }"""
        }
        r = requests.post(url, json=data)
        return r.json()

    def stop_pod(self, pod_id):
        url = f'https://api.runpod.io/graphql?api_key={self.api_key}'
        data = {'query': 
            f"""mutation {{
                podStop(input: {{podId: "{pod_id}"}}) {{
                    id
                    desiredStatus
                }}
            }}"""
        }
        r = requests.post(url, json=data)
        return r.json()



if __name__=='__main__':
    api = RunPodAPI()
    #print(api.create_pod())
    r = api.get_pods()
    for pod in r['data']['myself']['pods']:
        print(pod)
        print(api.stop_pod(pod['id']))
    