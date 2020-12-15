% ViconCSVread.m - Version 1 (22/10/2020)
% EIT5: 20gr511
% Script for reading csv files from Vicon Tracker
% The measured file has to be inside a Matlab folder
% REMEMBER TO ADD ALL RELEVANT (SUB)FOLDERS TO THE PATH! (Else error)
    clear all;
    close all;

% Find and read file:
ViconFile=uigetfile('*.csv','Select exportet file from Vicon (csv)');
ViconData=csvread(ViconFile,5); % Ignore the first 5 columns (nodata)
    Frame=ViconData(:,1);   % Frame [#]
    RX=ViconData(:,3);      % Rotating x = Pitch [rad]
    RY=ViconData(:,4);      % Rotating y = Roll [rad]
    RZ=ViconData(:,5);      % Rotating z = Yaw [rad]
    TX=ViconData(:,6);      % Translation x = Right [mm]
    TY=ViconData(:,7);      % Translation y = Forward [mm]
    TZ=ViconData(:,8);      % Translation z = Upwards [mm]

% Units:
framerate = 100;
Frame = Frame/framerate; % Frames to seconds
RX = RX*(180/pi); % Radian to degrees
RY = RY*(180/pi);
RZ = unwrap(RZ*(180/pi)); % Unwrap stepping graph
TX = TX/1000; % mm to m
TY = TY/1000;
TZ = TZ/1000;

% Lowpass filtering and derivative:
fs=100;
syms f(x);
    RZ = lowpass(RZ,1,fs);
    dRZ = gradient(RZ(:)) ./ gradient(Frame(:));
    ddRZ = gradient(dRZ(:)) ./ gradient(Frame(:));
    TY = lowpass(TY,1,fs);
    dTY = gradient(TY(:)) ./ gradient(Frame(:));
    ddTY=gradient(dTY(:)) ./ gradient(Frame(:));

figure('Name','Steprespons for bevægelse i y-retning'); 
    subplot(2,1,1);
        plot(Frame,TY);
        title('Position');
        ylabel('y [m]');
        xlim([0.25 0.6]);
        ylim([-0.15 0.1]);
            kTY=0.5*framerate; %(Tangentpoint [s])*framerate
            tangTY=(Frame-Frame(kTY))*dTY(kTY)+TY(kTY); %y = slope * (x - xTangent) + yOffset
            hold on;
            plot(Frame,tangTY);
            scatter(Frame(kTY),TY(kTY));
            yline(-0.07942,'--');
            hold off;
            disp(round(dTY(kTY)));
        grid on;
    subplot(2,1,2);
        plot(Frame,dTY);
        title('Hastighed');
        ylabel('y [m/s]');
        %xlim([0.25 0.6]);
        %ylim([-0.5 1]);
%             kdTY=0.4*framerate; %(Tangentpoint [s])*framerate
%             tangdTY=(Frame-Frame(kdTY))*ddTY(kdTY)+dTY(kdTY); %y = slope * (x - xTangent) + yOffset
%             hold on;
%             plot(Frame,tangdTY);
%             scatter(Frame(kdTY),dTY(kdTY));
%             hold off;
%             disp(round(ddTY(kdTY)));
        grid on;
        xlabel('Tid [s]');      
        
figure('Name','Steprespons for rotation i z-retning'); 
    subplot(2,1,1);
        plot(Frame,RZ);
        title('Yaw vinkel');
        ylabel('rz [deg]');
        xlim([1 2.5]);
        ylim([50 250]);
            kRZ=1.75*framerate; %(Tangentpoint [s])*framerate
            tangRZ=(Frame-Frame(kRZ))*dRZ(kRZ)+RZ(kRZ); %y = slope * (x - xTangent) + yOffset
            hold on;
            plot(Frame,tangRZ);
            scatter(Frame(kRZ),RZ(kRZ));
            yline(101,'--');
            hold off;
            disp(round(dRZ(kRZ)));
        grid on;
    subplot(2,1,2);
        plot(Frame,dRZ);
        title('Yaw vinkelhastighed');
        ylabel('rz [deg/s]');
        xlim([1 2.5]);
        ylim([-50 200]);
%             kdRZ=1.4*framerate; %(Tangentpoint [s])*framerate
%             tangdRZ=(Frame-Frame(kdRZ))*ddRZ(kdRZ)+dRZ(kdRZ); %y = slope * (x - xTangent) + yOffset
%             hold on;
%             plot(Frame,tangdRZ);
%             scatter(Frame(kdRZ),dRZ(kdRZ));
%             hold off;
%             disp(round(ddRZ(kdRZ)));
        grid on;
        xlabel('Tid [s]');
        
figure('Name','Position i y-retning'); 
plot(Frame,TY);
        title('Position');
        ylabel('y [m]');
        xlim([0.25 0.6]);
        ylim([-0.15 0.1]);
            kTY=0.5*framerate; %(Tangentpoint [s])*framerate
            tangTY=(Frame-Frame(kTY))*dTY(kTY)+TY(kTY); %y = slope * (x - xTangent) + yOffset
            hold on;
            plot(Frame,tangTY);
            scatter(Frame(kTY),TY(kTY));
            yline(-0.07942,'--');
            hold off;
            disp(round(dTY(kTY)));
        grid on;