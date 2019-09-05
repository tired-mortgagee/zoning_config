#!/usr/bin/python

import os
import re
import csv
import sys
import string
import argparse

#####
##### global variables
#####

set_targets = set([])
set_initiators = set([])
set_zones = set([])
dict_initiators = {}
dict_targets = {}
list_zones = []
string_zoneset = ""
string_vsan = ""
bool_debug = False

#####
##### classes
#####

class fc_node(object):
   def __init__(self, mode, name, hbas, wwpns):
      self.mode = mode 
      self.name = name
      self.hbas = hbas.split(",")
      self.wwpns = wwpns.split(",")
   def __eq__(self, other):
      if not isinstance(other,fc_node): return NotImplemented
      return (self.name == other.name)
   def __hash__(self):
      return (hash(self.name))

class zone(object):
   def __init__(self,members):
      self.members = members.split(",")
      self.members.sort()
   def __eq__(self, other):
      if not isinstance(other,zone): return NotImplemented
      return (not(not(len(set(self.members) & set(other.members)))))
   #def __hash__(self):
   #   self.members.sort()
   #   return (hash(string.join(self.members)))

#####
##### functions
#####

def parse_input_line(string_input,int_input):
   
   if(bool_debug): print "begin_procedure parse_input_line()"
   
   if(len(string.strip(string_input)) == 0):
      return
   list_input = csv.reader([string_input],skipinitialspace=True).next() 
   if((list_input[0] == 't' or list_input[0] == 'i') and len(list_input) != 4):
      sys.exit("error 0x101: incorrect number of arguments in input file on line number "+str(int_input))
   if(list_input[0] == "z" and len(list_input) != 2):
      sys.exit("error 0x10D: incorrect number of arguments in input file on line number "+str(int_input))
   if((len(list_input[0]) != 1) or (list_input[0] != "t" and list_input[0] != "i" and list_input[0] != "z")): 
      if((len(list_input[0]) != 2) or (list_input[0] != "zs")):   
         sys.exit("error 0x10E: incorrect syntax in first argument in input file on line number "+str(int_input))
  
   # initiator or target
   if(list_input[0] == 't' or list_input[0] == "i"):
      obj_regex = re.compile(r'[a-zA-Z0-9\-_]+')
      if(not(obj_regex.match(list_input[1]))):
         sys.exit("error 0x102: incorrect syntax in second argument in input file on line number "+str(int_input))
      if(len(list_input[2].split(",")) != len(list_input[3].split(","))):
         sys.exit("error 0x103: number of sub-arguments does not match in third argument and fourth argument in input file on line number "+str(int_input))
      obj_regex = re.compile(r'^[a-zA-Z0-9]+$')
      for string_hba in list_input[2].split(","):
         if(not(obj_regex.match(string.strip(string_hba)))):
            sys.exit("error 0x104: incorrect syntax in sub-argument "+string_hba+ " of third argument in input file on line number "+str(int_input))
      obj_regex = re.compile(r'^[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}$')
      for string_wwpn in list_input[3].split(","):
         if(not(obj_regex.match(string.strip(string_wwpn)))):
            sys.exit("error 0x104: incorrect syntax in sub-argument "+string_wwpn+ " of third argument in input file on line number "+str(int_input))
      # target
      if(list_input[0] == "t"):
         if(bool_debug): print "adding target "+list_input[1]+" "+list_input[2]+" "+list_input[3]
         obj_fc_node = fc_node("target",list_input[1],list_input[2],list_input[3])
         if(obj_fc_node not in set_targets): 
            set_targets.add(obj_fc_node)
         else:
            print "warning 0x106: target "+list_input[1]+" on line number "+str(int_input)+ " of input file is already defined, skipping"
         if(obj_fc_node in set_initiators):
            print "error 0x109: target "+list_input[1]+" on line number "+str(int_input)+ " of input file is already defined as an initiator"
      # initiator
      if(list_input[0] == "i"):
         if(bool_debug): print "adding initiator "+list_input[1]+" "+list_input[2]+" "+list_input[3]
         obj_fc_node = fc_node("initiator",list_input[1],list_input[2],list_input[3])
         if(obj_fc_node not in set_initiators):
            set_initiators.add(obj_fc_node)
         else:
            print "warning 0x107: initiator "+list_input[1]+" on line number "+str(int_input)+ " of input file is already defined, skipping"
         if(obj_fc_node in set_targets):
            print "error 0x10A: initiator "+list_input[1]+" on line number "+str(int_input)+ " of input file is already defined as a target"
   
   # zone
   if(list_input[0] == "z"):
      obj_regex = re.compile(r'[a-zA-Z0-9\-_]+')
      for string_member in list_input[1].split(","):
         if(not(obj_regex.match(string.strip(string_member)))):
            sys.exit("error 0x105: incorrect syntax in sub-argument "+string_member+ " of second argument in input file on line number "+str(int_input))
      obj_zone = zone(list_input[1])
      if(bool_debug): print "adding zone "+list_input[1]
      if(obj_zone not in set_zones):
         set_zones.add(obj_zone)
      else:
         print "warning 0x108: zone "+list_input[1]+" on line number "+str(int_input)+ " of input file is already defined, skipping"
   
   # zoneset
   if(list_input[0] == "zs"):
      obj_regex = re.compile(r'[a-zA-Z0-9\-_]+')
      if(not(obj_regex.match(list_input[1]))):
         sys.exit("error 0x10B: incorrect syntax in second argument in input file on line number "+str(int_input))
      obj_regex = re.compile(r'[0-9]+')
      if(not(obj_regex.match(list_input[2]))):
         sys.exit("error 0x10C: incorrect syntax in third argument in input file on line number "+str(int_input))
      global string_zoneset
      global string_vsan
      string_zoneset = list_input[1]
      string_vsan = str(list_input[2])

   if(bool_debug): print "end_procedure parse_input_line()"

