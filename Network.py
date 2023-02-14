import pandas as pd
import numpy as np
from sumolib import checkBinary
import traci
import os, sys


# #set up SUMO env path
# os.environ['SUMO_HOME'] = '/usr/local/opt/sumo/share/sumo'
# if 'SUMO_HOME' in os.environ:
#         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#         sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

class Network:

  #self.traci

  ## constructor to initialize an network object
  #def __init__(self, traci,fgfilename):
  def __init__(self,cfgfilename, conn):
    

    self.geometry = {}
    self.state = {}   #map from link/lane id to number of vehicles

    step = 0
    i = 0
    LaneID = conn.lane.getIDList()
    numberOfLan = getLaneNumber(conn.lane.getIDList())
    conn.trafficlight.setRedYellowGreenState("node1", "rrrrrrrrrrrr")

    list_links = trafficlight_link("node1", conn)

    light_list = trafficlight_light("node1", conn)

    phase_matrix = trafficlight_phase(list_links, light_list)

    length_lanes = {}   # map from lane_id to length of it
    lane_pairs = {}     # map from upper_lane_id to down_lane_id
    pressure_map = {}   # map from pair of lanes'( one stream)' to pressure
    vehicles_lanes = []
    res = []

    for x in range(numberOfLan):  
            each_length = conn.lane.getLength(LaneID[x])  # get current length
            length_lanes[LaneID[x]] = each_length          # put into a map
            links = conn.lane.getLinks(LaneID[x])         # get links list of current lane
            if len(links) > 0 and links[0][-2] != 't':     # if it has a list and it's not u-turn
                lane_pairs[LaneID[x]] = links[0][0] + links[0][-2]    # put it into the map
                
    # forming the map from pair of lanes'( one stream)' to the number of vehicles         
    for key in lane_pairs:                                      
        upper_to_down = key + "," + lane_pairs[key][0:-1]   # forming the key: upper_lane_id + comma + down_lane_id
        pressure_map[upper_to_down] = 0
    step += 1


    self.geometry["LaneID"] = LaneID
    self.geometry["pressure_map"] = pressure_map
    self.geometry["length_lanes"] = length_lanes
    self.geometry["list_links"] = list_links
    self.geometry["phase_matrix"] = phase_matrix
    self.geometry["numberOfLan"] = numberOfLan
    self.geometry["length_lanes"] = length_lanes
    self.geometry["light_list"] = light_list
    
  def getGeometry(self):
    return self.geometry

  def getState(self,conn):
    vehicle_number_each_lane = {}                # map from lane_id to number of vehicles
    for x in range(self.geometry["numberOfLan"]):  
        lane_length = conn.lane.getLength(self.geometry["LaneID"][x])                    # extract length and number of
        total_number = conn.lane.getLastStepVehicleNumber(self.geometry["LaneID"][x])    # vehicles in each lane
        vehicle_number_each_lane[self.geometry["LaneID"][x]] = total_number
    self.state["vehicle_number_each_lane"] = vehicle_number_each_lane
    VehicleID = conn.vehicle.getIDList()
    self.state["vehicleID"] = VehicleID
    return self.state
  
  def applyControl(self,controller, conn):
    RedYellowGreenState = ''.join(str(e) for e in controller)
    conn.trafficlight.setRedYellowGreenState("node1", RedYellowGreenState)
    self.geometry["light_list"] = controller
     


#########################################################################################
##    helper method for extracting information of the network
def getLaneNumber(idList):
  res = 0
  for i in range(len(idList)):
      if idList[i][0] != ':':
          res = res + 1
  return res

def findItem(theList, item1, item2):
  return [(i) for (i, sub) in enumerate(theList) if item1 and item2 in sub]

def trafficlight_link(junction,conn):
  links = conn.trafficlight.getControlledLinks(junction)
  out = [item for t in links for item in t]
  list_links = [list(ele) for ele in out]
  for i in range(len(list_links)):
      list_links[i].pop(2)
      # ex:[['5_0', '-6_0'], ['5_1', '-6_1'], ['5_2', '2_2'], ['-2_0', '-1_0'], ['-2_1', '-1_1'], ['-2_2', '-6_2'], ['6_0', '-5_0'], ['6_1', '-5_1'], ['6_2', '-1_2'], ['1_0', '2_0'], ['1_1', '2_1'], ['1_2', '-5_2']]

  return list_links

def trafficlight_light(junction,conn):
  lights = conn.trafficlight.getRedYellowGreenState("node1")
  light_list = list(lights)
  # ex:['r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r']
  
  return light_list

def trafficlight_phase(list_links, light_list):  #putting the link, phase, and light into a matrix
  a = 0  # phase id
  w = len(list_links)
  h = 3
  Matrix = [[0 for x in range(w)] for y in range(h)] 
  #print(Matrix)
  
  for i in range(len(list_links)):
      Matrix[0][i] = list_links[i]
      
  for i in range(len(list_links)):
      if list_links[i][0][0] == list_links[i-1][0][0] and list_links[i][0][1] == list_links[i-1][0][1] and list_links[i][1][0] == list_links[i-1][1][0] and list_links[i][1][1] == list_links[i-1][1][1]:
          a -= 1
          # using the fisrt two chart of the two elements to defined whether their in the same phase
      a +=1
      Matrix[1][i] = a
      
  for i in range(len(list_links)):
      Matrix[2][i] = light_list[i]
      
  return Matrix

  