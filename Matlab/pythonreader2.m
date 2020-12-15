% Python reader
clear all;
close all;
format short;

ktangent = 2; % Tangentpoint for simulation [s]
ktangent2 = 5;%5;
simTY = 0; % 1 for simulation of TY
simRZ = 1; % 1 for simulation of RZ
setTimeZero = 0;

% Find and read file:
measFile=uigetfile('*.csv','Select exportet file from Vicon (csv)');
measData=csvread(measFile,1); % Ignore the first 5 columns (nodata)
    time=measData(:,1);   % Time [ms]
    TX=measData(:,2);      % Translation x = Right [m]
    TY=measData(:,3);      % Translation y = Forward [m]
    TZ=measData(:,4);      % Translation z = Upwards [m]
    stepRef=measData(:,5);      % Translation z = Upwards [m]
    RZ=-measData(:,6);

% Units and definitions
    time = ((time-time(1))/1000);
    %TX = TX-TX(1); % So position starts at 0 [m]
    %TY = TY-TY(1); % So position starts at 0 [m]
    TXY = sqrt((TX.^2)+(TY.^2));
    RZ = unwrap(RZ);
    dTX = gradient(TX(:)) ./ gradient (time(:));
    dTY = gradient(TY(:)) ./ gradient (time(:));
    dTZ = gradient(TZ(:)) ./ gradient (time(:));
    dTXY = gradient(TXY(:)) ./ gradient (time(:));
    xStart = 0;
    xEnd = time(end);
    %xEnd = 2.5;

% Filtering
    fs=100;
    syms f(x);
    ldTXY = lowpass(dTXY,1,fs);
    RZ = lowpass(RZ,1,fs);
    RZ(:) = RZ(:)-RZ(1);
    dRZ(:) = gradient(RZ(:)) ./ gradient (time(:));
    doRZ = lowpass(dRZ,1,50);

% Translation i XYZ
figure('Name','Bevægelse i XYZ');
    subplot(3,1,1);
        plot(time, TX);
        title('Bevægelse i x-retning');
        xlim([0 xEnd]);
        ylabel('TX [m]');
        grid on;
    subplot(3,1,2);
        plot(time, TY);
        title('Bevægelse i y-retning');
        xlim([0 xEnd]);
        ylabel('TY [m]');
        grid on;
    subplot(3,1,3);
        plot(time, TZ);
        title('Bevægelse i z-retning');
        xlim([0 xEnd]);
        xlabel('Tid [s]');
        ylabel('TZ [m]');
        grid on;

% Velocity in XYZ
figure('Name','Hastighed for XYZ');
    subplot(3,1,1);
        plot(time, dTX);
        title('Hastighed i x-retning');
        ylabel('dTX [m/s]');
        xlim([xStart xEnd]);
        grid on;
    subplot(3,1,2);
        plot(time, dTY);
        title('Hastighed i y-retning');
        ylabel('dTY [m/s]');
        xlabel('Tid [s]');
        xlim([xStart xEnd]);
        grid on;
    subplot(3,1,3);
        plot(time, dTZ);
        title('Hastighed i z-retning');
        ylabel('dTZ [m/s]');
        xlabel('Tid [s]');
        xlim([xStart xEnd]);
        grid on;
        
if simTY == 1
    % Method for deciding firstorder model for translation
    figure('Name','Steprespons for fremadgående bevægelse'); 
        %subplot(2,1,1);
            plot(time,TXY);
            title('Fremadgående bevægelse');
            ylabel('Position [m]');
            xlabel('Sekunder [s]'); 
            xlim([xStart xEnd]);
            %ylim([min(TY) max(TY)]);
            ylim([min(TY) 2]);
                ktangent=round(mean(find(time < ktangent+0.1 & time > ktangent-0.1)));
                tangTXY=(time-time(ktangent))*dTXY(ktangent)+TXY(ktangent);
                hold on;
                plot(time,tangTXY);
                scatter(time(ktangent),TXY(ktangent));
                yline(0,'--');
                hold off;
            grid on;
%         subplot(2,1,2);
%             plot(time,dTXY);
%             title('Hastighed');
%             ylabel('TXY [m/s]');
%             xlim([xStart xEnd]);
%             grid on;
%             xlabel('Tid [s]'); 

    % Simulation
    tau=time(round(mean(find(tangTXY < 0.05 & tangTXY > -0.05))));
    K = (dTXY(ktangent));
    s=tf('s');
    G=K/(tau*s+1)
    [simTXY simTime] = step(G);
    figure('Name','Steprespons');
        plot(time,dTXY,time,ldTXY,simTime,simTXY);
        yline(simTXY(end),'--');
        legend('Hastighedsmåling','Lavpas-filtreret hastighedsmåling','Simuleret model','Reference','Location','southeast');
        xlim([xStart xEnd]);
        %ylim([min(simTXY) max(dTXY)]);
        ylim([min(simTXY) 1]);
        ylabel('Hastighed [m/s]');
        xlabel('Sekunder [s]');
        title('Steprespons for hastighed i y-retning');
end

if simRZ == 1
    % Method for deciding firstorder model for translation
    figure('Name','Steprespons for fremadgående bevægelse'); 
        %subplot(2,1,1);
            plot(time,RZ);
            title('Yaw rotering');
            ylabel('Yaw [grader]');
            xlabel('Sekunder [s]');
            xlim([xStart xEnd]);
            ylim([min(RZ) max(RZ)]);
                ktangent2=round(mean(find(time < ktangent2+0.1 & time > ktangent2-0.1)));
                tangRZ=(time-time(ktangent2))*dRZ(ktangent2)+RZ(ktangent2);
                hold on;
                plot(time,tangRZ);
                scatter(time(ktangent2),RZ(ktangent2));
                yline(0,'--');
                hold off;
            grid on;
%         subplot(2,1,2);
%             plot(time,dRZ);
%             title('Yaw hastighed');
%             ylabel('dRZ [deg/s]');
%             xlim([xStart xEnd]);
%             grid on;
%             xlabel('Tid [s]'); 

    % Simulation
    tauRZ=time(round(mean(find(tangRZ < 0.95 & tangRZ > -0.95))));
    KRZ = (dRZ(ktangent2));
    %KRZ = 45.1389;
    %tauRZ = 0.22;
    s=tf('s');
    G=KRZ/(tauRZ*s+1)
    [simRZ simTime2] = step(G);
    figure('Name','Steprespons');
        %plot(time,dTXY,time,ldTXY,simTime,simTXY);
        plot(time,dRZ,time,doRZ,simTime2,simRZ);
        yline(simRZ(end),'--');
        legend('Hastighedsmåling','Lavpas-filtreret hastighedsmåling','Simuleret model','Reference','Location','southeast');
        %xlim([xStart xEnd]);
        xlim([xStart 2]);
        %ylim([min(simRZ) max(dRZ)]);
        ylim([min(simRZ) 55]);
        ylabel('Hastighed [grader/s]');
        xlabel('Sekunder [s]');
        title('Steprespons for hastighed i yaw-orientering');
end