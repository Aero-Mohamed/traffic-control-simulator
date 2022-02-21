import os, sys
import sumolib

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

#  Convert Longitute & Latitute to Neighboring Lane ID - Edge ID
# This Coordinate are pointing in (Faculty Engineering Cairo University) 🌎  Street
lat     = 30.026797;
lon     = 31.210914;
# load the network file
net = sumolib.net.readNet('cu.net.xml');
# Convert to the local x, y coordinates
x, y = net.convertLonLat2XY(lon, lat);
# fine the closest Edge
edges = net.getNeighboringEdges(x, y, 100);

destanceError = 0;
closestEdge = '';
if(len(edges)):
    closestEdge = edges[0][0];
    destanceError = edges[0][1];
else:
    exit();

for i in edges:
    if(i[1] < destanceError):
        closestEdge = i[0];
        destanceError = i[1];

print("DestanceError: ", destanceError);
print("Edge: ", closestEdge);









