from Network import Network
# from Controller import Controller,MaxPressureController
# import pandas as pd
# import numpy as np
# from sumolib import checkBinary
import traci
import os, sys

#if __name__ == "__main__":

# controller_type = "max_pressure"

# LOAD SUMO STUFF
cfgfilename = "test_1110.sumo.cfg" # sys.argv[1]
print("access config file " + str(cfgfilename))

# os.environ['SUMO_HOME'] = '/usr/local/opt/sumo/share/sumo'
# if 'SUMO_HOME' in os.environ:
#         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#         sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

# print("2")

# os.environ['SUMO_HOME'] = '/usr/local/opt/sumo/share/sumo'

dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path,"network",cfgfilename)
sumoCmd = ["sumo", "-c", filepath]

# initialize the network object and controller object
tracilabel= "sim1"
traci.start(sumoCmd, label=tracilabel)
conn = traci.getConnection(tracilabel)


network = Network(filepath,'sim1')
controller = "max_pressure"
if controller_type=="max_pressure":
    controller = MaxPressureController()
else :
    controller = DQNXController()
print("Initial traffic light is " + str(network.geometry["light_list"]))




step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    if step > 1 and step%30 == 0: 


        print(step)
        # get current state
        state = network.getState(conn)
        geometry = network.getGeometry(conn)

        print("Current traffic light is " + str(geometry["light_list"]))

        # get maxpressure controller
        control = controller.getController(geometry,state)

        # update the state of the network
        network.applyControl(control,conn)      

        #########write_state_to_file(state)   

    ## RUN Data Analysis 
    step += 1



traci.close(False)