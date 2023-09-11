# 
#         osloS
#                   www.fabiocrameri.ch/colourmaps
from matplotlib.colors import LinearSegmentedColormap      
      
cm_data = [[0.011981, 0.022573, 0.035904],      
           [0.9755, 0.97627, 0.97736],      
           [0.30552, 0.47648, 0.73395],      
           [0.62419, 0.68501, 0.78985],      
           [0.087109, 0.22965, 0.36899],      
           [0.78818, 0.80419, 0.83221],      
           [0.056384, 0.12516, 0.19661],      
           [0.47934, 0.59453, 0.79049],      
           [0.15395, 0.34405, 0.55685],      
           [0.045051, 0.079044, 0.11765],      
           [0.068913, 0.17697, 0.28302],      
           [0.70433, 0.73922, 0.79993],      
           [0.5492, 0.638, 0.79001],      
           [0.11283, 0.28431, 0.45849],      
           [0.4033, 0.54528, 0.78064],      
           [0.88441, 0.88917, 0.89742],      
           [0.21582, 0.40565, 0.65075],      
           [0.061699, 0.15035, 0.23901],      
           [0.66327, 0.71065, 0.79272],      
           [0.05216, 0.10171, 0.15603],      
           [0.83587, 0.84511, 0.86123],      
           [0.13107, 0.31389, 0.50733],      
           [0.35647, 0.51314, 0.76358],      
           [0.58637, 0.66109, 0.7894],      
           [0.029592, 0.05624, 0.085837],      
           [0.076503, 0.20119, 0.32264],      
           [0.93302, 0.93515, 0.93873],      
           [0.74795, 0.77185, 0.81362],      
           [0.1833, 0.37572, 0.60697],      
           [0.44529, 0.57287, 0.78828],      
           [0.097979, 0.25504, 0.41039],      
           [0.25504, 0.438, 0.69265],      
           [0.51216, 0.61504, 0.79069],      
           [0.90873, 0.91198, 0.91758],      
           [0.16771, 0.35962, 0.58184],      
           [0.8601, 0.86682, 0.87855],      
           [0.56773, 0.64949, 0.78964],      
           [0.38054, 0.52984, 0.77355],      
           [0.27982, 0.45722, 0.7145],      
           [0.5307, 0.62654, 0.7904],      
           [0.020473, 0.040333, 0.064433],      
           [0.64352, 0.69754, 0.79087],      
           [0.72581, 0.75497, 0.80584],      
           [0.049925, 0.09066, 0.13649],      
           [0.60516, 0.6729, 0.78942],      
           [0.42482, 0.55955, 0.78536],      
           [0.81186, 0.82418, 0.84572],      
           [0.065067, 0.16352, 0.26083],      
           [0.68351, 0.72448, 0.79564],      
           [0.1214, 0.29907, 0.48282],      
           [0.054125, 0.11324, 0.17602],      
           [0.081609, 0.21535, 0.34567],      
           [0.33129, 0.49527, 0.7504],      
           [0.058867, 0.13757, 0.21759],      
           [0.10497, 0.26965, 0.43433],      
           [0.14184, 0.32887, 0.532],      
           [0.093033, 0.2441, 0.39255],      
           [0.77073, 0.7899, 0.82345],      
           [0.073118, 0.19072, 0.30554],      
           [0.95123, 0.9527, 0.95509],      
           [0.039346, 0.06983, 0.104],      
           [0.4935, 0.60342, 0.79073],      
           [0.19642, 0.38824, 0.6258],      
           [0.4601, 0.58235, 0.78958],      
           [0.23185, 0.41923, 0.6691],      
           [0.67332, 0.71747, 0.79403],      
           [0.057498, 0.13131, 0.20704],      
           [0.29259, 0.46688, 0.72457],      
           [0.01615, 0.031315, 0.05138],      
           [0.070924, 0.18381, 0.29422],      
           [0.34399, 0.50435, 0.75741],      
           [0.75926, 0.78073, 0.81827],      
           [0.060281, 0.14391, 0.22826],      
           [0.61464, 0.67891, 0.78957],      
           [0.55845, 0.64373, 0.78981],      
           [0.034477, 0.063258, 0.095163],      
           [0.31844, 0.48596, 0.74258],      
           [0.92088, 0.92353, 0.92804],      
           [0.055201, 0.11913, 0.18627],      
           [0.63382, 0.69121, 0.79027],      
           [0.50285, 0.60926, 0.79075],      
           [0.43518, 0.56631, 0.78702],      
           [0.24318, 0.42853, 0.68103],      
           [0.4142, 0.55255, 0.78326],      
           [0.16061, 0.35178, 0.56932],      
           [0.051245, 0.096126, 0.14619],      
           [0.10879, 0.27697, 0.44639],      
           [0.46979, 0.5885, 0.79013],      
           [0.57704, 0.65527, 0.7895],      
           [0.87225, 0.87793, 0.88781],      
           [0.96337, 0.96446, 0.96617],      
           [0.053115, 0.10741, 0.16595],      
           [0.53994, 0.63227, 0.79021],      
           [0.39208, 0.53772, 0.77743],      
           [0.17526, 0.36759, 0.59439],      
           [0.11699, 0.29169, 0.47064],      
           [0.20583, 0.39683, 0.63832],      
           [0.65334, 0.70401, 0.79167],      
           [0.89657, 0.90052, 0.90736],      
           [0.047784, 0.084964, 0.12697]]      
      
osloS_map = LinearSegmentedColormap.from_list('osloS', cm_data)      
# For use of "viscm view"      
test_cm = osloS_map      
      
if __name__ == "__main__":      
    import matplotlib.pyplot as plt      
    import numpy as np      
      
    try:      
        from viscm import viscm      
        viscm(osloS_map)      
    except ImportError:      
        print("viscm not found, falling back on simple display")      
        plt.imshow(np.linspace(0, 100, 256)[None, :], aspect='auto',      
                   cmap=osloS_map)      
    plt.show()      
