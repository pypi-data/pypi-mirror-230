import socket
import time
import platform
from simple_term_menu import TerminalMenu
from subprocess import call
from os.path import expanduser

from tools.dtos.utill_var import var as utils_var
from tools.dtos.jump_var import var as jump_var
from tools.dtos.k8_var import var as k8_var
from tools.utils.k8_utils import *

def render_choices(options:list):
  options.append("Back")
  terminal_menu = TerminalMenu(options)
  menu_entry_index = terminal_menu.show()
  result = options[menu_entry_index]
  if "Back" in result :
    return False
  return result

def get_executable():
  if platform.system()=='Darwin':
    executable = "/bin/zsh"
  else:
    executable = "/bin/bash"
  return executable

def get_config_path(path):
  path = path.split("~")[1]
  return expanduser("~")+path

def routing(gateway_ip, cidr):
  try:
    if platform.system()=='Darwin':
      call([
        'sudo',
        'route',
        'add',
        str(cidr),
        str(gateway_ip)
      ])
      call([
        'sudo',
        'route',
        'change',
        str(cidr),
        str(gateway_ip)
      ])
    else:
      call([
        'sudo',
        'ip',
        'route',
        'add',
        str(cidr),
        'via',
        str(gateway_ip)
      ])
      call([
        'sudo',
        'ip',
        'route',
        'replace',
        str(cidr),
        'via',
        str(gateway_ip)
      ])
  except:
    raise "Route error!"

def shell_exec(cmd:str):
  stdout, stderr = subprocess.Popen(
    cmd, 
    shell=True, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
  ).communicate()
  if stderr.decode('UTF-8') != "" and "Warning" not in stderr.decode('UTF-8'):
    raise Exception(f'Remote execute error: {stderr.decode("UTF-8")}')
  return stdout.decode('UTF-8')

def get_default_gw_ip():
  # osx 
  def get_default_gw_ip_osx():
      cmd = "networksetup -listallhardwareports"
      physical_interface_raw = shell_exec(cmd)
      physic_interfaces = []
      for interface in physical_interface_raw.split("\n"):
        if "Device" in interface:
          physic_interfaces.append(interface.split("Device: ")[1])
      cmd = "netstat -nr -f inet"
      route_list_raw = shell_exec(cmd)
      for item in route_list_raw.split("\n"):
        for interface in physic_interfaces:
          if (interface in item) and ("default" in item or "0.0.0.0/1" in item or "0.0.0.0/0" in item):
            return item.split()[1]
  # ubuntu
  def get_default_gw_ip_ubuntu():
    cmd = "ls -l /sys/class/net/ |grep -v virtual"
    physical_interface_raw = shell_exec(cmd)
    physic_interfaces = []
    for interface in physical_interface_raw.split("\n"):
      if "net" in interface:
        physic_interfaces.append(interface.split("net/")[1])
    cmd = "ip route list"
    route_list_raw = shell_exec(cmd)
    for item in route_list_raw.split("\n"):
      for interface in physic_interfaces:
        if (interface in item) and ("default" in item or "0.0.0.0/1" in item or "0.0.0.0/0" in item):
          return(item.split()[2])
  try:
    if platform.system()=='Darwin':
      return get_default_gw_ip_osx()
    return get_default_gw_ip_ubuntu()
  except:
    raise "Get gateway ip error!"

def del_route(gateway_ip, cidr):
  try:
    if platform.system()=='Darwin':
      call([
        'sudo',
        'route',
        'delete',
        str(cidr),
        str(gateway_ip)
      ])
    else:
      call([
        'sudo',
        'ip',
        'route',
        'del',
        str(cidr),
        'via',
        str(gateway_ip)
      ])
  except:
    raise "Route error!"

def exist_handler(signum, frame):
  if jump_var.gateway_ip != None:
    del_route(jump_var.gateway_ip,jump_var.cidr)
  if utils_var.allow_exist == False:
    utils_var.allow_exist = True
  else:
    exit(1)

def ex_stacks(stacks: list): 
  i = 0
  while i < len(stacks) and i!= -1:
    r = stacks[i]()
    if r == True :
      i += 1
    elif r == False :
      i-=1
      
  if i != -1:
    return True
  return False

def is_port_open(host:str, port:int, max_retry: int=5):
  result = 1
  for i in range(max_retry):
    print("Testing ...")
    time.sleep(2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destination = (host, port)
    result = s.connect_ex(destination)
    if result == 0:
      break
  if result != 0:
    return False
  return True

def fetch_and_update_kubeconfig():
  connection = is_port_open(k8_var.ksapi_ip, 80)
  if connection:
    k8_var.token = get_kubesphere_access_token(
      k8_var.ksapi_ip,
      k8_var.username,
      k8_var.password
    )
    k8_var.old_kubeconfig = load_kubeconfig_file()
    k8_var.new_kubeconfig = requests_kubeconfig(
      k8_var.ksapi_ip,
      k8_var.token
    )
    updated_kubeconfig = update_kube_context(
      k8_var.old_kubeconfig,
      k8_var.new_kubeconfig,
      jump_var.profile
    )
    save_kubeconfig(updated_kubeconfig)
    print("Configured!")
