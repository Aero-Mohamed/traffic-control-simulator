%% Init
clear
close all
clc
import traci.constants
%% Inputs
TEST_NAME_PREFIX = '45PercentClient';

%% Run Simulation
traci.start(['sumo-gui -c ./../network/simulation.sumo.cfg -r ./' TEST_NAME_PREFIX '/routes.rou.xml --start']);

SIM_STEPS = [1 3600];
beginTime = SIM_STEPS(1);
duration =  SIM_STEPS(2);
endTime =  SIM_STEPS(1) +  SIM_STEPS(2) - 1;
vehicleNumberPerTimeStep = zeros(1, duration);

ClientVehicleIDList = {'Trip-1', 'Trip-2', 'Trip-3', 'Trip-4', 'Trip-5', 'Trip-6', 'Trip-7', 'Trip-8', 'Trip-9', 'Trip-10'};

VehiclesPosition = containers.Map;

for i = 2: duration
   VehicleIDList = traci.vehicle.getIDList();
   if ~isempty(VehicleIDList)
       for j = 1:length(VehicleIDList)
           if ismember(VehicleIDList{j}, ClientVehicleIDList)
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
end

%% Exit Simulation
traci.close()
