%% Init
clear
close all
clc

%% Inputs
EdgeDensities = './3PercentClient/edgeDensities-2.mat';
xlsxFile = './3PercentClient/edgeDensities-edgeID.xlsx';
%% Optimization

EdgeDensities = load(EdgeDensities);
EdgeDensities = EdgeDensities.EdgeDensities;
edgesID = string(EdgeDensities.keys);
edgeMeanDensity = zeros(1, length(edgesID));

for k=1:length(edgesID)
    edgeMeanDensity(k) = mean(EdgeDensities(edgesID(k)));
end

%% Export
xlswrite(xlsxFile, [edgesID; edgeMeanDensity]');