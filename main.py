import sys
import subprocess
import os
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'));
    
import sumolib
import traci
import mysql.connector
import requests


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
## Defult for the program. 🍭
origin_destination_matrix = [
    # [
    #     ## Origin
    #     {
    #         "lon" : 31.210914,
    #         "lat" : 30.026797
    #     },
    #     ## Destination
    #     {
    #         "lon"   : 31.202546,
    #         "lat"   : 30.029341
    #     }
    # ]
];


def get_options(args=None):
    optParser = sumolib.options.ArgumentParser(description="Generate Route based on origin-destination points.")
    # Updated
    optParser.add_argument("--origin", type=str,help="Origin lat,lon");
    optParser.add_argument("--destination", type=str,help="Destination lat,lon");
    options = optParser.parse_args(args=args);
    return options


def connectDB():
    db = mysql.connector.connect(
        host="localhost",
        port=3307, 
        user="root", 
        password="",
        database="skywire"
    );
    return db;


def getCurrentTrips(db):
    cr = db.cursor();
    cr.execute("SELECT id, user_id, astext(origin) as origin, astext(destination) as destination FROM trips where arrived=0");
    res = cr.fetchall();
    return res;

def formatedTrips(res):
    for x in res:
        origin = x[2].replace('POINT(',"").replace(")", "").split(" ");
        destination = x[3].replace('POINT(',"").replace(")", "").split(" ");

        origin_destination_matrix.append([
            # Origin
            {
                "lat" : origin[0],
                "lon" : origin[1],
            },
            ## Destination
            {
                "lat" : destination[0],
                "lon" : destination[1],
            }
        ]);
        return x[1]; # Return the first Trip ID

def updateTripRoute(db, trip_id, tripRoute):
    cleanTripRouteTable(db, trip_id);
    cr = db.cursor();
    cr.executemany("INSERT INTO trip_routes (trip_id, position) VALUES (%s, ST_PointFromText(%s))", tripRoute);
    db.commit();
    print(cr.rowcount, "was inserted. 🙂 "); 


def cleanTripRouteTable(db, trip_id):
    print("Cleaning Trip Infromation From DB ⚙ ");
    cr = db.cursor();
    cr.execute("DELETE FROM trip_routes WHERE trip_id = "+str(trip_id)+"");
    db.commit();

def nofityServer():
    print("Notifying The Server ⚙ ");
    res = requests.post("http://skywire.com/api/v1/notifyClients", {});

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
        

def main(db):
    SUBSCRIBED_TARGET_VEH = False;
    """
        Parse the Network file
    """
    print("Reading Network ⚙ ");
    net = sumolib.net.readNet(NET_FILE);
    """
        1. convert origin-destination (lon, lat) matrix to be in term
        of edge identifier origin-destination pairs
        2. Generate trip file
    """
    print("Generating Trips ⚙ ");
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
    tripRoute = [];
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
            tripRoute.append([
                trip_id,
                "POINT("+str(lat)+" "+str(lon)+")"
            ]);
            # print("LatLng(", lat, ', ', lon, '),');
    """
        Send to Database server
    """
    updateTripRoute(db, trip_id, tripRoute);


    """
        Kindly ask server to inform clients with 
        the new routing information.
    """
    nofityServer();

            
    traci.close();
    print('Completed ... ✈ '); 

if __name__ == "__main__":
    db = connectDB();
    res = getCurrentTrips(db);
    trip_id = formatedTrips(res);

    if not main(db):
        sys.exit(1)