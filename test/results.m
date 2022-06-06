%% Init
clear
close all
clc

%% Inputs
TEST_NAME_PREFIX = 'Random-Trips';

VehiclesPositions = [...
    load(['./' TEST_NAME_PREFIX '/results-1.mat']),...
    load(['./' TEST_NAME_PREFIX '/results-2.mat'])] ;
colors = {'+b';'.g'};
legendText = {'Simulation 1', 'Simulation 2'};

%% Initializing results Data
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
error = 0;
maxDistance = 0;
for w=1:size(VehiclesPositions, 2)-1
    error = error + sqrt(sum(abs(positions(w).x - positions(w+1).x))^2 + sum(abs(positions(w).y - positions(w+1).y))^2);
    maxDistance = max(positions(w).distance, positions(w+1).distance);
end
error = error/maxDistance*100;
title(['Simulation of ' TEST_NAME_PREFIX ' with Total Error of ' num2str(error) '% of total travel distance of ' num2str(maxDistance)]);


