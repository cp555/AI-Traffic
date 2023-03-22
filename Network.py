import pandas as pd
import numpy as np
from sumolib import checkBinary
import traci
import os, sys
import optparse


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
    

    self.network = {}
    self.DQNgeometry = {}
    self.allLaneId = []
    step = 0
    i = 0
    allLaneId = []
    intersections = conn.trafficlight.getIDList()
    for i in range(len(intersections)):
      self.network[intersections[i]] = {"geometry": {}, "state" : {}}

      list_links = trafficlight_link(intersections[i], conn)

      LaneID = getLaneID(list_links)
      for k in range(len(LaneID)):
        allLaneId.append(LaneID[k])
      numberOfLane = len(LaneID)
      allnumberofLane = len(set(allLaneId))
      conn.trafficlight.setRedYellowGreenState(intersections[i], "rrrrrrrrrrrr")

      light_list = trafficlight_light(intersections[i], conn)

      phase_matrix = trafficlight_phase(list_links, light_list)

      length_lanes = {}   # map from lane_id to length of it
      lane_pairs = {}     # map from upper_lane_id to down_lane_id
      pressure_map = {}   # map from pair of lanes'( one stream)' to pressure
      vehicles_lanes = []
      res = []


      for j in range(len(LaneID)):
        each_length = conn.lane.getLength(LaneID[j]) # get current length
        length_lanes[LaneID[j]] = each_length # put into a map
                  
      # forming the map from pair of lanes'( one stream)' to the number of vehicles         
      for x in range(len(list_links)):                                      
          upper_to_down = list_links[x][0] + "," + list_links[x][1]   # forming the key: upper_lane_id + comma + down_lane_id
          pressure_map[upper_to_down] = 0
      step += 1


      self.network[intersections[i]]["geometry"]["LaneID"] = LaneID
      self.network[intersections[i]]["geometry"]["pressure_map"] = pressure_map
      self.network[intersections[i]]["geometry"]["length_lanes"] = length_lanes
      self.network[intersections[i]]["geometry"]["list_links"] = list_links
      self.network[intersections[i]]["geometry"]["phase_matrix"] = phase_matrix
      self.network[intersections[i]]["geometry"]["numberOfLane"] = numberOfLane
      self.network[intersections[i]]["geometry"]["length_lanes"] = length_lanes
      self.network[intersections[i]]["geometry"]["light_list"] = light_list
      self.network[intersections[i]]["geometry"]["open_phases_map"] = {1:[1,5],2:[2,6],3:[3,7],4:[4,8],5:[1,5],6:[2,6],7:[3,7],8:[4,8]}

    DQN_list_links = []
    DQN_light_list = []
    DQN_phase_matrix = {}
    for i in range(len(intersections)):
        DQN_list_links.append(trafficlight_link(intersections[i],conn))
        DQN_light_list.append(trafficlight_light(intersections[i],conn))
        DQN_phase_matrix[intersections[i]] = trafficlight_phase(DQN_list_links[i], DQN_light_list[i])

    self.allLaneId = list(set(allLaneId))
    self.allnumberofLane = allnumberofLane
    self.intersections = intersections
    self.DQNgeometry["DQN_list_links"] = DQN_list_links
    self.DQNgeometry["DQN_light_list"] = DQN_light_list
    self.DQNgeometry["DQN_phase_matrix"] = DQN_phase_matrix
    self.DQNgeometry["intersections"] = intersections
  
  def DQN_getstate(self, conn, action):
    number_each_lane = {}
    for x in range(self.allnumberofLane):  
        total_number = conn.lane.getLastStepVehicleNumber(self.allLaneId[x])
        number_each_lane[self.allLaneId[x]] = total_number
            
    number_each_lane_list = list(number_each_lane.values())            

    DQN_action =[]
    for x in range(512):   
        if x == action :
            DQN_action.append(1)
        else:
            DQN_action.append(0)


    num_each_lane_arr = np.array(number_each_lane_list)
    num_each_lane_arr = num_each_lane_arr.reshape(1, 60, 1)

    DQN_action_arr = np.array(DQN_action)
    DQN_action_arr = DQN_action_arr.reshape(1, 512, 1)
      
    return [num_each_lane_arr, DQN_action_arr]

  def getVehicleNum(self, conn):
    VehicleNum = 0
    for i in range(self.allnumberofLane):
        VehicleNum += conn.lane.getLastStepVehicleNumber(self.allLaneId[i])

    return VehicleNum

  def getHaltingNum(self, conn):
    HaltingNum = 0
    for i in range(self.allnumberofLane):
        HaltingNum += conn.lane.getLastStepHaltingNumber(self.allLaneId[i])

    return HaltingNum
  def get_options(self):
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                            default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

  def getGeometry(self,intersection):
    return self.network[intersection]["geometry"]

  def getState(self,conn,intersection):
    vehicle_number_each_lane = {}                # map from lane_id to number of vehicles
    for x in range(self.network[intersection]["geometry"]["numberOfLane"]):  
        lane_length = conn.lane.getLength(self.network[intersection]["geometry"]["LaneID"][x])                    # extract length and number of
        total_number = conn.lane.getLastStepVehicleNumber(self.network[intersection]["geometry"]["LaneID"][x])    # vehicles in each lane
        vehicle_number_each_lane[self.network[intersection]["geometry"]["LaneID"][x]] = total_number
    self.network[intersection]["state"]["vehicle_number_each_lane"] = vehicle_number_each_lane
    VehicleID = conn.vehicle.getIDList()
    self.network[intersection]["state"]["vehicleID"] = VehicleID
    return self.network[intersection]["state"]
  
  def applyControl(self,controller,conn,intersection):
    RedYellowGreenState = ''.join(str(e) for e in controller)
    conn.trafficlight.setRedYellowGreenState(intersection, RedYellowGreenState)
    self.network[intersection]["geometry"]["light_list"] = controller
     


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

def getLaneID(links):
  res = []
  for i in range(len(links)):
    res.append(links[i][0])
    res.append(links[i][1])
  return res

def trafficlight_light(junction,conn):
  lights = conn.trafficlight.getRedYellowGreenState(junction)
  light_list = list(lights)
  # ex:['r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r']
  
  return light_list

def trafficlight_phase(list_links, light_list):  #putting the link, phase, and light into a matrix
  a = 0  # phase id
  w = len(list_links)
  h = 3
  Matrix = [[0 for x in range(w)] for y in range(h)] 
  
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

  