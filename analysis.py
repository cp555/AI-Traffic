'''
Author: sh0829kk 381534335@qq.com
Date: 2023-02-08 15:25:37
LastEditors: sh0829kk 381534335@qq.com
LastEditTime: 2023-02-15 15:59:15
FilePath: /AI-Traffic/test.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# /usr/bin/python


def updateMetrics(step, conn, metrics, state, geometry, key):
    if key == 'lane':
        for lane in geometry["LaneID"]:
            if lane not in metrics:
                metrics[lane] = {'step': [], 'WaitingTime': [], 'CO2': []}
            metrics[lane]['step'].append(step)
            metrics[lane]['WaitingTime'].append(conn.lane.getWaitingTime(lane))
            metrics[lane]['CO2'].append(conn.lane.getCO2Emission(lane))
    if key == 'vehicle':
        for vehicle in state["vehicleID"]:
            if vehicle not in metrics:
                metrics[vehicle] = {
                    'step': [], 'TimeLoss': [], 'AccumulatedWaitingTime': []}
            metrics[vehicle]['step'].append(step)
            metrics[vehicle]['TimeLoss'].append(
                conn.vehicle.getTimeLoss(vehicle))
            metrics[vehicle]['AccumulatedWaitingTime'].append(conn.vehicle.getAccumulatedWaitingTime(vehicle))
    return metrics

    # track time-step, vehicle-id, control-signal
    # metrics-land & metrics-vehicle
    #
