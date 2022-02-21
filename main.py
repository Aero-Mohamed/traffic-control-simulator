import sumolib

## Inputs
NET_FILE = './network/cu.net.xml';
OUTPUT_TRIP_FILE = './outputs/trips.trips.xml';

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
            "lon"   : 31.20873,
            "lat"   : 30.033228
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



if __name__ == "__main__":
    main()