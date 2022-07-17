%% Init
clear
close all
clc

%% Inputs
TEST_NAME_PREFIX = '3PercentClient';
TRAFFIC_FREE = '3PercentClient';

VehiclesPositions = [...
    load(['./' TEST_NAME_PREFIX '/Optimization-results-2.mat']),...
    load(['./' TRAFFIC_FREE '/results-1.mat'])] ;
colors = {'*g';'+b';'.g'};
legendText = {'Optimized Routes 2', 'Shortest Path Only'};

%% Initializing results Data
x_ = [1 2 3 4 5 6 7 8 9 10 1 2 3 4 5 6 7 8 9 10];
y_ = zeros(1,20);
positions = [];
for i=1:size(VehiclesPositions, 2)
    positions = [positions struct('x', [], 'y', [], 'distance', 0)];
end
for w=1:size(VehiclesPositions, 2)
    VehiclesPos = VehiclesPositions(w);
    VehiclesPos = VehiclesPos.VehiclesPosition;
    
    keys = VehiclesPos.keys;
    totalDistance = 0;
    for j = 2:VehiclesPos.Count
        hold on;
        position = VehiclesPos(cell2mat(keys(j)));
        for i=1:size(position, 1)-1
            distance = sqrt((position(i, 1) - position(i+1, 1))^2 + (position(i, 2) - position(i+1, 2))^2);
            positions(w).distance = positions(w).distance + distance;
        end
        
        y_((10*w)-10+j) = size(position(:, 1), 1);
        
        positions(w).x = [positions(w).x; position(:, 1)];
        positions(w).y = [positions(w).y; position(:, 2)];
        
    end
    hold on;
    plot(positions(w).x, positions(w).y, colors{w});
end
legend(legendText);
absError = 0; sumError = 0; maxDistance = 0;
for w=1:size(VehiclesPositions, 2)-1
    % Fix matrix dimensions if required
    sim1Size = size(positions(w).x, 1);
    sim2Size = size(positions(w+1).x, 1);
    additionalDimensionFixElements = ones(abs(sim1Size - sim2Size), 1);
    if(sim1Size < sim2Size)
        positions(w).x = [positions(w).x; additionalDimensionFixElements .* positions(w+1).x(end)];
        positions(w).y = [positions(w).y; additionalDimensionFixElements .* positions(w+1).y(end)];
    else
        positions(w+1).x = [positions(w+1).x; additionalDimensionFixElements .* positions(w).x(end)];
        positions(w+1).y = [positions(w+1).y; additionalDimensionFixElements .* positions(w).y(end)];
    end
    absError = absError + sqrt(sum(abs(positions(w).x - positions(w+1).x))^2 + sum(abs(positions(w).y - positions(w+1).y))^2);
    sumError = sumError + sqrt(sum(positions(w).x - positions(w+1).x)^2 + sum(positions(w).y - positions(w+1).y)^2);
    maxDistance = max(positions(w).distance, positions(w+1).distance);
end
absError = round(absError/maxDistance*100);
sumError = round(sumError/maxDistance*100);
title(['Simulation of ' TEST_NAME_PREFIX ' with Total abs Error of ' num2str(absError) '%  and distance sum error of ' num2str(sumError) '% of total travel distance of ' num2str(round(maxDistance))]);




%% Travel Time 
figure;
scatter(x_(1:10),y_(1:10))
hold on
scatter(x_(11:20),y_(11:20))
%scatter(x_(21:30),y_(21:30))
legend(legendText);
