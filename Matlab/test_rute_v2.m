    clear all;
    close all;
    format short;
    
ViconFile=uigetfile('*.csv','Select exported file from Vicon (csv)');
ViconData=csvread(ViconFile,5); % Ignore the first 5 columns (nodata)
    Frame=ViconData(:,1);   % Frame [#]
    TX=ViconData(:,6);      % Translation x = Right [mm]
    TY=ViconData(:,7);      % Translation y = Forward [mm]
%from mm to m
framerate = 100;
Frame = Frame/framerate; % Frames to seconds
TX = TX/1000;
TY = TY/1000;

% How close did it land?
Landdist = sqrt((TX(length(TX))-(-0.5))^2 + (TY(length(TY))-0.5)^2 )

%Route
figure(1);
    plot([-0.5 0.5 0.5 -0.5 -0.5], [0.5 0.5 -0.5 -0.5 0.5],'b'); hold on;
    plot(TX,TY,'r');
    plot(TX(1),TY(1),'ro', TX(end),TY(end),'bo');

%     plot(-0.5,0.5,'kx', 0.5,0.5,'kx', 0.5,-0.5,'kx', -0.5,-0.5,'kx');    
%     text(0.5,0.5,{'1'},'VerticalAlignment','top','HorizontalAlignment','left')
%     text(0.5,-0.5,{'2'},'VerticalAlignment','top','HorizontalAlignment','left')
%     text(-0.5,-0.5,{'3'},'VerticalAlignment','top','HorizontalAlignment','right')
%     text(-0.5,0.5,{'4'},'VerticalAlignment','top','HorizontalAlignment','right')

    plot(-0.5,0.5,'kx', 0,0.5,'kx', 0.5,0.5,'kx', 0.5,0,'kx', 0.5,-0.5,'kx', 0,-0.5,'kx', -0.5,-0.5,'kx', -0.5,0,'kx')    
    text(-0.5,0,{'1'},'VerticalAlignment','top','HorizontalAlignment','right')
    text(-0.5,-0.5,{'2'},'VerticalAlignment','top','HorizontalAlignment','right')
    text(0,-0.5,{'3'},'VerticalAlignment','top','HorizontalAlignment','right')
    text(0.5,-0.5,{'4'},'VerticalAlignment','top','HorizontalAlignment','left')
    text(0.5,0,{'5'},'VerticalAlignment','top','HorizontalAlignment','left')
    text(0.5,0.5,{'6'},'VerticalAlignment','top','HorizontalAlignment','left')
    text(0,0.5,{'7'},'VerticalAlignment','top','HorizontalAlignment','right')
    text(-0.5,0.5,{'8'},'VerticalAlignment','top','HorizontalAlignment','right')

    h.Annotation.LegendInformation.IconDisplayStyle = 'off';
    legend('Planlagt flyverute','Dronens flyverute','Startpunkt','Slutpunkt','Rutepunkt');
    grid;
    xlabel('X position [m]');
    ylabel('Y position [m]');
    %ylim([-0.6 1.5]);
    %xlim([-0.6 1.5]);
    hold off;

    %Distance
for i = 1 : length(TX)
    %Line distances
    L1Dist = abs(0.5-TY(i));
    L2Dist = abs(-0.5-TY(i));
    L3Dist = abs(-0.5-TX(i));
    L4Dist = abs(0.5-TX(i));
    
    %Check for invalid line distances
    %Ignore horizontal lines if outside of box in x direction
    if TX(i) < -0.5 || TX(i) > 0.5
        L1Dist = 1e6;
        L2Dist = 1e6;
    end
    %Ignore vertical lines if outside of box in y direction
    if TY(i) < -0.5 || TY(i) > 0.5
        L3Dist = 1e6;
        L4Dist = 1e6;
    end
    %If outside of box in both x and y direction use point distances instead
    if (TX(i) < -0.5 || TX(i) > 0.5) && (TY(i) < -0.5 || TY(i) > 0.5)
        %Point distances
        L1Dist = sqrt((0.5 - TX(i))^2 + (0.5 - TY(i))^2);
        L2Dist = sqrt((-0.5  -TX(i))^2 + (0.5 - TY(i))^2);
        L3Dist = sqrt((0.5 - TX(i))^2 + (-0.5 - TY(i))^2);
        L4Dist = sqrt((-0.5 - TX(i))^2 + (-0.5 - TY(i))^2);
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
yline(0.30,'r')
ylim([0 0.35]);
xlim([0 Frame(end)]);
ylabel('Dronens afstand fra rute [m]');
xlabel('Sekunder [s]');


% Plotting velocitty
fs=100;
%Frame = Frame/fs; %frames to seconds
syms f(x);
    %TY = lowpass(TY,1,fs);
    dTY = gradient(TY(:)) ./ gradient(Frame(:));
    %TX = lowpass(TY,1,fs);
    dTX = gradient(TX(:)) ./ gradient(Frame(:));
    %Speed to velocity
     for i = 1 : length(TX)
         dTD(i) = sqrt(dTY(i)^2 + dTX(i)^2); 
     end
     %dTd = lowpass(dTD,1,fs);
     
figure(3);  
    plot(Frame,dTD);
    ylabel('Hastighed [m/s]');
    %ylim([0 2]);
    xlim([0 Frame(end)]);
    grid on;
    xlabel('Tid [s]');   

max(DistVector)
