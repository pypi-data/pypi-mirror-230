"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.1 CAM-TVPT-010 Camera best focus determination

N-CAM

Synopsis:
    - compute EEF in 2x2 pixels (and 3x3 pixels TBC) for all the acquired 
    images at all temperatures T
    - save them into a file: T columns (baseline 5 temperatures) and N+1 lines
    (N FoV positions acquired)
    - plot distribution of EEF2 for each temperature, save mean and std values
    - fit polynom over the 5 mean EEF2
    - compute and save maximum --> best focus temperature
    
This file provides only a library of functions that are called in a Juypter 
Notebook to evaluate the data acquired at the TH.

Authors: M. Pertenais

Versions:
    2021 03 23 - 0.1 Draft -- Creation
    2021 10 27 - 0.2 Draft 
    2022 07 27 - 1.0 Formal Issue 1.0 (== draft 0.2) that was used for the EM analysis


"""
 
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize          

def maxeef(image, imagette_size = 8, verbose = False):
    '''
    Parameters
    ----------
    image : np.array 
    imagette_size : integer defining the reference imagette size 
    to normalize the EEF: The default is 8.

    Returns
    -------
    bpff : max Brightest Pixel Flux Fraction of this PSF 
    max_eef2 : max Ensquared Energy fraction in 2x2 pixels
    max_eef3 : max Ensquared Energy fraction in 3x3 pixels

    '''
    #row_centroid, column_centroid = get_centroid_single_image(image)
    row_centroid, column_centroid = get_brightest_pixel_coordinate(image)
        
    row_max     = int(min(row_centroid + imagette_size/2,image.shape[0]))
    row_min     = int(max(row_centroid - imagette_size/2,0))
    column_max  = int(min(column_centroid + imagette_size/2,image.shape[1]))
    column_min  = int(max(column_centroid - imagette_size/2,0))
    #ee_reference = 0
    ee1_signal = 0.0  
    ee2_signal = 0.0 
    ee3_signal = 0.0

    image_cropped = image[row_min:row_max, column_min:column_max]
        
    ee_reference = np.sum(image_cropped)
    
    for row in range(np.size(image_cropped,0)):
        for column in range(np.size(image_cropped,1)):

            #weight = image_cropped[row][column]
            #ee_reference    += weight
                
            ee1_signal = max(ee1_signal, image_cropped[row][column])
            
            if column < (np.size(image_cropped,1)) and row < (np.size(image_cropped,0)):
                ee2_signal = max(ee2_signal, 
                                 np.sum(image_cropped[row:row + 2, column:column + 2]))
                
            if column < (np.size(image_cropped,1) - 1) and row < (np.size(image_cropped,0) - 1):
                ee3_signal = max(ee3_signal, 
                                 np.sum(image_cropped[row:row + 3, column:column + 3]))
                
    bpff = ee1_signal / ee_reference
    max_eef2 = ee2_signal / ee_reference  
    max_eef3 = ee3_signal / ee_reference  
    
    if verbose == True:
        print("centroid = ", [row_centroid, column_centroid], "rows =", 
              [row_min, row_max], "columns =", [column_min, column_max])
        
        print("BPFF =", round(bpff * 100,2), "%","\n"
         "EEF in 2x2 pix =", round(max_eef2 * 100, 2), "%","\n"
         "EEF in 3x3 pix =", round(max_eef3 * 100, 2), "%")
        
        plt.imshow(image_cropped, cmap='binary')
        plt.show()
    
    return bpff, max_eef2, max_eef3  


def eef_vs_temp(fffiles, temperatures, imagette_size = 8):
    """ 
    Compute the Mean Ensquared Energy fraction in 2x2 pixels 
    using PSFs for XXXX star positions on the CCDs and temperatures
    
    Args: temperatures: vector with temperatures. Eg. [-90, -85, -80, -75, -70]
    num_subpixel: integer number of subpixels acquisitions per FoV position
    fffiles is a 3D array with first argument the temperature, 2nd the star ID 
    and 3rd the frame # at this FoV position
    Example: fffiles[0,19,2] provides the data of the 3rd fits file 
    for the 20th star at the 1st temperature analyzed

    
    Output:   np.array with the EEF in 2x2 pixels for all 40 stars (40 rows)
    and all 5 temperatures (5 columns) 
    """

    num_layers = np.size(fffiles,2)
    number_star = np.size(fffiles,1)
    
    table1 = [[0 for _ in range(len(temperatures))] for _ in range(number_star)]
    table2 = [[0 for _ in range(len(temperatures))] for _ in range(number_star)]
    table3 = [[0 for _ in range(len(temperatures))] for _ in range(number_star)]
    #table=np.zeros(len(temperatures),number_star))
    

    
    for tt in range(len(temperatures)):
        print("Start of analysis of temperature:", temperatures[tt], "°C")
        
        for star_ID in range(number_star):
            # open all the files for this temperature and FoV position
            #simtemp = fffiles[temperatures.index(temp)][star_ID]
            simtemp = fffiles[tt,star_ID,:]
            
            bpff, eef2, eef3 = 0, 0, 0
            bpff_temp, eef2_temp, eef3_temp = 0, 0, 0
            layer_max = 0
    
            for subpixel in range(num_layers):
                #compute the EEF and add it to an array

                PSF = simtemp[subpixel]
                bpff_temp, eef2_temp, eef3_temp = maxeef(PSF, imagette_size=imagette_size, verbose = False)   
                if abs(eef2_temp) > abs(eef2):
                    layer_max = subpixel
                bpff = max(abs(bpff_temp), abs(bpff))
                eef2 = max(abs(eef2_temp), abs(eef2))
                eef3 = max(abs(eef3_temp), abs(eef3))
                print("Script done with star position #",star_ID+1, ", and layer:",subpixel)
                print("EE2F =",eef2_temp)
                
            table1[star_ID][tt] = bpff
            table2[star_ID][tt] = eef2
            table3[star_ID][tt] = eef3
            print("Script done with star position #",star_ID+1, ", FYI: EEF in 2x2 pixels is:",eef2, "layer ID is:",layer_max)
            
    np.savetxt("eef_in_2x2pixels" + str(temperatures), table2, fmt='%.18e', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)
    np.savetxt("eef_in_3x3pixels" + str(temperatures), table3, fmt='%.18e', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)
    
    print("Script execution was succesful")
    return table1,table2, table3
  
  
def argmax_cubic(k_1, k_2, k_3):
    # return value x_0 of f(x) = k_3 x³ + k_2 x² + k_1 x  where attains its maximum
    a = 3*k_3
    b = 2*k_2
    c = k_1
    d = b**2 - 4*a*c
    poly = lambda x: (k_1*x + k_2*x**2 + k_3*x**3)
    if d >= 0:
        if b > 0:
            root1 = (- b - np.sqrt(d))/(2*a)
        else:
            root1 = (- b + np.sqrt(d))/(2*a)
        root2 = c/(a*root1) # use Vieta's Theorem -> avoid Loss of significance
        if (poly(root1) > poly(root2)):
            return root1
        else:
            return root2
    else:
        print("No maximum found!")
        return np.nan
    
    
def fit_eef(table, temps, verbose=True):
    """
    data : table saved by eef_vs_temp() with a column per temperature and EEF values for each FoV positions

    Returns: the best focus temperature
    """
    data = table
    
    # calculate mean[position][temperature] and std with respect to all N_STAR stars
    mean_eef = np.mean(data, axis = 0)
    std_eef = np.std(data, axis = 0)
    
    def poly3(T, a_0, a_1, a_2, a_3):
        return a_0 + a_1*T + a_2*(T**2) + a_3*(T**3)
    
    poly_fit_params, cov = optimize.curve_fit(poly3, temps, mean_eef, sigma = std_eef)
    argmax = argmax_cubic(poly_fit_params[1], poly_fit_params[2], poly_fit_params[3])
    optimal_temps = argmax
    
    if verbose == True:
        plt.figure(figsize = (12,9))
        plt.xlim((-92, -68))
        plt.xlabel("temperature [°C]", fontsize = 'x-large')
        plt.ylabel("mean ensquared energy fraction", fontsize = 'x-large')
        plt.ylim((0.33,1))
        plt.title("Polynomial LSF of mean ensquared energy fraction", fontsize = 'xx-large')
        plt.grid()
        
        plot_temps = np.linspace(-95, -65, 500)
        
        plt.scatter(temps, mean_eef)
        plt.errorbar(temps, mean_eef, yerr=std_eef, fmt="o")
        plt.plot(plot_temps, poly3(plot_temps, poly_fit_params[0], poly_fit_params[1], 
                                   poly_fit_params[2], poly_fit_params[3]), label='Polynominal Fit', c = 'C0')
        plt.axvline(x=optimal_temps, label = 'Best Focus Temperature', c='k')
        plt.legend(loc = "upper left", fontsize = 'x-large', shadow = True)
        plt.show()
        
    print("The best focus temperature is:", round(optimal_temps))
    
    return optimal_temps


    

################################################################################
### EQUI-SURFACE DISTRIBUTIONS -- IGNORING INTER-CCD GAP -- ONE QUADRANT
################################################################################


# Neglecting the central dead-cross between CCDs
def equi_surface_radii_fullquadrant(cells=None):
    """
    Compute the radii of the rings making sure all cells occupy the same area
    """
    if cells is None:
        cells = [1,2,3,4]
    radius = 81.5184
    cells = np.array(cells)
    nslices = len(cells)
    ncells = np.sum(cells)
    radii = np.zeros(nslices)

    # Surface of each individual cell = surface of the quadrant / nb of cells
    unit_surface = (np.pi * radius * radius) / 4. / ncells

    # inner surface = surface of all rings 'inside' and including the current one=
    inner_surface = 0.

    for slice in range(nslices):
        slice_area = unit_surface * cells[slice]

        inner_surface += slice_area

        radii[slice] = np.sqrt(4. * inner_surface / np.pi)

    return radii


def equi_surface_coordinates_fullquadrant(cells=None, midradius=True, verbose=False):
    """

    Parameters
    ----------
    radius : TYPE
        DESCRIPTION.
    cells : TYPE, optional
        DESCRIPTION. The default is [1,2,3,4].

    midradius : used to compute the radius of the points
        midradius = True : the point is at half the thickness of the slice
                  = False : the point is at the radius where half the surface
                           of the cell is outside, and half inside. This depends
                           on the cell geometry -- not implemented

    Returns
    -------
    x,y = np.arrays of length = number of cells

    """
    if cells is None:
        cells = [1,2,3,4]
    radius = 81.5184
    cells = np.array(cells)
    nslices = len(cells)

    slice_radii = equi_surface_radii_fullquadrant(cells=cells)

    xs, ys = [], []

    inner_radius = 0.
    for slice in range(nslices):
        if midradius:
            point_radius = (slice_radii[slice] + inner_radius) / 2.
        else:
            raise Exception("midradius - False is not implemented")

        inner_radius = slice_radii[slice]
        #
        # angular span of a cell
        cell_span = np.pi / 2. / (cells[slice])

        point_angles = np.array([(cell_span / 2. + i * cell_span) for i in range(cells[slice])])
        xs.append(point_radius * np.cos(point_angles))
        ys.append(point_radius * np.sin(point_angles))

        if verbose:
            print(f"slice {slice} radius {point_radius:.3f} angles {[np.rad2deg(i) for i in point_angles]}")

    x1d = np.array([point for aslice in xs for point in aslice])
    y1d = np.array([point for aslice in ys for point in aslice])

    return x1d, y1d


def equi_surface_edges_fullquadrant(cells=None, alledges=False):
    """
    equi_surface_edges_fullquadrant(radius, cells=None, alledges=False)

    This function computes cell-edges in equi-surface distributions.
    It is only relevant for display purposes.

    alledges = False (default) : the edges at 0 & 90 degrees are not included

    """
    if cells is None:
        cells = [1,2,3,4]
    radius = 81.5184
    alledges = {False: 0, True: 1}[alledges]

    cells = np.array(cells)
    nslices = len(cells)

    outer_radii = equi_surface_radii_fullquadrant(cells=cells)

    innerxys, outerxys = [], []

    inner_radius = 0.
    for slice in range(nslices):
        outer_radius = outer_radii[slice]

        # angular span of a cell
        cell_span = np.pi / 2. / (cells[slice])

        edge_angles = np.array([(i * cell_span) for i in range(1 - alledges, 4*cells[slice] + alledges)])

        for angle in edge_angles:
            innerxys.append([inner_radius * np.cos(angle), inner_radius * np.sin(angle)])
            outerxys.append([outer_radius * np.cos(angle), outer_radius * np.sin(angle)])

        inner_radius = outer_radius

    return np.array(innerxys), np.array(outerxys)

###################################
## PORTING ONE TO ALL 4 QUADRANTS
###################################

def oneTo4quadrants(x, y, cells, boost=-1, boostFactor=1):
    """
    oneTo4quadrants(x,y, cells, boost=-1, boostFactor=1)

    Assuming x,y represent coordinates in 1 quadrant of a circle,
    we rotate them to copy them the other 3 quadrants

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    cells : description of the radial distribution of iso-surface cells

    boost: if >= 0, it points to an annulus (i.e. position in 'cells') to be boosted
           boosting means multiplying the number of field positions in that annulus, i.e. returning
           multiple field positions / cell for that specific annulus

    boostFactor if boost >= 0, boostFactor indicates how many field-positions to return / cell on the selected annulus

    Returns
    -------
    x,y: same as input, but rotated by multiples of 90 over all quadrants

    """
    xnp, ynp = np.array(x), np.array(y)

    # Propagate solution to all 4 quadrants, 1 radius at a time  ('slice' is a reserved word)
    xxx, yyy = [], []
    innerPoints = 0

    for c, torus in enumerate(cells):
        if c == boost:
            npoints = torus * boostFactor
        else:
            npoints = torus
        xslice, yslice = xnp[innerPoints:innerPoints + npoints], ynp[innerPoints:innerPoints + npoints]
        for theta in [np.pi / 2. * i for i in range(4)]:
            R = np.matrix([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
            xrot, yrot = R @ [xslice, yslice]
            xxx.extend(np.array(xrot)[0, :])
            yyy.extend(np.array(yrot)[0, :])

        innerPoints += npoints

    return np.array(xxx), np.array(yyy)

###################################
## FOV REPRESENTATION
###################################


def plotFPA(figname=None, figsize=None, **kwargs):
    import matplotlib.pyplot as plt
    # from matplotlib.patches import Rectangle

    if not 'color' in kwargs.keys(): kwargs['color'] = 'k'
    if not 'lw' in kwargs.keys(): kwargs['lw'] = 1
    if not 'fill' in kwargs.keys(): kwargs['fill'] = False

    ccdSize = 81.18  ## mm
    offset = 1.3  ## mm
    plt.figure(figname, figsize=figsize)
    # lower left
    rectll = plt.Rectangle((-ccdSize - offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(rectll)
    # top right
    recttr = plt.Rectangle((offset, offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(recttr)
    # top left
    recttl = plt.Rectangle((-ccdSize - offset, offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(recttl)
    # lower right
    rectlr = plt.Rectangle((offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(rectlr)

    plt.axis('equal')
    plt.xlim(-80, 140)
    plt.ylim(-100, 100)

    circle = plt.Circle((128, 0), radius=5, **kwargs)
    plt.gca().add_patch(circle)

    return


def plotCCDs(figname=None, figsize=(10,10), **kwargs):
    import matplotlib.pyplot as plt
    # from matplotlib.patches import Rectangle

    if not 'color' in kwargs.keys(): kwargs['color'] = 'k'
    if not 'lw' in kwargs.keys(): kwargs['lw'] = 1
    if not 'fill' in kwargs.keys(): kwargs['fill'] = False


    plt.figure(figname, figsize=figsize)


    #origin_x = origin_y = [1.3,1.3,1.3,1.3]  ## mm

    offset = 1.3
    ccdSize = 81.18  ## mm

    # CCD1 top left
    recttl = plt.Rectangle((-ccdSize - offset, offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(recttl)
    # CCD2 lower left
    rectll = plt.Rectangle((-ccdSize - offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(rectll)
    # CCD3 lower right
    rectlr = plt.Rectangle((offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(rectlr)
    # CCD4 top right
    recttr = plt.Rectangle((offset, offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(recttr)


    plt.xlim(-82, 82)
    plt.ylim(-82, 82)
    plt.axis('equal')

    plt.xlabel("X [mm]", size=14)
    plt.ylabel("Y [mm]", size=14)

    # circle = plt.Circle((128,0),radius=5,**kwargs)
    # plt.gca().add_patch(circle)

    return

def equi_surface_plot_full(radius = 81.5184, alledges=False, title="Equi-surface full quadrant",
                                   **kwargs):
    from matplotlib.patches import Circle

    cells = [1,2,3,4]
        
    radius = 81.5184

    radii = equi_surface_radii_fullquadrant()
    xxs, yys = equi_surface_coordinates_fullquadrant()
    xs, ys = oneTo4quadrants(xxs, yys, cells)

    ax = plt.subplot(111, aspect=1.)
    ax.scatter(xs, ys, c='k')
    plt.xlim(-radius, radius)
    plt.ylim(-radius, radius)

    kwargs.setdefault("linestyle", "--")
    kwargs.setdefault("linewidth", "1")

    # CIRCLES
    for r in radii:
        circle = Circle((0, 0), r, edgecolor=(0.5, 0.5, 0.5), facecolor="none", **kwargs)
        ax.add_patch(circle)

    # Outer circle
    # circle = Circle((0, 0), R, facecolor='none', edgecolor='k', linewidth=1, linestyle="-")
    # ax.add_patch(circle)

    # RADIAL EDGES
    inxys, outxys = equi_surface_edges_fullquadrant(cells=cells, alledges=alledges)


    for edge in range(len(inxys)):
        plt.plot([inxys[edge, 0], outxys[edge, 0]], [inxys[edge, 1], outxys[edge, 1]], c=(0.5, 0.5, 0.5), **kwargs)

    plt.xlabel('[mm]', size=14)
    plt.ylabel('[mm]', size=14)
    plt.title(title)

    return

def get_centroid_single_image(image):

    """ Calculate centroid of the (single) source in the given image.

    Args:
        - image: Image in which to look for a single (point) sources,
                  represented by a 2D numpy array.

    Returns:
        - row_centroid: Row coordinate of the centroid [pixels].
        - column_centroid: Column coordinate of the centroid [pixels].
    """

    row_centroid = 0
    column_centroid = 0

    weight = 0

    for row in range(image.shape[0]):

        for column in range(image.shape[1]):

            row_centroid += image[row][column] * row
            column_centroid += image[row][column] * column

            weight += image[row][column]

    row_centroid /= weight
    column_centroid /= weight

    return row_centroid, column_centroid


def get_brightest_pixel_coordinate(image):

    """ Calculate centroid of the (single) source in the given image.

    Args:
        - image: Image in which to look for a single (point) sources,
                  represented by a 2D numpy array.

    Returns:
        - row_centroid: Row coordinate of the centroid [pixels].
        - column_centroid: Column coordinate of the centroid [pixels].
    """

    row_centroid = 0
    column_centroid = 0
    max5 = 0

    for row in range(image.shape[0]-5):
        for column in range(image.shape[1]-5):
            
            cropped_image = image[row:row+5, column:column+5]
            five_square = np.sum(cropped_image)
            
            if five_square > max5:
                 row_centroid = row + 3
                 column_centroid = column + 3
                 max5 = five_square
                 
    #print(np.size(cropped_image))
    return row_centroid, column_centroid