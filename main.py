from distutils.command.clean import clean
from lib2to3.pgen2.literals import simple_escapes
from re import L
import sys
import subprocess
import sumolib
import traci

# Inputs
NET_FILE = './network/cu.net.xml';
OUTPUT_TRIP_FILE = './outputs/trips.trips.xml';
# DUArouter Inputs ✏ 
DUAROUTER = sumolib.checkBinary('duarouter');
OUTPUT_ROUTE_FILE = './outputs/routes.rou.xml';
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



## Setup Manually for now 🙂 
origin_destination_matrix = [
    [
        ## Origin
        {
            "lon" : 31.210914,
            "lat" : 30.026797
        },
        ## Destination
        {
            "lon"   : 31.202546,
            "lat"   : 30.029341
        }
    ]
    
];

def tuple2Arr(tup):
    arr = [];
    arr.append(tup);
    return [x for xs in arr for x in xs];


def generateVehicleProperityKeysToRetrive():
    keys = [
        0x40,      # Speed - getSpeed
        0x72,      # Acceleration - getAcceleration
        0x42,      # Position 2D - getPosition
        0x50,      # Current Road ID - getRoadID
        0x51,      # Current Lane ID - getLaneID
        0x4f,      # Vehicle Type - getTypeID
        0x69,      # Current edge Index - getRouteIndex
        0x54,      # string cell array of the edges the vehicles route is made of - getRoute
        0x56,      # Position in the lane - getLanePosition
        0x84,      # The distance, the vehicle has already driven [m] - getDistance
        0x4b,      # vehicles signales - getSignals
        0x65,      # fuel consumption - getFuelConsumption
        0x71,      # electricity consumption - getElectricityConsumption
        0xb2,      # information about the wish to use subsequent lanes - getBestLanes
        0x45          # getColor   
    ];
    return keys;

def closestEdge(edges):
    closestEdge = edges[0];
    destanceError = edges[0][1];

    for i in edges:
        if(i[1] < destanceError):
            closestEdge = i;
            destanceError = i[1];
    return closestEdge;


def getODEdges(net, ODM): # Origin Destination Matrix 🚌 
    origin_destination_trips_by_edges = [];

    for trip in ODM:
        tripEdges = [];
        for i in trip:
            
            x, y = net.convertLonLat2XY(i['lon'], i['lat']);
            edges = net.getNeighboringEdges(x, y, 100);
            if(len(edges) == 0):
                continue;
            edge = closestEdge(edges);
            tripEdges.append(edge);

        origin_destination_trips_by_edges.append(tripEdges);

    return origin_destination_trips_by_edges;  
        

def main():
    SUBSCRIBED_TARGET_VEH = False;
    """
        Parse the Network file
    """
    net = sumolib.net.readNet(NET_FILE);
    """
        1. convert origin-destination (lon, lat) matrix to be in term
        of edge identifier origin-destination pairs
        2. Generate trip file
    """
    trips = getODEdges(net, origin_destination_matrix);
    with open(OUTPUT_TRIP_FILE, 'w') as fouttrips:
        sumolib.writeXMLHeader(fouttrips, "$Id$", "routes");
        for idx,trip in enumerate(trips):
            label = "%s%s" % ('Trip-', idx);
            depart = sumolib.miscutils.parseTime(0)
            attrFrom = ' from="%s"' % trip[0][0].getID();
            attrTo = ' to="%s"' % trip[1][0].getID();
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


    """
        Run Simulation & Extract (Lon & Lat) of the Trip
    """
    traci.start(["sumo", "-c", "network/simulation.sumo.cfg", "--start"]);

    while(traci.simulation.getMinExpectedNumber() > 0):
        traci.simulationStep();
        targetVeh = "Trip-0";

        vehicles = tuple2Arr(traci.vehicle.getIDList());
        if( targetVeh in vehicles):
            
            if(not SUBSCRIBED_TARGET_VEH):
                traci.vehicle.subscribe(targetVeh, generateVehicleProperityKeysToRetrive());
                SUBSCRIBED_TARGET_VEH = True;

            targetVehicleHandle = traci.vehicle.getSubscriptionResults(targetVeh);
            position = targetVehicleHandle[0x42];
            [lon, lat] = traci.simulation.convertGeo(position[0], position[1]);

            """
                Send to Database server
            """
            print("Lon: ", lon, ', Lat: ', lat);
    
    traci.close();

    print('Completed ... ✈ '); 

if __name__ == "__main__":
    main();