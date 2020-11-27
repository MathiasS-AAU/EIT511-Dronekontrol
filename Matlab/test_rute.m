    clear all;
    %close all;

ViconFile=uigetfile('*.csv','Select exported file from Vicon (csv)');
ViconData=csvread(ViconFile,5); % Ignore the first 5 columns (nodata)
    Frame=ViconData(:,1);   % Frame [#]
    TX=ViconData(:,6);      % Translation x = Right [mm]
    TY=ViconData(:,7);      % Translation y = Forward [mm]
%from mm to m
TX = TX/1000;
TY = TY/1000;

%Route
figure(1);
plot([-0.75 0.75 0.75 -0.75 -0.75], [0.75 0.75 -0.75 -0.75 0.75],TX,TY)
    ylim([-1 1]);
    xlim([-1 1]);

%Distance
for i = 1 : length(TX)
    %Line distances
    L1Dist = abs(0.75-TY(i));
    L2Dist = abs(-0.75-TY(i));
    L3Dist = abs(-0.75-TX(i));
    L4Dist = abs(0.75-TX(i));
    
    
    %Check for invalid line distances
    %Ignore horizontal lines if outside of box in x direction
    if TX(i) < -0.75 || TX(i) > 0.75
        L1Dist = 1e6;
        L2Dist = 1e6;
    end
    %Ignore vertical lines if outside of box in y direction
    if TY(i) < -0.75 || TY(i) > 0.75
        L3Dist = 1e6;
        L4Dist = 1e6;
    end
    %If outside of box in both x and y direction use point distances instead
    if (TX(i) < -0.75 || TX(i) > 0.75) && (TY(i) < -0.75 || TY(i) > 0.75)
        %Point distances
        L1Dist = Sqrt((0.75 - TX(i))^2 + (0.75 - TY(i))^2);
        L2Dist = Sqrt((-0.75  -TX(i))^2 + (0.75 - TY(i))^2);
        L3Dist = Sqrt((0.75 - TX(i))^2 + (-0.75 - TY(i))^2);
        L4Dist = Sqrt((-0.75 - TX(i))^2 + (-0.75 - TY(i))^2);
    end
    
    %Find the lowest value
    if L1Dist < L2Dist
        Dist = L1Dist;
    else
        Dist = L2Dist;
    end
    if Dist > L3Dist
        Dist = L3Dist;
    end
    if Dist > L4Dist
        Dist = L4Dist;
    end
    
    %Put the lowest value in the array
    DistVector(i) = Dist;
end
figure(2);
plot(Frame,DistVector)


% Plotting velocitty
fs=100;
Frame = Frame/fs; %frames to seconds
syms f(x);
    TY = lowpass(TY,1,fs);
    dTY = gradient(TY(:)) ./ gradient(Frame(:));
    TX = lowpass(TY,1,fs);
    dTX = gradient(TX(:)) ./ gradient(Frame(:));
    %Speed to velocity
    for i = 1 : length(TX)
        dTD(i) = sqrt(dTY(i)^2 + dTX(i)^2);
    end
    ddTD = gradient(dTD(:)) ./ gradient(Frame(:));
figure(3);  
    plot(Frame,dTD);
    title('Hastighed');
    ylabel('y [m/s]');
    ylim([0 2]);
    grid on;
    xlabel('Tid [s]');   
   
% How close did it land?
Landdist = sqrt((-0.75 - TX(length(TX)))^2 + (0.75 - TY(length(TY)))^2 )