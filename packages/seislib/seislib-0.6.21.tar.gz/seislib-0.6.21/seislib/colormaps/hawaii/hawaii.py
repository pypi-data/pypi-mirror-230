# 
#         hawaii
#                   www.fabiocrameri.ch/colourmaps
from matplotlib.colors import LinearSegmentedColormap      
      
cm_data = [[0.55054, 0.006842, 0.45198],      
           [0.55149, 0.015367, 0.44797],      
           [0.55243, 0.023795, 0.444],      
           [0.55333, 0.032329, 0.44002],      
           [0.55423, 0.04117, 0.43606],      
           [0.5551, 0.049286, 0.43213],      
           [0.55595, 0.056667, 0.42819],      
           [0.5568, 0.063525, 0.42427],      
           [0.55762, 0.06997, 0.42038],      
           [0.55841, 0.076028, 0.41651],      
           [0.55921, 0.081936, 0.41266],      
           [0.55999, 0.087507, 0.40882],      
           [0.56075, 0.092811, 0.40501],      
           [0.56149, 0.098081, 0.40124],      
           [0.56224, 0.10313, 0.39747],      
           [0.56295, 0.108, 0.39374],      
           [0.56366, 0.11287, 0.39002],      
           [0.56435, 0.11753, 0.38634],      
           [0.56503, 0.12212, 0.3827],      
           [0.56571, 0.12668, 0.37907],      
           [0.56638, 0.13117, 0.37547],      
           [0.56704, 0.13554, 0.3719],      
           [0.56768, 0.13987, 0.36838],      
           [0.56831, 0.1442, 0.36486],      
           [0.56894, 0.14842, 0.36138],      
           [0.56956, 0.15262, 0.35794],      
           [0.57017, 0.15681, 0.35452],      
           [0.57078, 0.16093, 0.35113],      
           [0.57138, 0.16501, 0.34776],      
           [0.57197, 0.16912, 0.34442],      
           [0.57256, 0.17313, 0.34112],      
           [0.57314, 0.17717, 0.33784],      
           [0.57371, 0.18114, 0.3346],      
           [0.57428, 0.18515, 0.33136],      
           [0.57484, 0.18909, 0.32817],      
           [0.57541, 0.19304, 0.32499],      
           [0.57597, 0.19698, 0.32185],      
           [0.57652, 0.20085, 0.31874],      
           [0.57706, 0.20478, 0.31565],      
           [0.5776, 0.20866, 0.31256],      
           [0.57814, 0.21254, 0.30954],      
           [0.57868, 0.21643, 0.30652],      
           [0.57921, 0.22029, 0.3035],      
           [0.57975, 0.22411, 0.30052],      
           [0.58027, 0.22798, 0.29757],      
           [0.58079, 0.23182, 0.29462],      
           [0.58131, 0.23565, 0.29171],      
           [0.58183, 0.23946, 0.28881],      
           [0.58235, 0.24327, 0.28591],      
           [0.58287, 0.2471, 0.28307],      
           [0.58339, 0.25092, 0.2802],      
           [0.5839, 0.25474, 0.27738],      
           [0.58442, 0.25853, 0.27455],      
           [0.58493, 0.26234, 0.27174],      
           [0.58544, 0.26616, 0.26898],      
           [0.58595, 0.26997, 0.2662],      
           [0.58646, 0.27377, 0.26344],      
           [0.58696, 0.27758, 0.26068],      
           [0.58747, 0.28137, 0.25793],      
           [0.58797, 0.28518, 0.25522],      
           [0.58848, 0.28901, 0.25249],      
           [0.58898, 0.29282, 0.24977],      
           [0.58949, 0.29665, 0.24708],      
           [0.59, 0.30047, 0.24438],      
           [0.59051, 0.3043, 0.24172],      
           [0.59102, 0.30814, 0.23903],      
           [0.59153, 0.31197, 0.23638],      
           [0.59204, 0.31585, 0.23369],      
           [0.59255, 0.3197, 0.23106],      
           [0.59305, 0.32356, 0.22842],      
           [0.59356, 0.32743, 0.22577],      
           [0.59407, 0.33131, 0.22313],      
           [0.59458, 0.33523, 0.22051],      
           [0.5951, 0.33913, 0.21787],      
           [0.59561, 0.34305, 0.21523],      
           [0.59613, 0.34698, 0.21261],      
           [0.59664, 0.35092, 0.20999],      
           [0.59716, 0.35488, 0.20739],      
           [0.59768, 0.35883, 0.20478],      
           [0.5982, 0.36282, 0.20215],      
           [0.59872, 0.36683, 0.19953],      
           [0.59925, 0.37084, 0.19696],      
           [0.59977, 0.37488, 0.19437],      
           [0.60029, 0.37893, 0.19174],      
           [0.60082, 0.38301, 0.18915],      
           [0.60135, 0.38709, 0.18655],      
           [0.60187, 0.39122, 0.18395],      
           [0.6024, 0.39535, 0.18134],      
           [0.60293, 0.39949, 0.17878],      
           [0.60346, 0.40368, 0.17616],      
           [0.604, 0.40787, 0.17359],      
           [0.60452, 0.4121, 0.17101],      
           [0.60504, 0.41635, 0.16844],      
           [0.60556, 0.42062, 0.16585],      
           [0.60608, 0.42493, 0.16332],      
           [0.60661, 0.42925, 0.16073],      
           [0.60713, 0.4336, 0.1582],      
           [0.60764, 0.438, 0.15565],      
           [0.60814, 0.44241, 0.15309],      
           [0.60864, 0.44685, 0.15058],      
           [0.60913, 0.45132, 0.14807],      
           [0.60961, 0.45583, 0.14561],      
           [0.61008, 0.46036, 0.14312],      
           [0.61054, 0.46493, 0.14069],      
           [0.61099, 0.46954, 0.13827],      
           [0.61142, 0.47417, 0.13583],      
           [0.61183, 0.47884, 0.13351],      
           [0.61223, 0.48354, 0.13121],      
           [0.6126, 0.48829, 0.12892],      
           [0.61295, 0.49305, 0.12672],      
           [0.61327, 0.49788, 0.12457],      
           [0.61357, 0.5027, 0.12249],      
           [0.61384, 0.50759, 0.12051],      
           [0.61407, 0.5125, 0.11867],      
           [0.61426, 0.51746, 0.11685],      
           [0.61442, 0.52243, 0.11516],      
           [0.61453, 0.52746, 0.11366],      
           [0.61459, 0.53251, 0.11227],      
           [0.61461, 0.53759, 0.11103],      
           [0.61457, 0.54271, 0.11],      
           [0.61447, 0.54785, 0.10911],      
           [0.61431, 0.55302, 0.10842],      
           [0.61408, 0.55821, 0.10801],      
           [0.61379, 0.56345, 0.10785],      
           [0.61342, 0.56868, 0.10794],      
           [0.61297, 0.57395, 0.10831],      
           [0.61245, 0.57923, 0.10903],      
           [0.61184, 0.58452, 0.11004],      
           [0.61115, 0.58982, 0.11132],      
           [0.61035, 0.59513, 0.11296],      
           [0.60947, 0.60044, 0.11486],      
           [0.60849, 0.60575, 0.11717],      
           [0.60741, 0.61106, 0.11981],      
           [0.60622, 0.61635, 0.12276],      
           [0.60493, 0.62162, 0.12612],      
           [0.60354, 0.62688, 0.12976],      
           [0.60203, 0.63211, 0.13369],      
           [0.60041, 0.63731, 0.13797],      
           [0.59869, 0.64247, 0.1425],      
           [0.59686, 0.64759, 0.14733],      
           [0.59492, 0.65266, 0.15242],      
           [0.59287, 0.6577, 0.15779],      
           [0.59071, 0.66267, 0.16342],      
           [0.58844, 0.66758, 0.16926],      
           [0.58608, 0.67243, 0.17528],      
           [0.58361, 0.67721, 0.18151],      
           [0.58105, 0.68192, 0.18799],      
           [0.57839, 0.68656, 0.19459],      
           [0.57565, 0.69112, 0.20131],      
           [0.57281, 0.69561, 0.20824],      
           [0.56988, 0.70002, 0.21528],      
           [0.56689, 0.70435, 0.22247],      
           [0.56381, 0.7086, 0.22974],      
           [0.56066, 0.71275, 0.23717],      
           [0.55746, 0.71684, 0.24462],      
           [0.55418, 0.72084, 0.25222],      
           [0.55085, 0.72477, 0.25987],      
           [0.54747, 0.7286, 0.26757],      
           [0.54404, 0.73238, 0.27539],      
           [0.54057, 0.73606, 0.28324],      
           [0.53707, 0.73968, 0.29114],      
           [0.53351, 0.74323, 0.29909],      
           [0.52994, 0.7467, 0.30708],      
           [0.52633, 0.75011, 0.31511],      
           [0.5227, 0.75346, 0.32319],      
           [0.51905, 0.75675, 0.33128],      
           [0.51537, 0.75998, 0.33944],      
           [0.51168, 0.76316, 0.3476],      
           [0.50799, 0.76629, 0.35578],      
           [0.50428, 0.76937, 0.36398],      
           [0.50055, 0.77241, 0.37222],      
           [0.49682, 0.77541, 0.38048],      
           [0.49309, 0.77836, 0.38876],      
           [0.48935, 0.78129, 0.39705],      
           [0.48561, 0.78418, 0.40538],      
           [0.48188, 0.78704, 0.41371],      
           [0.47814, 0.78987, 0.42206],      
           [0.47441, 0.79267, 0.43044],      
           [0.47068, 0.79546, 0.43882],      
           [0.46695, 0.79822, 0.44724],      
           [0.46322, 0.80096, 0.45567],      
           [0.45952, 0.80369, 0.46412],      
           [0.45581, 0.80641, 0.47258],      
           [0.45212, 0.80911, 0.48105],      
           [0.44844, 0.8118, 0.48955],      
           [0.44477, 0.81447, 0.49809],      
           [0.44111, 0.81714, 0.50662],      
           [0.43749, 0.8198, 0.51517],      
           [0.43386, 0.82246, 0.52375],      
           [0.43028, 0.82511, 0.53235],      
           [0.42672, 0.82776, 0.54096],      
           [0.42319, 0.8304, 0.5496],      
           [0.41971, 0.83304, 0.55824],      
           [0.41626, 0.83567, 0.56692],      
           [0.41287, 0.83831, 0.57561],      
           [0.40952, 0.84094, 0.58431],      
           [0.40624, 0.84356, 0.59304],      
           [0.40304, 0.84619, 0.60178],      
           [0.3999, 0.84882, 0.61054],      
           [0.39687, 0.85144, 0.61932],      
           [0.39395, 0.85406, 0.6281],      
           [0.39115, 0.85668, 0.63691],      
           [0.38847, 0.8593, 0.64571],      
           [0.38593, 0.86192, 0.65453],      
           [0.38359, 0.86453, 0.66337],      
           [0.38141, 0.86713, 0.6722],      
           [0.37942, 0.86973, 0.68102],      
           [0.37767, 0.87232, 0.68986],      
           [0.37617, 0.87491, 0.69869],      
           [0.37492, 0.87748, 0.70751],      
           [0.37398, 0.88005, 0.71632],      
           [0.37334, 0.8826, 0.72511],      
           [0.37304, 0.88514, 0.73387],      
           [0.37311, 0.88765, 0.7426],      
           [0.37357, 0.89016, 0.7513],      
           [0.37444, 0.89264, 0.75995],      
           [0.37572, 0.8951, 0.76855],      
           [0.37747, 0.89752, 0.7771],      
           [0.37967, 0.89992, 0.78557],      
           [0.38235, 0.90229, 0.79397],      
           [0.38553, 0.90462, 0.80228],      
           [0.38921, 0.90691, 0.8105],      
           [0.39338, 0.90916, 0.81862],      
           [0.39807, 0.91137, 0.82663],      
           [0.40326, 0.91353, 0.83451],      
           [0.40893, 0.91563, 0.84226],      
           [0.41508, 0.91769, 0.84986],      
           [0.4217, 0.91968, 0.85731],      
           [0.42879, 0.92161, 0.86461],      
           [0.43631, 0.92349, 0.87173],      
           [0.44423, 0.92529, 0.87868],      
           [0.45254, 0.92703, 0.88545],      
           [0.4612, 0.9287, 0.89204],      
           [0.47021, 0.93031, 0.89842],      
           [0.47952, 0.93184, 0.90462],      
           [0.4891, 0.9333, 0.91062],      
           [0.49895, 0.93469, 0.91641],      
           [0.50902, 0.936, 0.92201],      
           [0.51928, 0.93725, 0.92739],      
           [0.52972, 0.93842, 0.93259],      
           [0.54029, 0.93952, 0.93759],      
           [0.551, 0.94055, 0.9424],      
           [0.5618, 0.94151, 0.94702],      
           [0.57269, 0.94241, 0.95146],      
           [0.58362, 0.94324, 0.95573],      
           [0.59461, 0.94402, 0.95982],      
           [0.60561, 0.94473, 0.96377],      
           [0.61664, 0.94539, 0.96756],      
           [0.62765, 0.94599, 0.97121],      
           [0.63865, 0.94654, 0.97474],      
           [0.64962, 0.94705, 0.97815],      
           [0.66055, 0.94751, 0.98145],      
           [0.67144, 0.94793, 0.98465],      
           [0.68228, 0.94832, 0.98777],      
           [0.69306, 0.94866, 0.9908],      
           [0.70378, 0.94898, 0.99377]]      
      
hawaii_map = LinearSegmentedColormap.from_list('hawaii', cm_data)      
# For use of "viscm view"      
test_cm = hawaii_map      
      
if __name__ == "__main__":      
    import matplotlib.pyplot as plt      
    import numpy as np      
      
    try:      
        from viscm import viscm      
        viscm(hawaii_map)      
    except ImportError:      
        print("viscm not found, falling back on simple display")      
        plt.imshow(np.linspace(0, 100, 256)[None, :], aspect='auto',      
                   cmap=hawaii_map)      
    plt.show()      
