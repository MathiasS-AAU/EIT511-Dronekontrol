clear all;
close all;
format short;

% Manual input: 488, 514
startframe = 514; % Specifik frame where the step is set [frames]
xEnd = 4.3; % The plots will stop with this time value [s]
ktangent = 2+(startframe/100); % Tangentpoint for simulation [s]

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

% Units and definitions
    framerate = 100;
    xStart = 0;
    Frame = (Frame/framerate)-(startframe/framerate); % Frames to seconds
    startframe = 0;
    TX = TX/1000; % mm to m
    TY = TY/1000;
    TZ = TZ/1000;
    offsetTX = TX-TX(1); % Set startvalue of TX to 0
    offsetTY = TY-TY(1); % Set startvalue of TY to 0
    Fremad = sqrt((offsetTX.^2)+(offsetTY.^2)); % Calculate absolute position for drone
    fs=100;
    syms f(x);
    %Fremad = lowpass(Fremad,1,fs);
    dFremad = gradient(Fremad(:)) ./ gradient(Frame(:));
    doffsetTX = gradient(offsetTX(:)) ./ gradient (Frame(:));
    doffsetTY = gradient(offsetTY(:)) ./ gradient (Frame(:));

% For setting x-limit:
figure('Name','Rå måledata for position');
    subplot(3,1,1);
        plot(Frame, TX);
        title('Bevægelse i x-retning');
        ylabel('TX [m]');
        grid on;
    subplot(3,1,2);
        plot(Frame, TY);
        title('Bevægelse i y-retning');
        ylabel('TY [m]');
        grid on;
    subplot(3,1,3);
        plot(Frame, TZ);
        title('Bevægelse i z-retning');
        xlabel('Tid [s]');
        ylabel('TZ [m]');
        grid on;

% Plot of general XY movement
figure('Name','Bevægelse i XY-plan');
    subplot(4,1,1);
        plot(Frame, offsetTX);
        title('Bevægelse i x-retning med offset');
        ylabel('TX [m]');
        xlim([xStart xEnd]);
        grid on;
    subplot(4,1,2);
        plot(Frame, doffsetTX);
        title('Hastighed i x-retning');
        ylabel('dTX [m/s]');
        xlim([xStart xEnd]);
        grid on;
    subplot(4,1,3);
        plot(Frame, offsetTY);
        title('Bevægelse i y-retning med offset');
        ylabel('TY [m]');
        xlabel('Tid [s]');
        xlim([xStart xEnd]);
        grid on;
    subplot(4,1,4);
        plot(Frame, doffsetTY);
        title('Hastighed i y-retning');
        ylabel('dTY [m/s]');
        xlim([xStart xEnd]);
        grid on;
        
figure('Name','Steprespons for bevægelse i y-retning'); 
    subplot(2,1,1);
        plot(Frame,Fremad);
        title('Position');
        ylabel('y [m]');
        xlim([xStart xEnd]);
        %ylim([-0.15 0.1]);
            kFremad=ktangent*framerate;
            tangFremad=(Frame-Frame(kFremad))*dFremad(kFremad)+Fremad(kFremad);
            hold on;
            plot(Frame,tangFremad);
            scatter(Frame(kFremad),Fremad(kFremad));
            yline(0,'--');
            hold off;
        grid on;
    subplot(2,1,2);
        plot(Frame,dFremad);
        title('Hastighed');
        ylabel('y [m/s]');
        xlim([xStart xEnd]);
        grid on;
        xlabel('Tid [s]'); 

% Simulation
intersection=find(tangFremad < 0.005 & tangFremad > -0.005);
tau = min(Frame(intersection)-(startframe/framerate))
K = (dFremad(kFremad))
s=tf('s');
G=K/(tau*s+1);
[simFremad simFrame] = step(G);
figure('Name','Steprespons');
    plot(simFrame,simFremad,Frame,dFremad);
    yline(simFremad(end),'--');
    legend('Simuleret model','Differentieret måling','Reference','Location','southeast');
    %xlim([0 simFrame(end)]);
    xlim([xStart xEnd]);
    %ylim([min(simFremad) max(simFremad)+0.2]);
    ylim([-0.3 1.5]);
    ylabel('Hastighed [m/s]');
    xlabel('Sekunder [s]');
    title('Steprespons for hastighed i y-retning');
    
    
figure('Name','Rapportfigur'); 
        plot(Frame,Fremad);
        title('Bevægelse i y-retning');
        ylabel('Position [m]');
        xlabel('Sekunder [s]');
        xlim([xStart xEnd]);
        %ylim([-0.15 0.1]);
            kFremad=ktangent*framerate;
            tangFremad=(Frame-Frame(kFremad))*dFremad(kFremad)+Fremad(kFremad);
            hold on;
            plot(Frame,tangFremad);
            scatter(Frame(kFremad),Fremad(kFremad));
            yline(0,'--');
            hold off;
        grid on;

        
figure('Name','Rapportfigur'); 
        plot(Frame,RZ);
        title('Bevægelse i y-retning');
        ylabel('Position [m]');
        xlabel('Sekunder [s]');
        %xlim([xStart xEnd]);
        %ylim([-0.15 0.1]);
        grid on;
