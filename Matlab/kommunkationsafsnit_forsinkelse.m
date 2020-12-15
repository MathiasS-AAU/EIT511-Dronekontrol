

s = tf('s')
G0 = exp(-1*s)
G1 = exp(-0.1*s)
G2 = exp(-0.01*s)
G3 = exp(-0.001*s)

close all;
figure('Name','Effekt af forsinkelse på fase'); 
    opts = bodeoptions('cstprefs');
    opts.MagVisible = 'off';
    subplot(1,4,1);
        bode(G0,opts)
        title('1 s');
    subplot(1,4,2);
        bode(G1,opts)
        title('100 ms');
    subplot(1,4,3);
        bode(G2,opts)
        title('10 ms');
    subplot(1,4,4);
        bode(G3,opts)
        title('1 ms');