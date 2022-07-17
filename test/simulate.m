%% Init
clear
close all
clc
import traci.constants
%% Inputs
TEST_NAME_PREFIX = '2PercentClient';

%% Run Simulation
traci.start(['sumo-gui -c ./../network/simulation.sumo.cfg -r ./' TEST_NAME_PREFIX '/routes.rou.xml --start']);

SIM_STEPS = [1 3600];
beginTime = SIM_STEPS(1);
duration =  SIM_STEPS(2);
endTime =  SIM_STEPS(1) +  SIM_STEPS(2) - 1;
vehicleNumberPerTimeStep = zeros(1, duration);
everyTenSteps = 0;
ClientVehicleIDList = {'Trip-1', 'Trip-2', 'Trip-3', 'Trip-4', 'Trip-5', 'Trip-6', 'Trip-7', 'Trip-8', 'Trip-9', 'Trip-10'};

VehiclesPosition = containers.Map;
EdgeDensities = containers.Map;


%% Get All Edges Length/s
lanes = traci.lane.getIDList();
edgeLength = containers.Map;

for k=1:length(lanes)
    edgeID = traci.lane.getEdgeID(lanes{k});
    if ~isKey(edgeLength ,lanes{k})
        edgeLaneNumber = traci.edge.getLaneNumber(edgeID);
        edgeLength(edgeID) = [traci.lane.getLength(lanes{k}) edgeLaneNumber];
    end
end


%% Subscribe to All Edges 
edges = traci.edge.getIDList();
for k=1:length(edges)
    traci.edge.subscribe(edges{k}, {...
        %'0x13', ... % Occupancy
        '0x10' ... % lastStepVehiclesNumber
        %'0x15', ... % lastStepMeanVehiclesLength
    })
end

%% Simulation
i = 2;
while traci.simulation.getMinExpectedNumber() > 0
    
    % Update Edge Effort to be its current density
    % Ignore First Step
    
    if everyTenSteps == 10
        for e=1:length(edges)
            edge_length_laneNo = edgeLength(edges{e});

            % retreive edge subscription data
            edgeData = traci.edge.getSubscriptionResults(edges{e});
            %occupancy = edgeData('0x13');
            %effort = edgeData('0x59');
            vehicleNo = edgeData('0x10');
            %vehicleMeanLength = edgeData('0x15');
            edge_i_length = edge_length_laneNo(1);
            edge_i_lanes = edge_length_laneNo(2);
            edgeDensity = (vehicleNo)/( edge_i_length * edge_i_lanes );
            
            % Update Effort
            eff = (4*edgeDensity + edge_i_length)/5;
            traci.edge.setEffort(edges{e}, eff);
                        
            if isKey(EdgeDensities, edges{e})
                EdgeDensities(edges{e}) = [EdgeDensities(edges{e}); edgeDensity];
            else
                EdgeDensities(edges{e}) = edgeDensity;
            end
        end
        everyTenSteps = 0;
    end
    
    
    
   % Client Postions
   VehicleIDList = traci.vehicle.getIDList();
   if ~isempty(VehicleIDList)
       for j = 1:length(VehicleIDList)
           if ismember(VehicleIDList{j}, ClientVehicleIDList)
               
               % reBuild Route by Effort
               traci.vehicle.rerouteEffort(VehicleIDList{j});
               
                p = traci.vehicle.getPosition(VehicleIDList{j});
                if isKey(VehiclesPosition ,VehicleIDList{j})
                    VehiclesPosition(VehicleIDList{j}) = [VehiclesPosition(VehicleIDList{j}); p];
                else
                    VehiclesPosition(VehicleIDList{j}) = p;
                end
           end
       end
   end
   traci.simulationStep();
   vehicleNumberPerTimeStep(i) = vehicleNumberPerTimeStep(i-1) - traci.simulation.getArrivedNumber() + ...
       traci.simulation.getDepartedNumber();
   
   i = i + 1;
   ignoreFirstStep = 1;
end

%% Exit Simulation
traci.close()
