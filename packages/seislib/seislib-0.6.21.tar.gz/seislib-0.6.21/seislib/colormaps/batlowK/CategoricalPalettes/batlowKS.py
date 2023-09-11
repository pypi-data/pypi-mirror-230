# 
#         batlowKS
#                   www.fabiocrameri.ch/colourmaps
from matplotlib.colors import LinearSegmentedColormap      
      
cm_data = [[0.018513, 0.030323, 0.04078],      
           [0.99074, 0.75313, 0.84424],      
           [0.51261, 0.48112, 0.20814],      
           [0.90582, 0.60722, 0.38711],      
           [0.22179, 0.33519, 0.3201],      
           [0.099048, 0.19481, 0.23238],      
           [0.35364, 0.40936, 0.27281],      
           [0.98645, 0.67864, 0.62454],      
           [0.72477, 0.55319, 0.22307],      
           [0.96121, 0.64103, 0.50536],      
           [0.28592, 0.37495, 0.30406],      
           [0.61491, 0.51957, 0.19586],      
           [0.156, 0.27615, 0.30089],      
           [0.99257, 0.71399, 0.73008],      
           [0.82123, 0.57917, 0.28723],      
           [0.42993, 0.44523, 0.23742],      
           [0.065295, 0.11181, 0.13657],      
           [0.9394, 0.6245, 0.44904],      
           [0.38788, 0.42573, 0.25635],      
           [0.99089, 0.69631, 0.67777],      
           [0.12686, 0.24002, 0.27462],      
           [0.25171, 0.3552, 0.31557],      
           [0.08079, 0.15478, 0.18864],      
           [0.19125, 0.31085, 0.31696],      
           [0.99245, 0.73196, 0.78263],      
           [0.67344, 0.53837, 0.20467],      
           [0.77449, 0.56661, 0.25099],      
           [0.31677, 0.3911, 0.29052],      
           [0.97624, 0.65842, 0.56173],      
           [0.56554, 0.50192, 0.19779],      
           [0.46974, 0.46296, 0.22167],      
           [0.86378, 0.59175, 0.33055],      
           [0.046912, 0.076977, 0.093391],      
           [0.17356, 0.29443, 0.31077],      
           [0.11209, 0.21772, 0.2549],      
           [0.26875, 0.36534, 0.3105],      
           [0.40848, 0.43538, 0.24683],      
           [0.64402, 0.5292, 0.19865],      
           [0.072509, 0.13277, 0.16255],      
           [0.99178, 0.74244, 0.81317],      
           [0.98216, 0.66852, 0.5934],      
           [0.53857, 0.49157, 0.20208],      
           [0.88577, 0.59929, 0.35802],      
           [0.33497, 0.4002, 0.28189],      
           [0.92374, 0.61562, 0.41758],      
           [0.95273, 0.63382, 0.48111],      
           [0.36806, 0.41631, 0.26583],      
           [0.20446, 0.3219, 0.31941],      
           [0.45232, 0.4553, 0.22825],      
           [0.05984, 0.096955, 0.11757],      
           [0.090567, 0.17755, 0.21413],      
           [0.9927, 0.72164, 0.7525],      
           [0.99189, 0.70387, 0.70024],      
           [0.70287, 0.54703, 0.21396],      
           [0.034413, 0.059722, 0.074236],      
           [0.29902, 0.38193, 0.29856],      
           [0.5864, 0.50958, 0.196],      
           [0.97058, 0.6509, 0.53767],      
           [0.13895, 0.25605, 0.28725],      
           [0.23468, 0.34417, 0.31894],      
           [0.49384, 0.47331, 0.21356],      
           [0.84612, 0.5863, 0.3112],      
           [0.98877, 0.68622, 0.64752],      
           [0.79496, 0.57205, 0.26558],      
           [0.75347, 0.561, 0.23793],      
           [0.89605, 0.6032, 0.37237],      
           [0.16473, 0.28551, 0.30632],      
           [0.80825, 0.57562, 0.27612],      
           [0.14738, 0.26631, 0.29454],      
           [0.34422, 0.40476, 0.2774],      
           [0.68818, 0.54277, 0.20889],      
           [0.94635, 0.62911, 0.46502],      
           [0.076456, 0.14367, 0.17559],      
           [0.99263, 0.72678, 0.76752],      
           [0.93185, 0.62001, 0.4332],      
           [0.441, 0.45024, 0.23276],      
           [0.39809, 0.43053, 0.2516],      
           [0.4191, 0.44027, 0.24209],      
           [0.26021, 0.36034, 0.31322],      
           [0.55193, 0.49675, 0.19968],      
           [0.52546, 0.48634, 0.20493],      
           [0.97942, 0.66347, 0.57762],      
           [0.96616, 0.64594, 0.52153],      
           [0.65871, 0.53383, 0.20123],      
           [0.27732, 0.37019, 0.30742],      
           [0.98449, 0.67358, 0.60905],      
           [0.48166, 0.46812, 0.21752],      
           [0.21314, 0.32875, 0.3201],      
           [0.99216, 0.73717, 0.79784],      
           [0.98996, 0.69126, 0.6627],      
           [0.37788, 0.42099, 0.2611],      
           [0.62941, 0.52443, 0.19689],      
           [0.32579, 0.39565, 0.28626],      
           [0.085423, 0.16608, 0.20148],      
           [0.11926, 0.22899, 0.26513],      
           [0.30783, 0.38652, 0.29463],      
           [0.068875, 0.12209, 0.14953],      
           [0.99231, 0.70893, 0.71516],      
           [0.1053, 0.20632, 0.24391],      
           [0.1824, 0.30286, 0.3143]]      
      
batlowKS_map = LinearSegmentedColormap.from_list('batlowKS', cm_data)      
# For use of "viscm view"      
test_cm = batlowKS_map      
      
if __name__ == "__main__":      
    import matplotlib.pyplot as plt      
    import numpy as np      
      
    try:      
        from viscm import viscm      
        viscm(batlowKS_map)      
    except ImportError:      
        print("viscm not found, falling back on simple display")      
        plt.imshow(np.linspace(0, 100, 256)[None, :], aspect='auto',      
                   cmap=batlowKS_map)      
    plt.show()      
