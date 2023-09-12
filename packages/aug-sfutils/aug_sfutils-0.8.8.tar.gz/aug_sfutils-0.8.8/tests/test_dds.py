import aug_sfutils as sf

# bad shots: 35203, 35302, 35465

dds1 = sf.SFREAD(35465, 'dds') # ed=-1 in ed_cntrl, isis failing
dds2 = sf.SFREAD(35203, 'dds', ed=1) # Empty object names? Failing xsfed, isis

