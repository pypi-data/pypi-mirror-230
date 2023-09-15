import numpy as np
import matplotlib.pyplot as plt

from camtest import list_setups
from egse.state import GlobalState


def path_length(route, cities, dist='inf'):
    """
    SYNOPSIS
    path_length(route,cities,dist='inf')

    INPUTS
    route  : route [1D array of indices]
    cities : cities [n,2] array of coordinates
    dist   : distance to be used, in ['euc', 'l2, 'l1, 'linf', 'euclidian', 'taxi', 'cab', 'infinite']
             'euc', 'euclidian', 'l2' : euclidian
             'cab', 'taxi', 'l1' : L1 norm
             'linf' : L-infinity norm
             'dist' drives the 'ord' parameter in numpy.linalg.norm

    OUTPUT
    Path length according to the selected distance metric
    """
    c,r = cities, route
    result = 0.
    if (dist.find('euc')>=0) or (dist.find('l2')>=0):
        for p in range(len(r)):
            result += np.linalg.norm(c[r[p]] - c[r[p - 1]], ord=2)
    elif (dist.find('cab')>=0) or (dist.find('l1')>=0) or (dist.find('taxi')>=0):
        for p in range(len(r)):
            result += np.linalg.norm(c[r[p]] - c[r[p - 1]], ord=1)
    elif (dist.find('inf')>=0):
        for p in range(len(r)):
            result += np.linalg.norm(c[r[p]]-c[r[p-1]], ord=np.inf)
    else:
        print("WARNING, distance not recognised")
        return None
    return result

# Calculate the euclidian distance in n-space of the route r traversing cities c, ending at the path start.
#path_distance = lambda r,c: np.sum([np.linalg.norm(c[r[p]]-c[r[p-1]]) for p in range(len(r))])

# Reverse the order of all elements from element i to element k in array r.
two_opt_swap = lambda r,i,k: np.concatenate((r[0:i],r[k:-len(r)+i-1:-1],r[k+1:len(r)]))


def tsp_brute(cities, improvement_threshold, dist='inf'):
    """
    Travelling Salesperson Algorithm
    2-opt Algorithm adapted from https://en.wikipedia.org/wiki/2-opt

    SYNOPSIS
    tsp_brute(cities,improvement_threshold, dist='inf')

    INPUTS
    cities                : input coordinates
    improvement_threshold :
    dist                  : distance metric to be used, see path_length
                            dist drives the 'ord' parameter in np.linalg.norm

    OUTPUT
    route                 : 1d array of the indices (sorting of cities to minimise the total path length)
    """
    route = np.arange(cities.shape[0])  # Make an array of row numbers corresponding to cities.
    improvement_factor = 1  # Initialize the improvement factor.
    #best_distance = path_distance(route,cities)  # Calculate the distance of the initial path.
    best_distance = path_length(route, cities, dist=dist)  # Calculate the distance of the initial path.
    while improvement_factor > improvement_threshold:  # If the route is still improving, keep going!
        distance_to_beat = best_distance  # Record the distance at the beginning of the loop.
        for swap_first in range(1, len(route)-2):  # From each city except the first and last,
            for swap_last in range(swap_first+1, len(route)):  # to each of the cities following,
                new_route = two_opt_swap(route, swap_first,swap_last)  # try reversing the order of these cities
                #new_distance = path_distance(new_route,cities)  # and check the total distance with this modification.
                new_distance = path_length(new_route, cities, dist=dist)  # and check the total distance with this modification.
                if new_distance < best_distance:  # If the path distance is an improvement,
                    route = new_route  # make this the accepted best route
                    best_distance = new_distance  # and update the distance corresponding to this route.
        improvement_factor = 1 - best_distance/distance_to_beat  # Calculate how much the route has improved.
    return route  # When the route is no longer improving substantially, stop searching and return the route.

#=============================================================

list_setups()
setup = GlobalState.setup

#=============================================================

thetas = np.array(setup.fov_positions.reference_full_40.theta)
phis = np.array(setup.fov_positions.reference_full_40.phi)

fova = np.stack([thetas,phis]).T
gimbal = angles_to_sron_gimbal_angles(fova)

cities = gimbal.copy()

routel2 = tsp_brute(cities, improvement_threshold=0.001, dist='l2')
routel1 = tsp_brute(cities, improvement_threshold=0.001, dist='l1')
routelinf = tsp_brute(cities, improvement_threshold=0.001, dist='linf')

route = routelinf
print(f"Rx: {gimbal[route,0]}")
print(f"Ry: {gimbal[route,1]}")
print(f"theta: {thetas[route]}")
print(f"phi: {phis[route]}")


plt.figure("OptimisationGimbalPathL2", figsize=(10,10))
plt.plot(gimbal[routel2,0], gimbal[routel2,1], 'go-')
plt.xlabel("SRON Gimbal Rx [deg]", size=14)
plt.ylabel("SRON Gimbal Ry [deg]", size=14)
plt.title("Gimbal angles - Hartmann 40 - SRON\nTSP opt L2-norm - Angular distance", size=14)
plt.grid(alpha=0.25)
#plt.savefig("/Users/pierre/plato/em/sron_meas_path_gimbal_optimized_norm_L2.png")

plt.figure("OptimisationGimbalPathL1", figsize=(10,10))
plt.plot(gimbal[routel1,0], gimbal[routel1,1],'go-')
plt.xlabel("SRON Gimbal Rx [deg]", size=14)
plt.ylabel("SRON Gimbal Ry [deg]", size=14)
plt.title("Gimbal angles - Hartmann 40 - SRON\nTSP opt L1-norm - Gimbal Rx Ry rotations sequential", size=14)
plt.grid(alpha=0.25)
#plt.savefig("/Users/pierre/plato/em/sron_meas_path_gimbal_optimized_norm_L1.png")

plt.figure("OptimisationGimbalPathLinf", figsize=(10,10))
plt.plot(gimbal[routelinf,0], gimbal[routelinf,1], 'go-')
plt.xlabel("SRON Gimbal Rx [deg]", size=14)
plt.ylabel("SRON Gimbal Ry [deg]", size=14)
plt.title("Gimbal angles - Hartmann 40 - SRON\nTSP opt Linf-norm - Gimbal Rx Ry rotations simultaneous", size=14)
plt.grid(alpha=0.25)
#plt.savefig("/Users/pierre/plato/em/sron_meas_path_gimbal_optimized_norm_Linfinity.png")

plt.figure("GimbalPath", figsize=(10,10))
plt.plot(gimbal[:,0], gimbal[:,1], 'ko-', "raw")
plt.xlabel("SRON Gimbal Rx [deg]", size=14)
plt.ylabel("SRON Gimbal Ry [deg]",size=14)
plt.title("Gimbal angles - Hartmann 40 - SRON\nSorted In Azimuth", size=14)
plt.grid(alpha=0.25)
#plt.plot(gimbal[route,0], gimbal[route,1],'ro-', 'optimised')
#plt.legend()
#plt.savefig("/Users/pierre/plato/em/sron_meas_path_gimbal_sorted_in_azimuth.png")

