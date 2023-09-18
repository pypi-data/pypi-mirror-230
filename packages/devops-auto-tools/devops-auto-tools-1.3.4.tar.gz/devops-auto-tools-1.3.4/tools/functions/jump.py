from subprocess import call

from tools.utils import utils
from tools.dtos.jump_var import var
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

def get_cidr():
  return [
    "All traffics (Only work without vpn)",
    "Specific cidrs"
  ]

def set_profile():
  var.profile = utils.render_choices(get_profiles())
  if var.profile != False:
    return True
  return False

def set_cidr():
  var.cidr = utils.render_choices(get_cidr())
  if var.cidr != False:
    if "All traffics (Only work without vpn)" in var.cidr:
      var.cidr = "0.0.0.0/0"
    else:
      var.cidr = input("Enter cidr: ")
    var.gateway_ip = utils.get_default_gw_ip()
    return True
  return False
  
def set_proxy():
  utils_var.allow_exist = False
  utils.routing(var.gateway_ip, var.cidr)
  call([ 
    'sshuttle',
    '-r', 
    var.profile,
    var.cidr, 
    '-vv' 
  ])
  utils_var.allow_exist = True
  return False
