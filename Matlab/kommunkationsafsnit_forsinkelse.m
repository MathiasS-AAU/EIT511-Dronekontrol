

s = tf('s')
G0 = exp(-1*s)
G1 = exp(-0.1*s)
G2 = exp(-0.01*s)
G3 = exp(-0.001*s)

close all;
figure('Name','Effekt af forsinkelse på fase'); 
    opts = bodeoptions('cstprefs');
    opts.MagVisible = 'off';
    bode(G0,G1,G2,G3,opts)
        h.Annotation.LegendInformation.IconDisplayStyle = 'off';
        legend('1 s','100 ms','10 ms','1 ms');
        xlabel('Frekvens [rad/s]')
        xlim([0.01 100]);
        ylim([-10 0]);
        ylabel('Faseforskydning [grader]')