from subprocess import call, Popen, PIPE, run

from tools.utils import utils
from tools.dtos.ssh_var import var

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
  var.profile = utils.render_choices(get_profiles())
  if var.profile != False:
    return True
  return False

def set_ssh():
  run([ 
    'ssh', var.profile 
  ])
  return False
