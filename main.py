from distutils.command.clean import clean
from lib2to3.pgen2.literals import simple_escapes
import sys
import subprocess
import sumolib

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

    net = sumolib.net.readNet(NET_FILE);
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

    print("calling DUA-router ⚙ "); 
    # print(DUAROUTER_ARGS);
    sys.stdout.flush();
    subprocess.run(DUAROUTER_ARGS);
    sys.stdout.flush();

    print('Completed ... ✈ '); 


if __name__ == "__main__":
    main()