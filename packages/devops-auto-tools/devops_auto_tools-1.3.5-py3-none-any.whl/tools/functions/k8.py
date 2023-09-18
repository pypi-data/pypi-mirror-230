from subprocess import call
from threading import Thread

from tools.utils import utils
from tools.utils.utils import fetch_and_update_kubeconfig
from tools.dtos.jump_var import var as jump_var
from tools.dtos.k8_var import var as k8_var
from tools.dtos.utill_var import var as utils_var

def get_profiles():
  f = open(utils.get_config_path("~/.ssh/config"), 'r')
  lines = f.readlines()
  f.close()
  profiles = []
  for line in lines:
    if "Host " in line and "*" not in line:
      profiles.append(line.split("Host ")[1].split("\n")[0])
  return profiles

def set_profile():
  jump_var.profile = utils.render_choices(get_profiles())
  if jump_var.profile != False:
    return True
  return False

def set_profile_gw_username_pass():
  jump_var.profile = utils.render_choices(get_profiles())
  if jump_var.profile != False:
    jump_var.gateway_ip = utils.get_default_gw_ip()
    k8_var.username = input("Enter kubesphere username: ")
    k8_var.password = input("Enter kubesphere password: ")
    return True
  return False

def create_connection():
  utils_var.allow_exist = False
  jump_var.cidr = utils.get_svc_cidr(jump_var.profile)
  k8_var.ksapi_ip = utils.get_ksapi_ip(jump_var.profile)
  utils.routing(jump_var.gateway_ip, jump_var.cidr)
  update_kubeconfig_thread = Thread(target=fetch_and_update_kubeconfig)
  update_kubeconfig_thread.start()
  call([ 
    'sshuttle',
    '-r', 
    jump_var.profile,
    jump_var.cidr, 
    '-vv' 
  ])
  utils_var.allow_exist = True
  return False
