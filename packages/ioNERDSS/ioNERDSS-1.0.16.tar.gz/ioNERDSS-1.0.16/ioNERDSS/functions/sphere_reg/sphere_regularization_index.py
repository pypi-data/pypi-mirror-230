
#probably broken because of changes to other things. I added in the old functions under 'fake' to try and get it working again

import numpy as np
import warnings
import matplotlib as plt
from .fitSphere import fitSphere
from .single_restart_to_df import single_restart_to_df

def fake_read_file(FileName: str, SpeciesName: str):
    hist = []
    hist_temp = []
    hist_conv = []
    hist_count = []
    with open(FileName, 'r') as file:
        for line in file.readlines():
            if line[0:4] == 'Time':
                if hist_count != [] and hist_conv != []:
                    hist_temp.append(hist_count)
                    hist_temp.append(hist_conv)
                    hist.append(hist_temp)
                hist_count = []
                hist_conv = []
                hist_temp = []
                hist_temp.append(float(line.strip('Time (s): ')))
            else:
                string = '	' + str(SpeciesName) + ': '
                line = line.strip('. \n').split(string)
                if len(line) != 2:
                    print('Wrong species name!')
                    return 0
                else:
                    hist_count.append(int(line[0]))
                    hist_conv.append(int(line[1]))
            if len(hist_temp) == 0:
                hist_temp.append(hist_count)
                hist_temp.append(hist_conv)
                hist.append(hist_temp)
    hist_temp.append(hist_count)
    hist_temp.append(hist_conv)
    hist.append(hist_temp)
    return hist


def fake_hist(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str,
         BarSize: int = 1, ShowFig: bool = True, SaveFig: bool = False):
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    count_list = []
    size_list = []
    for k in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(k) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = FileName
        total_size_list = []
        total_count_list = []
        hist = fake_read_file(temp_file_name, SpeciesName)
        data_count = 0
        for i in hist:
            if InitialTime <= i[0] <= FinalTime:
                data_count += 1
                for j in i[2]:
                    if j not in total_size_list:
                        total_size_list.append(j)
                        total_count_list.append(i[1][i[2].index(j)])
                    else:
                        index = total_size_list.index(j)
                        total_count_list[index] += i[1][i[2].index(j)]
        total_count_list = np.array(total_count_list)/data_count
        if len(total_size_list) != 0:
            total_size_list_sorted = np.arange(1, max(total_size_list)+1, 1)
        else:
            total_size_list_sorted = np.array([])
        total_count_list_sorted = []
        for i in total_size_list_sorted:
            if i in total_size_list:
                index = total_size_list.index(i)
                total_count_list_sorted.append(total_count_list[index])
            else:
                total_count_list_sorted.append(0.0)
        size_list.append(total_size_list_sorted)
        count_list.append(total_count_list_sorted)
    max_size = 0
    for i in size_list:
        if max_size < len(i):
            max_size = len(i)
            n_list = i
    count_list_filled = np.zeros([FileNum, max_size])
    for i in range(len(count_list)):
        for j in range(len(count_list[i])):
            count_list_filled[i][j] += count_list[i][j]
    count_list_rev = []
    for i in range(len(count_list_filled[0])):
        temp = []
        for j in range(len(count_list_filled)):
            temp.append(count_list_filled[j][i])
        count_list_rev.append(temp)
    mean = []
    std = []
    for i in count_list_rev:
        mean.append(np.nanmean(i))
        std.append(np.nanstd(i))
    mean_ = []
    std_ = []
    n_list_ = []
    temp_mean = 0
    temp_std = 0
    bar_size_count = 0
    for i in range(len(mean)):
        temp_mean += mean[i]
        temp_std += std[i]
        bar_size_count += 1
        if i+1 == len(mean):
            mean_.append(temp_mean)
            std_.append(temp_std)
            n_list_.append(n_list[i])
        elif bar_size_count >= BarSize:
            mean_.append(temp_mean)
            std_.append(temp_std)
            n_list_.append(n_list[i])
            temp_mean = 0
            temp_std = 0
            bar_size_count = 0
    mean_ = np.array(mean_)
    std_ = np.array(std_)
    n_list_ = np.array(n_list_)
    if ShowFig:
        if FileNum != 1:
            plt.bar(n_list_, mean_, width=BarSize, color='C0',
                    yerr=std_, ecolor='C1', capsize=2)
        else:
            plt.bar(n_list_, mean_, width=BarSize)
        plt.title('Histogram of ' + str(SpeciesName))
        plt.xlabel('Number of ' + SpeciesName + ' in sigle complex')
        plt.ylabel('Count')
        if SaveFig:
            plt.savefig('Histogram.png', dpi=500)
        plt.show()
    return n_list_, mean_, 'Nan', std_