def validate_zone_members():
   for obj_zone in set_zones:
      for obj_zone_member in obj_zone.members:
         if((fc_node("",obj_zone_member,"","") not in set_initiators) and (fc_node("",obj_zone_member,"","") not in set_targets)):
            sys.exit("error 0x201: initiator or target "+obj_zone_member+ " is not defined")
   if((string_zoneset=="") or (string_vsan=="")):
      sys.exit("error 0x20B: zoneset information is not defined")


def write_aliases():
   print ""
   print "### device-aliases" 
   for obj_fc_node in set_targets:
      for int_index in range(0,len(obj_fc_node.hbas)): 
         print "device-alias name "+obj_fc_node.name+"_"+obj_fc_node.hbas[int_index]+" pwwn "+obj_fc_node.wwpns[int_index]
         dict_targets[obj_fc_node.name] = obj_fc_node
   for obj_fc_node in set_initiators:
      for int_index in range(0,len(obj_fc_node.hbas)): 
         print "device-alias name "+obj_fc_node.name+"_"+obj_fc_node.hbas[int_index]+" pwwn "+obj_fc_node.wwpns[int_index]
         dict_initiators[obj_fc_node.name] = obj_fc_node

def write_zones():
   print ""
   print "### zones"
   for obj_zone in set_zones:
      dict_zone_initiators = {}
      dict_zone_targets = {}
      for obj_zone_member in obj_zone.members:
         if obj_zone_member in dict_initiators:
            dict_zone_initiators[obj_zone_member] = dict_initiators[obj_zone_member].hbas
         if obj_zone_member in dict_targets:
            dict_zone_targets[obj_zone_member] = dict_targets[obj_zone_member].hbas
      for obj_initiator in dict_zone_initiators:
         for string_hba in dict_zone_initiators[obj_initiator]:
            for obj_target in dict_zone_targets:
               print "zone name "+obj_initiator+"_"+string_hba+"_"+obj_target+" vsan "+string_vsan
               print " member device-alias "+obj_initiator+"_"+string_hba
               for string_thba in dict_zone_targets[obj_target]:
                  print " member device-alias "+obj_target+"_"+string_thba
               list_zones.append(obj_initiator+"_"+string_hba+"_"+obj_target)
            
def write_zoneset():
   print ""
   print "### zoneset"
   print "zoneset name "+string_zoneset+" vsan "+string_vsan
   for string_zone in list_zones:
      print " member "+string_zone
   print " exit"
   print "zoneset activate "+string_zoneset+" vsan "+string_vsan

#####
##### main
#####

# argparse instantiation
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="the input file with the initiator and zoning information")
ns_args = parser.parse_args()

# parse inputs
if(not(os.path.exists(ns_args.input_file) and os.path.isfile(ns_args.input_file))):
   sys.exit("error 0x001: file " + ns_args.input_file + " does not exist")

with open(ns_args.input_file, 'r') as file:
   string_data = file.read()
list_data = string_data.split("\n")

int_line_number = 1
for string_line in list_data:
   parse_input_line(string_line,int_line_number)
   int_line_number = int_line_number + 1

validate_zone_members()
write_aliases()
write_zones()
write_zoneset()

if(bool_debug):
   print "# dump targets"
   for obj_fc_node in set_targets:
      print obj_fc_node.name + " " + obj_fc_node.mode + " " + ",".join(obj_fc_node.hbas) + " " + ",".join(obj_fc_node.wwpns)
   print "# dump initiators"
   for obj_fc_node in set_initiators:
      print obj_fc_node.name + " " + obj_fc_node.mode + " " + ",".join(obj_fc_node.hbas) + " " + ",".join(obj_fc_node.wwpns)
   print "# dump zones"
   for obj_zone in set_zones:
      print string.join(obj_zone.members)
