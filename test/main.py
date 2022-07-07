import sys
import random
import subprocess
import os
from xml.dom import minidom
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'));
    
import sumolib
# import traci
# import mysql.connector
# import requests


# Inputs
TEST_NAME_PREFIX = '45PercentClient';
NET_FILE = './../network/cu.net.xml';
RANDOM_TRIP_FILE = './randomTrips.rou.xml';
OUTPUT_TRIP_FILE = './'+TEST_NAME_PREFIX+'/trips.trips.xml';

# Setup Folders 🧮 
if(not os.path.isdir('./'+TEST_NAME_PREFIX)):
    os.mkdir(TEST_NAME_PREFIX);

# DUArouter Inputs ✏ 
DUAROUTER = sumolib.checkBinary('duarouter');
OUTPUT_ROUTE_FILE = './'+TEST_NAME_PREFIX+'/routes.rou.xml';
DUAROUTER_ARGS = [DUAROUTER, 
    '--net-file', NET_FILE,
    '--route-files', OUTPUT_TRIP_FILE,
    '--begin', str(0),
    '--end', str(3600), # An Hour 
    '-o', OUTPUT_ROUTE_FILE,
    '--ignore-errors',
    '--no-step-log',
    '--no-warnings',
];


# Simulation Inputs
MAX_SIMULATION_STEPS    = 3600;
STEP                    = 1;
SUBSCRIBED_TARGET_VEH   = False;

def get_options(args=None):
    optParser = sumolib.options.ArgumentParser(description="Generate Route based on origin-destination points.")
    # Updated
    optParser.add_argument("--odEdges", type=str,help="Peers of Orgigin/Destination Edges IDs Seperated by comman (,) Text File");
    optParser.add_argument("--clientPercentage", type=int,help="Percentage of Client on the network");
    options = optParser.parse_args(args=args);
    return options

def tuple2Arr(tup):
    arr = [];
    arr.append(tup);
    return [x for xs in arr for x in xs];

def inputOptionODEdge2Arr(odEdgesFile):
    odEdges = [];
    with open(odEdgesFile) as fp:
        Lines = fp.readlines();
        for line in Lines:
            if(line != "\n"):
                odEdges.append(line.strip().split(","));
    return odEdges;


def main(options):
    SUBSCRIBED_TARGET_VEH = False;
    """
        Parse the Network file
    """
    print("Reading Network ⚙ ");
    net = sumolib.net.readNet(NET_FILE);
    """
        1. Generate trip file
    """
    print("Generating Trips ⚙ ");
    trips = inputOptionODEdge2Arr(options.odEdges);
    clientPercentage = options.clientPercentage;
    addationalTripsCount = int((100 - clientPercentage) * len(trips) / clientPercentage);
    print('RequiredRandom  = '+ str(addationalTripsCount));

    RandomTripsOriginDestList = [];
    randomTripsFILE = minidom.parse(RANDOM_TRIP_FILE);
    RTF_routes = randomTripsFILE.getElementsByTagName('routes')
    RTF_vehicle = RTF_routes[0].getElementsByTagName('vehicle');
    for idx in range(0, len(RTF_vehicle)):
        vRoute = RTF_vehicle[idx].getElementsByTagName('route');
        vRoute = vRoute[0];
        vRoute = vRoute.getAttribute('edges').split(' ');
        origin = vRoute[0];
        dest = vRoute[-1];
        RandomTripsOriginDestList.append([origin, dest]);
        
    random.shuffle(RandomTripsOriginDestList);
    additionalTrips = RandomTripsOriginDestList[0: addationalTripsCount];
    print('Clients = '+ str(len(trips)));
    print('Random  = '+ str(len(additionalTrips)));
    trips = trips + additionalTrips;

    with open(OUTPUT_TRIP_FILE, 'w') as fouttrips:
        sumolib.writeXMLHeader(fouttrips, "$Id$", "routes");
        for idx,trip in enumerate(trips):
            label = "%s%s" % ('Trip-', idx+1);
            depart = sumolib.miscutils.parseTime(0)
            attrFrom = ' from="%s"' % trip[0];
            attrTo = ' to="%s"' % trip[1];
            combined_attrs = attrFrom + attrTo;
            fouttrips.write('    <trip id="%s" depart="%.2f"%s/>\n' % (
                        label, depart, combined_attrs))

        fouttrips.write("</routes>\n");


    """
        Run The DUA-router to generate trip route
        In term of edges identifires
    """
    print("calling DUA-router ⚙ "); 
    # print(DUAROUTER_ARGS);
    sys.stdout.flush();
    subprocess.run(DUAROUTER_ARGS);
    sys.stdout.flush();

    print('Completed ... ✈ '); 
    return True;

if __name__ == "__main__":
    options = get_options();
    if not main(options):
        sys.exit(1)