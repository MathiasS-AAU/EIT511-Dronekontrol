


s = tf('s');
G0 = exp(-1*s);
G1 = exp(-0.1*s);
G2 = exp(-0.01*s);
G3 = exp(-0.001*s);

close all;
fig = figure('Name','Effekt af forsinkelse på fase'); 
    opts = bodeoptions('cstprefs');
    opts.MagVisible = 'off';
    opts.xlim = [0.01 100];
    opts.ylim = [-10 0];
    %opts.ConfidenceRegionNumberSD = 4;
    opts.Grid = 'on';
    
    W=logspace(-3,3,10000);
    bode(G0,G1,G2,G3,opts,W)
        h.Annotation.LegendInformation.IconDisplayStyle = 'off';
        legend('1 s','100 ms','10 ms','1 ms');
        
        title('Bodeplot af forsinkelse')
        xlabel('Frekvens')
      
        
        ylabel('Faseforskydning (°)')
        labels = findall(fig,'Type','Text');
        label2 = labels(strncmp(get(labels,'String'),'Faseforskydning [°]',5));
        set(label2,'String',regexprep(get(label2,'String'),'(\(\w*))',''));