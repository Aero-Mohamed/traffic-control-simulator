%% Init
clear
close all
clc

%% 10 Client Test-1
% Initializing results Data
TestName = '10 Clients';
VehiclesPositions = [load("./10Clients-Test1/VehiclesPostion-1.mat"),load("./10Clients-Test1/VehiclesPostion-2.mat")] ;
colors = {'*b';'.g'};
legendText = {'Simulation 1', 'Simulation 2'};

positions = [];
for i=1:size(VehiclesPositions, 2)
    positions = [positions struct('x', [], 'y', [], 'distance', 0)];
end
for w=1:size(VehiclesPositions, 2)
    VehiclesPos = VehiclesPositions(w);
    VehiclesPos = VehiclesPos.VehiclesPosition;
    
    keys = VehiclesPos.keys;
    totalDistance = 0;
    for j = 1:VehiclesPos.Count
        hold on;
        position = VehiclesPos(cell2mat(keys(j)));
        for i=1:size(position, 1)-1
            distance = sqrt((position(i, 1) - position(i+1, 1))^2 + (position(i+1, 2) - position(i+1, 2))^2);
            positions(w).distance = positions(w).distance + distance;
        end
        positions(w).x = [positions(w).x; position(:, 1)];
        positions(w).y = [positions(w).y; position(:, 2)];
    end
    hold on;
    plot(positions(w).x, positions(w).y, colors{w});
end
legend(legendText);
error = sqrt(sum(abs(positions(1).x - positions(2).x))^2 + sum(abs(positions(1).y - positions(2).y))^2);
error = error/max(positions(1).distance, positions(2).distance)*100;
title(['Comparing Simulation results of ' TestName ' with Total Error of ' num2str(error) '%']);




