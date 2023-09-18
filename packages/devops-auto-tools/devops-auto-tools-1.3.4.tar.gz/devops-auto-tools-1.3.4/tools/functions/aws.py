from subprocess import call, Popen, PIPE
import json
import os

from tools.utils import utils
from tools.dtos.aws_var import var


def get_profiles():
  f = open(utils.get_config_path("~/.aws/credentials"), 'r')
  lines = f.readlines()
  f.close()
  profiles = []
  for line in lines:
    if "[" in line and "]" in line:
      profiles.append(line.split("[")[1].split("]")[0])
  return profiles

def get_region():
  return [
    "US East (N. Virginia)us-east-1",
    "US East (Ohio)us-east-2",
    "US West (N. California)us-west-1",
    "US West (Oregon)us-west-2",
    "Africa (Cape Town)af-south-1",
    "Asia Pacific (Hong Kong)ap-east-1",
    "Asia Pacific (Jakarta)ap-southeast-3",
    "Asia Pacific (Mumbai)ap-south-1",
    "Asia Pacific (Osaka)ap-northeast-3",
    "Asia Pacific (Seoul)ap-northeast-2",
    "Asia Pacific (Singapore)ap-southeast-1",
    "Asia Pacific (Sydney)ap-southeast-2",
    "Asia Pacific (Tokyo)ap-northeast-1",
    "Canada (Central)ca-central-1",
    "Europe (Frankfurt)eu-central-1",
    "Europe (Ireland)eu-west-1",
    "Europe (London)eu-west-2",
    "Europe (Milan)eu-south-1",
    "Europe (Paris)eu-west-3",
    "Europe (Stockholm)eu-north-1",
    "Middle East (Bahrain)me-south-1",
    "South America (São Paulo)sa-east-1",
  ]

def get_eks():
  process = Popen([
    'aws', 'eks', 
    '--profile', var.profile, 
    '--region', var.region, 
    'list-clusters'
  ], stdout=PIPE, stderr=PIPE)
  out, err = process.communicate()
  response = json.loads(out.decode('ascii','ignore'))
  return response["clusters"]

def set_profile():
  var.profile = utils.render_choices(get_profiles())
  if var.profile != False:
    # os.environ["AWS_PROFILE"] = var.profile
    return True
  return False

def set_region():
  var.region = utils.render_choices(get_region())
  if var.region != False:
    var.region = str(var.region).split(")")[1]
    os.environ["AWS_REGION"] = var.region
    return True
  return False

def set_eks_name():
  var.eks_name = utils.render_choices(get_eks())
  if var.eks_name != False:
    return True
  return False

def set_cluster():
  call([ 
    'aws', 'eks', 
    '--region', var.region, 
    '--profile', var.profile, 
    'update-kubeconfig', 
    '--name', var.eks_name 
  ])