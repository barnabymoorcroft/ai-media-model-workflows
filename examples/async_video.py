import json,os,time
from urllib.request import Request,urlopen
def call(base,key,path,body=None):
 h={'Authorization':'Bearer '+key,'User-Agent':'ai-media-model-workflows/1.0'}
 data=None
 if body is not None:h['Content-Type']='application/json';data=json.dumps(body).encode()
 with urlopen(Request(base.rstrip('/')+path,data=data,headers=h),timeout=90) as r:return json.load(r)
def submit_and_poll(prompt,model='seedance-2.5'):
 base=os.getenv('VIDEO_API_BASE_URL','https://argolink.io/v1');key=os.environ['VIDEO_API_KEY']
 job=call(base,key,'/videos/generations',{'model':model,'prompt':prompt,'duration':5,'resolution':'720p','aspect_ratio':'16:9'})['request_id']
 for _ in range(240):
  item=call(base,key,'/videos/'+job)
  if item.get('status') in ('done','failed','expired'):return item
  time.sleep(10)
 raise TimeoutError(job)
if __name__=='__main__':print(submit_and_poll('A sunrise over a quiet harbor.'))
