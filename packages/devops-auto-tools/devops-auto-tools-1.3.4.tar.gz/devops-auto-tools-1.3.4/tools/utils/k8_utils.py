import requests
import jwt
import yaml
import os
import subprocess

from tools.dtos.k8_var import var as k8_var
from tools.dtos.jump_var import var as jump_var

def get_kubesphere_access_token(
  host:str,
  username:str,
  password:str
):
  try:
    data = {
      'grant_type': 'password',
      'username': username,
      'password': password,
      'client_id': 'kubesphere',
      'client_secret': 'kubesphere'
    }
    response = requests.post(f'http://{host}/oauth/token', data=data)
    access_token = response.json()["access_token"]
    return access_token
  except:
    print("Login false!")
    return None

def decode_jwt(token):
  return jwt.decode(token, options={"verify_signature": False})

def requests_kubeconfig(
  host:str,
  access_token:str
):
  headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
  }
  token_parser = decode_jwt(access_token)
  response = requests.get(
  f'http://{host}/kapis/resources.kubesphere.io/v1alpha2/users/{token_parser["username"]}/kubeconfig', 
  headers=headers
  )
  return yaml.safe_load(response.text)

def update_kube_context(old_kubeconfig, new_kubeconfig, new_context_name):
  # get new profile
  
  new_user_profile = new_kubeconfig["users"][0]
  new_cluster_profile = new_kubeconfig["clusters"][0]
  # gen new context
  new_context_profile = new_kubeconfig["contexts"][0]
  new_context_profile["name"] = new_context_name
  
  # update config
  # change context 
  old_kubeconfig["current-context"] = new_context_name
  
  # dedup old context
  for item in old_kubeconfig["contexts"]:
      if item["name"] == new_context_profile["name"]:
          old_kubeconfig["contexts"].remove(item)
  old_kubeconfig["contexts"].append(new_context_profile)
  
  # dedup old user profile 
  for item in old_kubeconfig["users"]:
      if item["name"] == new_user_profile["name"]:
          old_kubeconfig["users"].remove(item)
  old_kubeconfig["users"].append(new_user_profile)
  
  # dedup old cluster profile
  for item in old_kubeconfig["clusters"]:
      if item["name"] == new_cluster_profile["name"]:
          old_kubeconfig["clusters"].remove(item)
  old_kubeconfig["clusters"].append(new_cluster_profile)
  return old_kubeconfig

def load_kubeconfig_file():
  try:
    homepath = os.path.expanduser('~')
    f = open(f'{homepath}/.kube/config','r')
    data = yaml.safe_load(f)
    f.close()
    return data
  except:
    return None

def save_kubeconfig(kubeconfig):
  homepath = os.path.expanduser('~')
  f = open(f'{homepath}/.kube/config','w')
  yaml.dump(kubeconfig, f)
  f.close()

def ssh_remote_exec(
  ssh_profile_name:str,
  cmd:str
):
  stdout, stderr = subprocess.Popen(
    f"ssh {ssh_profile_name} {cmd}", 
    shell=True, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
  ).communicate()
  if stderr.decode('UTF-8') != "" and "Warning" not in stderr.decode('UTF-8'):
    raise Exception(f'Remote execute error: {stderr.decode("UTF-8")}')
  return stdout.decode('UTF-8')

def get_svc_cidr(ssh_profile_name:str):
  cmd = "kubectl cluster-info dump | grep -m 1 service-cluster-ip-range"
  data = ssh_remote_exec(ssh_profile_name,cmd)
  return data.split()[0].replace('"--service-cluster-ip-range=', '').replace('",','')

def get_ksapi_ip(ssh_profile_name:str):
  cmd = "kubectl get svc -A|grep ks-apiserver"
  data = ssh_remote_exec(ssh_profile_name,cmd)
  return data.split("\n")[0].split()[3]

def update_kubeconfig():
  k8_var.token = get_kubesphere_access_token(
    k8_var.kubesphere_ip, 
    k8_var.username,
    k8_var.password
  )
  k8_var.new_kubeconfig = requests_kubeconfig(
    k8_var.kubesphere_ip,
    k8_var.token
  )
  k8_var.old_kubeconfig = load_kubeconfig_file()
  if k8_var.old_kubeconfig == None:
    save_kubeconfig(k8_var.new_kubeconfig)
  else:
    k8_var.old_kubeconfig = update_kube_context(
      k8_var.old_kubeconfig,
      k8_var.new_kubeconfig,
      jump_var.profile
    )
    save_kubeconfig(k8_var.old_kubeconfig)