def sphere_regularization_index(FileNameHist: str, SpeciesName: str, LitNum: int, TimeStep: float,
                                ComplexNum: int, Radius: float):
    """This function calculates the regularization index of the given parameters.
    Note: This was made with chatgpt and may be wrong

    Parameters:
        FileNameHist: A string representing the file name of the histogram
        SpeciesName: A string representing the species name
        LitNum: An integer representing the number of the litter
        TimeStep: A float representing the time step
        ComplexNum: An integer representing the number of complexes
        Radius: A float representing the radius
    
    Returns:
        max_complex_size_return: A list of integers representing the maximum complex size
        theta_ideal_return: A list of floats representing the ideal spherical angle
        sphere_radius_return: A list of floats representing the sphere radius
        sphere_center_position_return: A list of floats representing the sphere center position
        complex_COM_return: A list of floats representing the complex center of mass
        regularization_index_return: A list of floats representing the regularization index
    
    This function calculates the regularization index of the given parameters. It firsts get the data from the histogram and then calculates the maximum complex size. It then fits 3 spheres and does a sanity check. It then calculates the center of mass of the max complex and determines the spherical angle corresponding to the ideal complex with surface area. It then determines if the monomer on complex is on the ideal cap and returns the regularization index.
    """
    warnings.simplefilter("ignore")
    t = TimeStep * LitNum
    data = fake_hist(FileName=FileNameHist,
                FileNum=1, InitialTime=t, FinalTime=t+TimeStep,
                SpeciesName=SpeciesName, ShowFig=False)
    x_data = data[0]
    y_data = data[1]
    size_list = []
    i = len(x_data)-1
    while i >= 0:
        if y_data[i] != 0:
            size_list.append(x_data[i])
        i -= 1

    max_complex_size_return = []
    theta_ideal_return = []
    sphere_radius_return = []
    sphere_center_position_return = []
    complex_COM_return = []
    regularization_index_return = []

    SerialNum = 0
    protein_remain = []
    for m in range(ComplexNum):
        pdb_file_name = str(LitNum)+'.pdb'
        restart_file_name = 'restart'+str(LitNum)+'.dat'
        complex_pdb_df, SerialNum = single_restart_to_df(FileNamePdb=pdb_file_name,
                                                         ComplexSizeList=size_list,
                                                         FileNameRestart=restart_file_name,
                                                         SerialNum=SerialNum)

        max_complex_size = len(complex_pdb_df)
        sphere_center_position_candidate = np.zeros((3, 3))
        sphere_radius_candidate = np.zeros((3, 1))

        # Shuffle the dataframe
        complex_pdb_df = complex_pdb_df.sample(frac=1)

        # if the COM number is gearter than 30, then split the COM list into 3 parts and fit 3 spheres
        # if the differences of sphere center coordinates are smaller than 0.1
        # and the |fiited radius - 50| < 0.1 , we consider the fitting as good
        x_list = np.array(complex_pdb_df['x_coord'])
        y_list = np.array(complex_pdb_df['y_coord'])
        z_list = np.array(complex_pdb_df['z_coord'])

        partition = [[0, int(len(x_list)/3)], [int(len(x_list)/3),
                                               int(len(x_list)/3*2)], [int(len(x_list)/3*2), -1]]

        for ind, part in enumerate(partition):
            r, cx, cy, cz = fitSphere(np.array(complex_pdb_df['x_coord'][part[0]:part[1]]),
                                      np.array(
                                          complex_pdb_df['y_coord'][part[0]:part[1]]),
                                      np.array(complex_pdb_df['z_coord'][part[0]:part[1]]))
            sphere_center_position_candidate[ind, :] = [cx, cy, cz]
            sphere_radius_candidate[ind, :] = r

        # sanity check
        if sum(abs(np.array(sphere_radius_candidate) - r)) >= 0.1 * 3:
            print("Caution, the radius error is > 0.1! The fitted radii are: \n",
                  sphere_radius_candidate)

        # check sphere center coordinate error
        count = 0
        for i in range(3):
            if abs(sphere_center_position_candidate[0][i] - sphere_center_position_candidate[1][i]) >= 0.1 \
                    and abs(sphere_center_position_candidate[1][i] - sphere_center_position_candidate[2][i]) >= 0.1 \
                    and abs(sphere_center_position_candidate[0][i] - sphere_center_position_candidate[2][i]) >= 0.1:
                count += 1
        if count > 0:
            print("Caution, the center coordinate error is > 0.1! The fitted coordinates are: \n",
                  sphere_center_position_candidate)

        sphere_center_position = np.mean(sphere_center_position_candidate, 0)
        sphere_radius = np.mean(sphere_radius_candidate)

        # calculate the center of mass of the max complex
        complex_COM = np.mean(
            complex_pdb_df[['x_coord', 'y_coord', 'z_coord']])
        # directional vector that directs from sphere center to complex COM
        dir_vector = complex_COM - sphere_center_position

        # the surface area of a Gag compelx is
        S_whole_sphere = 4*np.pi*50**2  # nm^2
        S_per_Gag = S_whole_sphere/3697  # nm^2
        S_max_complex = S_per_Gag*max_complex_size  # nm^2

        # determine the spherical angle corresponding to the ideal complex with surface area S_max_complex
        # A = 2*pi*r^2*(1-cos(theta))
        # max polar angle possible
        theta_ideal = np.arccos(1-S_max_complex/2/np.pi/sphere_radius**2)

        # determine if the monomer on complex is on the ideal cap
        counter = 0
        inside_sphere_cap = []
        outside_sphere_cap = []
        for i in range(max_complex_size):
            monomer_vector = list(
                complex_pdb_df.iloc[i][['x_coord', 'y_coord', 'z_coord']])-sphere_center_position
            monomer_theta = np.arccos(float(np.dot(monomer_vector, dir_vector)/np.linalg.norm(
                monomer_vector.astype(float))/np.linalg.norm(dir_vector.astype(float))))
            if monomer_theta <= theta_ideal:
                counter += 1
                inside_sphere_cap.append(
                    list(complex_pdb_df.iloc[i][['x_coord', 'y_coord', 'z_coord']]))
            else:
                outside_sphere_cap.append(
                    list(complex_pdb_df.iloc[i][['x_coord', 'y_coord', 'z_coord']]))
        regularization_index = counter/max_complex_size

        max_complex_size_return.append(max_complex_size)
        theta_ideal_return.append(theta_ideal)
        sphere_radius_return.append(sphere_radius)
        sphere_center_position_return.append(sphere_center_position)
        complex_COM_return.append(list(complex_COM))
        regularization_index_return.append(regularization_index)

        print("Complex Size: %f \nTheta of the sphere cap: %f \nR of the fitted circle: %f " % (
            max_complex_size, theta_ideal, sphere_radius))
        print('Sphere center coord: ', sphere_center_position)
        print('Sphere cap COM: ', list(complex_COM))
        print("Regularixation index: ", regularization_index)
        if m != ComplexNum-1:
            print(
                '------------------------------------------------------------------------------')
        else:
            print(
                '------------------------------------End---------------------------------------')

    return max_complex_size_return, theta_ideal_return, sphere_radius_return, sphere_center_position_return, complex_COM_return, regularization_index_return