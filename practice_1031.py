import os, sys
import optparse

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
     sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary
import traci

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.set_defaults(verbose=True)
    opt_parser.add_option("--nogui", action="store_true",
                          default = False, help = "run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


def run():
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationstep()
        print(step)
        step += 1

    traci.close()
    sys.stdout.flush()


if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui ')

    traci.start([sumoBinary, "-c", "C:/Users/ZenBook/test.sumo.cfg",
                 "--tripinfo-output", "tripinfo.xml"])
    run()