#!/usr/bin/env python

#import argparse
import subprocess
import os
import sys

from ansible.inventory import Inventory
from ansible.inventory.host import Host
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.errors import AnsibleError

from os import listdir
from os.path import isfile, join

inventory_base='./inventory'
ssh_cmd_line = ['ssh']

def help():
   print('''
Ansible ssh helper for accessing inventory nodes directly:
Command line:
$ ansible-ssh [host] [any ssh-arguments]

Description:
This tool will parse all inventory files in ./inventory and for each it will try to find given host.
If found it will use first match and try to ssh to given host.
   ''')
   exit(0)

def get_inventory_files(base):
  inventory_files = [f for f in listdir(base) if isfile(join(base, f))]

  if not inventory_files:
    raise Exception("No inventory file present.")
  return inventory_files

def find_host_in_inventory(base, host_name):
  loader = DataLoader()
  var_manager = VariableManager()
  host_vars = None
  host_info = []

  for i in get_inventory_files(base):
    try:
      inv = Inventory(host_list='%s/%s' %(base, i), loader=loader, variable_manager=var_manager)
      host_vars = inv.get_vars(host_name)
    except AnsibleError:
      continue

  if host_vars:
    ssh_host = host_vars.get('ansible_ssh_host', None)
    ssh_user = host_vars.get('ansible_ssh_user', None)
    ssh_key  = host_vars.get('ansible_ssh_private_key_file', None)
    ssh_port = host_vars.get('ansible_ssh_port', 22)
  else:
    raise Exception('Host %s is not present in any inventory %s' %(host_name, ' '.join(get_inventory_files(base))))

  if not ssh_host or not ssh_user:
    raise Exception('ansible_ssh_host and ansible_ssh_user required.')

  host_info.append(str('%s@%s' %(ssh_user, ssh_host)))

  if ssh_key:
    ssh_key = os.path.expanduser(ssh_key)

    if not os.path.isabs(ssh_key):
      ssh_key = os.path.abspath(ssh_key)

    if os.path.exists(ssh_key):
      host_info += ['-i', str(ssh_key)]
    else:
      print ("SSH key %s doesn't exists please check path." %(ssh_key))

  if ssh_port:
    if not int(ssh_port) == min(max(int(ssh_port), 0), 65535):
      raise Exception('Incorrect port number given')
    host_info += ['-p', str(ssh_port)]

  return host_info

if len(sys.argv) <= 1:
  help()

host = sys.argv[1]

#parser = argparse.ArgumentParser(description='Ssh client wrapper for ansible inventory files')
#parser.add_argument('-i', dest='inventory', action='store', help='Inventory file')
#parser.add_argument('-H', dest='host', action='store', help='Host name to login to')
#parser.add_argument('-k', dest='key', action='store', help='Path to private key')

#args = parser.parse_args()

ssh_cmd_line += find_host_in_inventory(inventory_base, host)

ssh_cmd_line += sys.argv[2::]

if len(ssh_cmd_line) < 2:
  print("I can't find host or user are you sure that we are in ansible repo directory ?")
  exit(1)

subprocess.call(ssh_cmd_line)
