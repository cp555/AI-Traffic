'''
Author: sh0829kk 381534335@qq.com
Date: 2023-02-08 21:57:11
LastEditors: sh0829kk 381534335@qq.com
LastEditTime: 2023-02-15 15:59:02
FilePath: /AI-Traffic/run.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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
    cfgfilename = "test_1110.sumo.cfg"  # sys.argv[1]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, "network", cfgfilename)
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
            state = network.getState(conn)
            geometry = network.getGeometry()

            # get maxpressure controller
            control = controller.getController(geometry, state)

            # update the state of the network
            network.applyControl(control, conn)

            # print('vehicle', network.state["vehicleID"])

            # write_state_to_file(state)
            metrics_lane = updateMetrics(
                step, conn, metrics_lane, state, geometry, key='lane')
            metrics_vehicle = updateMetrics(
                step, conn, metrics_vehicle, state, geometry, key='vehicle')

        # RUN Data Analysis
        step += 1

    with open("metrics_lane.json", "w") as outfile:
        json.dump(metrics_lane, outfile)
    with open("metrics_vehicle.json", "w") as outfile:
        json.dump(metrics_vehicle, outfile)

    traci.close(False)
