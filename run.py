'''
Author: sh0829kk 381534335@qq.com
Date: 2023-02-08 21:57:11
LastEditors: sh0829kk 381534335@qq.com
LastEditTime: 2023-02-13 16:20:33
FilePath: /AI-Traffic/run.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import pandas as pd
import numpy as np
from Network import Network
from Controller import MaxPressureController
from Controller import dqnController
import traci
import os, sys
import json
if __name__ == "__main__":

    controller_type = "max_pressure"

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
    #sumoCmd = ["sumo-gui", "-c", filepath]  # if you want to see the simulation

    # initialize the network object and controller object
    tracilabel = "sim1"
    traci.start(sumoCmd, label=tracilabel)
    conn = traci.getConnection(tracilabel)

    network = Network(filepath, conn)
    controller = "max_pressure"
    if controller_type=="max_pressure":
        controller = MaxPressureController()
    else :
        controller = dqnController()
    # print("Initial traffic light is " + str(network.geometry["light_list"]))

    step = 0

    metrics = {'WaitingTime':[],'AccumulatedWaitinTime':[],'CO2':[],'TimeLoss':[]}
    while conn.simulation.getMinExpectedNumber() > 0:
        conn.simulationStep()
        if step > 1 and step%30 == 0: 


            # print(step)
            # get current state
            state = network.getState(conn)
            geometry = network.getGeometry()

            # print("Current traffic light is " + str(geometry["light_list"]))

            # get maxpressure controller
            control = controller.getController(geometry,state)

            # update the state of the network
            network.applyControl(control,conn)      

            print('vehicle',network.geometry["VehicleID"])
            
            #########write_state_to_file(state)   
            for lane in network.geometry["LaneID"]:
                metrics['WaitingTime'].append(traci.lane.getWaitingTime(lane))
                metrics['CO2'].append(traci.lane.getCO2Emission(lane))
            # for vehicle in network.geometry["VehicleID"]:
            #     metrics['TimeLoss'].append(traci.getTimeLoss(vehicle))
           
     # traci.vehicle.getSpeed() for each lane
    # traci.getPosition()
    # traci.getTimeLoss()

    # metrics['getAccumulatedWaitingTime'] = traci.lane.getAccumulatedWaitingTime('5_0')
    
  
        ## RUN Data Analysis 
        step += 1
    # print(metrics)
    metrics = metrics.
    # print('Timeloss',traci.vehicle.getTimeLoss(7))


    traci.close(False)