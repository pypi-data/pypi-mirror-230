# 
#         bamO
#                   www.fabiocrameri.ch/colourmaps
from matplotlib.colors import LinearSegmentedColormap      
      
cm_data = [[0.30946, 0.18635, 0.26374],      
           [0.31419, 0.18609, 0.2688],      
           [0.31943, 0.18615, 0.27428],      
           [0.32515, 0.18655, 0.2802],      
           [0.33135, 0.18735, 0.28652],      
           [0.33801, 0.18851, 0.29323],      
           [0.34509, 0.19002, 0.30029],      
           [0.35254, 0.19193, 0.30766],      
           [0.36032, 0.19424, 0.3153],      
           [0.36841, 0.19687, 0.32316],      
           [0.37673, 0.19981, 0.33118],      
           [0.38522, 0.20312, 0.33937],      
           [0.39388, 0.20673, 0.34762],      
           [0.40263, 0.21057, 0.35593],      
           [0.41144, 0.21468, 0.36426],      
           [0.42029, 0.21903, 0.37259],      
           [0.42913, 0.22357, 0.3809],      
           [0.43796, 0.22831, 0.38916],      
           [0.44674, 0.23316, 0.39735],      
           [0.45546, 0.2382, 0.40548],      
           [0.46412, 0.24335, 0.41353],      
           [0.47268, 0.24864, 0.42148],      
           [0.48116, 0.25399, 0.42936],      
           [0.48954, 0.25945, 0.43714],      
           [0.49784, 0.26495, 0.44482],      
           [0.506, 0.27056, 0.45241],      
           [0.51409, 0.2762, 0.45989],      
           [0.52204, 0.28188, 0.46728],      
           [0.52991, 0.2876, 0.47457],      
           [0.53765, 0.29337, 0.48176],      
           [0.54528, 0.29918, 0.48885],      
           [0.55279, 0.30499, 0.49584],      
           [0.5602, 0.31084, 0.50275],      
           [0.56749, 0.31669, 0.50956],      
           [0.57466, 0.32257, 0.51626],      
           [0.58173, 0.32844, 0.52289],      
           [0.58869, 0.33433, 0.52942],      
           [0.59554, 0.34023, 0.53586],      
           [0.60229, 0.34612, 0.54222],      
           [0.60895, 0.35204, 0.5485],      
           [0.6155, 0.35798, 0.5547],      
           [0.62197, 0.36392, 0.56083],      
           [0.62837, 0.36989, 0.56692],      
           [0.63469, 0.3759, 0.57295],      
           [0.64095, 0.38195, 0.57894],      
           [0.64717, 0.38805, 0.5849],      
           [0.65334, 0.39422, 0.59083],      
           [0.65949, 0.40047, 0.59676],      
           [0.66561, 0.40678, 0.60268],      
           [0.6717, 0.41319, 0.60861],      
           [0.67779, 0.41968, 0.61452],      
           [0.68385, 0.42627, 0.62046],      
           [0.68991, 0.43298, 0.6264],      
           [0.69595, 0.43978, 0.63234],      
           [0.70196, 0.44669, 0.6383],      
           [0.70796, 0.45371, 0.64425],      
           [0.71393, 0.46083, 0.65021],      
           [0.71988, 0.46807, 0.65616],      
           [0.72579, 0.47542, 0.66211],      
           [0.73165, 0.48285, 0.66804],      
           [0.73747, 0.4904, 0.67395],      
           [0.74325, 0.49806, 0.67983],      
           [0.74896, 0.50579, 0.6857],      
           [0.75461, 0.51364, 0.69151],      
           [0.76017, 0.52157, 0.69729],      
           [0.76567, 0.52959, 0.70301],      
           [0.77107, 0.53769, 0.70868],      
           [0.77637, 0.54587, 0.71426],      
           [0.78156, 0.5541, 0.71977],      
           [0.78664, 0.5624, 0.72519],      
           [0.79159, 0.57073, 0.73049],      
           [0.7964, 0.57911, 0.73569],      
           [0.80107, 0.5875, 0.74075],      
           [0.80558, 0.59592, 0.74568],      
           [0.80993, 0.60432, 0.75046],      
           [0.8141, 0.61269, 0.75507],      
           [0.81809, 0.62103, 0.75949],      
           [0.82189, 0.6293, 0.76373],      
           [0.82548, 0.6375, 0.76776],      
           [0.82887, 0.64559, 0.77159],      
           [0.83204, 0.65356, 0.77518],      
           [0.83499, 0.66138, 0.77853],      
           [0.83772, 0.66905, 0.78165],      
           [0.84023, 0.67653, 0.78452],      
           [0.84252, 0.68381, 0.78713],      
           [0.84458, 0.69088, 0.78948],      
           [0.84641, 0.69773, 0.79158],      
           [0.84804, 0.70434, 0.79344],      
           [0.84947, 0.71071, 0.79503],      
           [0.85068, 0.71682, 0.79639],      
           [0.8517, 0.72267, 0.7975],      
           [0.85255, 0.72828, 0.79839],      
           [0.8532, 0.73363, 0.79906],      
           [0.85369, 0.73873, 0.79951],      
           [0.85402, 0.74357, 0.79976],      
           [0.8542, 0.74817, 0.79982],      
           [0.85425, 0.75252, 0.79969],      
           [0.85415, 0.75664, 0.79939],      
           [0.85394, 0.76053, 0.79892],      
           [0.85361, 0.7642, 0.79831],      
           [0.85318, 0.76766, 0.79755],      
           [0.85265, 0.77091, 0.79666],      
           [0.85202, 0.77396, 0.79565],      
           [0.8513, 0.77682, 0.79453],      
           [0.85052, 0.77949, 0.7933],      
           [0.84966, 0.78199, 0.79197],      
           [0.84873, 0.78432, 0.79056],      
           [0.84774, 0.78649, 0.78907],      
           [0.84669, 0.7885, 0.78749],      
           [0.84559, 0.79037, 0.78585],      
           [0.84444, 0.7921, 0.78414],      
           [0.84323, 0.7937, 0.78235],      
           [0.84198, 0.79517, 0.7805],      
           [0.84068, 0.79652, 0.77858],      
           [0.83931, 0.79777, 0.77659],      
           [0.83789, 0.79891, 0.77451],      
           [0.83639, 0.79995, 0.77234],      
           [0.83483, 0.80089, 0.77007],      
           [0.83318, 0.80174, 0.76769],      
           [0.83143, 0.8025, 0.76519],      
           [0.82958, 0.80316, 0.76254],      
           [0.8276, 0.80372, 0.75972],      
           [0.82549, 0.80417, 0.75674],      
           [0.82324, 0.80452, 0.75355],      
           [0.82081, 0.80473, 0.75014],      
           [0.8182, 0.80482, 0.7465],      
           [0.8154, 0.80475, 0.74259],      
           [0.81237, 0.80452, 0.7384],      
           [0.80912, 0.8041, 0.73391],      
           [0.8056, 0.80348, 0.7291],      
           [0.80181, 0.80264, 0.72394],      
           [0.79772, 0.80155, 0.71842],      
           [0.79333, 0.80019, 0.71252],      
           [0.78861, 0.79852, 0.70623],      
           [0.78354, 0.79653, 0.69951],      
           [0.77812, 0.79421, 0.69239],      
           [0.77232, 0.79152, 0.68483],      
           [0.76617, 0.78844, 0.67687],      
           [0.75964, 0.78497, 0.66849],      
           [0.75277, 0.78109, 0.65973],      
           [0.74556, 0.77681, 0.65062],      
           [0.73803, 0.77211, 0.64118],      
           [0.73022, 0.76703, 0.63148],      
           [0.72215, 0.76158, 0.62155],      
           [0.71388, 0.75578, 0.61146],      
           [0.70545, 0.74966, 0.60126],      
           [0.69689, 0.74325, 0.591],      
           [0.68825, 0.73658, 0.58073],      
           [0.67956, 0.7297, 0.57051],      
           [0.67088, 0.72262, 0.56039],      
           [0.66223, 0.71541, 0.55039],      
           [0.65362, 0.70805, 0.54055],      
           [0.6451, 0.70061, 0.53089],      
           [0.63668, 0.6931, 0.52144],      
           [0.62837, 0.68555, 0.51221],      
           [0.62019, 0.67796, 0.5032],      
           [0.61213, 0.67037, 0.49445],      
           [0.60424, 0.66277, 0.48591],      
           [0.59647, 0.65519, 0.47762],      
           [0.58885, 0.64764, 0.46958],      
           [0.58139, 0.64013, 0.46176],      
           [0.57407, 0.63266, 0.45418],      
           [0.56691, 0.62524, 0.44682],      
           [0.55989, 0.61787, 0.43969],      
           [0.55301, 0.61056, 0.43278],      
           [0.54628, 0.60331, 0.42607],      
           [0.53968, 0.59613, 0.41958],      
           [0.53323, 0.58901, 0.41328],      
           [0.52691, 0.58197, 0.40717],      
           [0.52072, 0.57499, 0.40126],      
           [0.51466, 0.56809, 0.39552],      
           [0.50873, 0.56127, 0.38995],      
           [0.50291, 0.55452, 0.38457],      
           [0.49723, 0.54784, 0.37934],      
           [0.49166, 0.54122, 0.37429],      
           [0.48619, 0.5347, 0.36937],      
           [0.48083, 0.52824, 0.3646],      
           [0.4756, 0.52184, 0.35997],      
           [0.47045, 0.51551, 0.35549],      
           [0.46539, 0.50926, 0.35112],      
           [0.46042, 0.50304, 0.34688],      
           [0.45555, 0.49689, 0.34274],      
           [0.45075, 0.49079, 0.33871],      
           [0.446, 0.4847, 0.33479],      
           [0.44132, 0.47866, 0.33092],      
           [0.4367, 0.47263, 0.32716],      
           [0.43213, 0.46662, 0.32347],      
           [0.42759, 0.46061, 0.31986],      
           [0.42308, 0.45463, 0.31631],      
           [0.41862, 0.44863, 0.31281],      
           [0.41419, 0.44264, 0.30939],      
           [0.40981, 0.43664, 0.30602],      
           [0.40545, 0.43065, 0.30268],      
           [0.40113, 0.42467, 0.29945],      
           [0.39683, 0.41869, 0.29625],      
           [0.39259, 0.41275, 0.2931],      
           [0.3884, 0.4068, 0.29003],      
           [0.38424, 0.40089, 0.28701],      
           [0.38015, 0.39499, 0.28407],      
           [0.37611, 0.38915, 0.28119],      
           [0.37212, 0.38334, 0.27839],      
           [0.3682, 0.37757, 0.27566],      
           [0.36434, 0.37185, 0.27297],      
           [0.36055, 0.36621, 0.27038],      
           [0.35687, 0.3606, 0.26783],      
           [0.35323, 0.35511, 0.26539],      
           [0.34969, 0.34967, 0.26303],      
           [0.34622, 0.3443, 0.26073],      
           [0.34287, 0.33906, 0.25851],      
           [0.33959, 0.33389, 0.25637],      
           [0.33639, 0.32882, 0.25434],      
           [0.33333, 0.32385, 0.25237],      
           [0.33034, 0.319, 0.25047],      
           [0.32745, 0.31425, 0.2487],      
           [0.32467, 0.30964, 0.24696],      
           [0.32201, 0.30512, 0.24532],      
           [0.31944, 0.30072, 0.24377],      
           [0.31698, 0.29645, 0.24231],      
           [0.3146, 0.29228, 0.24091],      
           [0.31233, 0.28823, 0.23961],      
           [0.31019, 0.28428, 0.23837],      
           [0.3081, 0.28043, 0.23723],      
           [0.30614, 0.27671, 0.23613],      
           [0.30423, 0.27305, 0.23512],      
           [0.30241, 0.26949, 0.23415],      
           [0.30069, 0.266, 0.23325],      
           [0.29906, 0.26257, 0.23245],      
           [0.29748, 0.25922, 0.2317],      
           [0.29598, 0.25589, 0.231],      
           [0.29455, 0.25265, 0.23036],      
           [0.29321, 0.24943, 0.22979],      
           [0.29194, 0.24625, 0.22931],      
           [0.29073, 0.2431, 0.2289],      
           [0.28961, 0.23999, 0.22856],      
           [0.28856, 0.23693, 0.22829],      
           [0.28759, 0.23383, 0.22809],      
           [0.28672, 0.2308, 0.22799],      
           [0.28595, 0.2278, 0.22799],      
           [0.28529, 0.22478, 0.22809],      
           [0.28474, 0.22184, 0.2283],      
           [0.28432, 0.21894, 0.22864],      
           [0.28404, 0.21608, 0.22909],      
           [0.28391, 0.21323, 0.22969],      
           [0.28395, 0.21048, 0.23047],      
           [0.28417, 0.20779, 0.23145],      
           [0.28459, 0.20518, 0.23258],      
           [0.28523, 0.20265, 0.23393],      
           [0.28613, 0.20023, 0.23553],      
           [0.28729, 0.19795, 0.23737],      
           [0.28876, 0.19581, 0.23946],      
           [0.29053, 0.19383, 0.24186],      
           [0.29265, 0.19199, 0.24455],      
           [0.29515, 0.19037, 0.24764],      
           [0.29805, 0.18898, 0.25106],      
           [0.30139, 0.18785, 0.25488],      
           [0.30519, 0.18694, 0.2591]]      
      
bamO_map = LinearSegmentedColormap.from_list('bamO', cm_data)      
# For use of "viscm view"      
test_cm = bamO_map      
      
if __name__ == "__main__":      
    import matplotlib.pyplot as plt      
    import numpy as np      
      
    try:      
        from viscm import viscm      
        viscm(bamO_map)      
    except ImportError:      
        print("viscm not found, falling back on simple display")      
        plt.imshow(np.linspace(0, 100, 256)[None, :], aspect='auto',      
                   cmap=bamO_map)      
    plt.show()      
