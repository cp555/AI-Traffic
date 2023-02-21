import pandas as pd
import numpy as np
from Network import Network
from Controller import MaxPressureController
from Controller import dqnController
import traci
import os
import sys
import json
from analysis import updateMetrics

if __name__ == "__main__":

    controller_type = "max_pressure"

    # LOAD SUMO STUFF
    #cfgfilename = "test_1110.sumo.cfg" 
    cfgfilename = "SUMO_Network.sumocfg"



    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path,"network",cfgfilename)
    print(filepath)

    sumoCmd = ["sumo", "-c", filepath]
    # sumoCmd = ["sumo-gui", "-c", filepath]  # if you want to see the simulation

    # initialize the network object and controller object
    tracilabel = "sim1"
    traci.start(sumoCmd, label=tracilabel)
    conn = traci.getConnection(tracilabel)

    network = Network(filepath, conn)
    controller = "max_pressure"
    if controller_type == "max_pressure":
        controller = MaxPressureController()
    else:
        controller = dqnController()

    step = 0

    metrics_lane = {}
    metrics_vehicle = {}
    while conn.simulation.getMinExpectedNumber() > 0:
        conn.simulationStep()
        if step > 1 and step % 30 == 0:

            # get current state

            intersections = list(network.network.keys())
            print("intersections" + str(intersections))
            print("in step " + str(step))
            for i in range(len(intersections)):
                intersection = intersections[i]
                state = network.getState(conn,intersection)
                geometry = network.getGeometry(intersection)

                # get maxpressure controller
                control = controller.getController(geometry,state)
                print("   " + intersection + " light list : " + str(control))
                # update the state of the network
                network.applyControl(control,conn,intersection)      
                
                #########write_state_to_file(state)   
                #metrics = updateMetrics(conn,metrics,state,geometry)
            print()
            print()
           


            # write_state_to_file(state)
            metrics_lane = updateMetrics(
                step, conn, metrics_lane, state, network.allLaneId, key='lane')
            metrics_vehicle = updateMetrics(
                step, conn, metrics_vehicle, state, network.allLaneId, key='vehicle')

        # RUN Data Analysis
        step += 1


    with open("metrics_lane.json", "w") as outfile:
        json.dump(metrics_lane, outfile)
    with open("metrics_vehicle.json", "w") as outfile:
        json.dump(metrics_vehicle, outfile)

    traci.close(False)

