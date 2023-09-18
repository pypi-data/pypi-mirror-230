from tools.functions import aws, k8, ssh, jump, k8
import signal

from tools.utils import utils

def eksm():
  stacks = [
    aws.set_profile,
    aws.set_region,
    aws.set_eks_name
  ]
  if utils.ex_stacks(stacks) :
    aws.set_cluster()  

def sshm():
  stacks = [
    ssh.set_profile,
    ssh.set_ssh
  ]
  if utils.ex_stacks(stacks) :
    ssh.set_profile() 

def jumpm():
  stacks = [
    jump.set_profile,
    jump.set_cidr,
    jump.set_proxy
  ]
  if utils.ex_stacks(stacks) :
    jump.set_cidr()

def k8m():
  stacks = [
    k8.set_profile_gw_username_pass,
    k8.create_connection
  ]
  if utils.ex_stacks(stacks) :
    k8.set_profile_gw_username_pass

signal.signal(signal.SIGINT, utils.exist_handler)
