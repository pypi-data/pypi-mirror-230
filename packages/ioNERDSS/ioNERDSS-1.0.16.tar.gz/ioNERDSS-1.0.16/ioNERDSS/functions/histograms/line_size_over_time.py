import numpy as np
import matplotlib.pyplot as plt
from ..file_managment.save_vars_to_file import save_vars_to_file


def line_size_over_time(Data: int, full_hist: list, FileNum: int, InitialTime: float, FinalTime: float,
                 SpeciesName: str = "tot", ExcludeSize: int = 0, SpeciesList: list = ["na"], ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """Creates a graph counting the number of protein species in a complex molecule over a time period.
        Can either be average count or the max count of that protein species at that time stamp .

    Args:
        Data (int): what will the graph show (1: mean, 2: max)
        full_hist (list): holds all of that data in the histogram.dat file
        FileNum (int): Number of the total input files (file names should be [fileName]_1,[fileName]_2,...)
        InitialTime (float): The starting time. Must not be smaller / larger then times in file.
        FinalTime (float): The ending time. Must not be smaller / larger then times in file.
        SpeciesName (str): The name of the species you want to examine. Should be in the .dat file.
        ExcludeSize (int): Monomers in the complex that are smaller or equal to this number will not be included. 
        SpeciesList (lst, optional): lists all of the species in the doc. Only needed for multi species hists.
        ShowFig (bool, optional): If the plot is shown. Defaults to True.
        SaveFig (bool, optional): If the plot is saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        graph. X-axis = time. Y-axis = mean number of species in a single complex molecule.
    """
    
    time_list = [] #list of every timestamp
    size_list = [] #list of mean sizes (index of this = index of timestep)
    max_size = 0 #the longest histogram
    max_index = 0 #the index of the longest histogram
    count = 0 #used to find number of species in a complex

    #write name of the plot / y label (if applicable)
    if Data == 1:
        graphTitle = 'Average Number of ' + str(SpeciesName) + ' in Single Complex'
        yLabel = 'Average Number of ' + str(SpeciesName)
    elif Data == 2:
        graphTitle = 'Maximum Number of ' + str(SpeciesName) + ' in Single Complex'
        yLabel = 'Maximum Number of ' + str(SpeciesName)
    else:
        raise Exception("Invalid data type")


    for index,hist in enumerate(full_hist):

        total_size_list = [] #list of every timestamp for this file
        total_time_list = [] #list of mean sizes (index of this = index of timestep)

        #create list of means / timesteps, based on what sizes are excluded/not
        if ExcludeSize >= 0:
            for timestep in hist:
                if InitialTime <= timestep[0] <= FinalTime:
                    total_time_list.append(timestep[0])
                    
                    #create a list of each complex size at this timestamp
                    if SpeciesList != ['na']:
                        timestep_edited = []
                        
                        #if all species are included or just 1 (for multi)
                        if SpeciesName != "tot":
                            ind = SpeciesList.index(SpeciesName)
                            for complex in timestep[1:]:
                                timestep_edited.append(complex[ind])
                        else:
                            for complex in timestep[1:]:
                                count = 0
                                for species in complex[:-1]:
                                    count += species
                                timestep_edited.append(count)
                    else:
                        timestep_edited = timestep[2]
        
                    if ExcludeSize > 0:
                        timestep_edited = [ele for ele in timestep_edited if ele>ExcludeSize] #create new list that only includes elements greater then exclude size
                        if timestep_edited == []: timestep_edited.append(0)

                    if Data == 1: #if it is a mean / max line graph
                        total_size_list.append(np.mean(timestep_edited))
                    else:
                        total_size_list.append(np.max(timestep_edited))
        
            #determine size of hist
            if len(total_size_list) > max_size:
                max_size = len(total_size_list)
                max_index = index


        else:
            print('ExcludeSize cannot smaller than 0!')
            return 0
        
        #add time/size lists to main, cross function lists
        time_list.append(total_time_list)
        size_list.append(total_size_list)

    #ensure all lists are tranposible (have equal shape)
    for index_file,file_size in enumerate(size_list):
        if len(file_size) != max_size:
            zero_list = np.zeros(max_size)
            for index_size,size in enumerate(file_size):
                zero_list[index_size] =+ size
            size_list[index_file] = zero_list


    #transpose list (each sub-list = 1 timesteps across every file)
    size_list_rev = []
    size_list_rev = np.transpose(size_list)

    #find mean and std dev
    mean = []
    std = []

    for index,timestamps in enumerate(size_list_rev):
        
        #if this timestamp is equal to previous, copy previous. 
        if (timestamps == size_list_rev[index-1]).all():
            mean.append(mean[index-1])
            if FileNum > 1: std.append(std[index-1])
        
        #Else calculate new measns/stds
        else:
            mean.append(np.nanmean(timestamps))
            if FileNum > 1: std.append(np.nanstd(timestamps))
    
    #output variables
    if SaveVars:
        if Data == 1:
            save_vars_to_file({"time_stamp":time_list[0],"mean_cmplx_size":mean,"std":std})
        if Data == 2:
            save_vars_to_file({"time_stamp":time_list[0],"max_cmplx_size":mean,"std":std})

    #show figure
    if ShowFig:
        errorbar_color = '#c9e3f6'
        plt.plot(time_list[max_index], mean, color='C0')
        if FileNum > 1:
            plt.errorbar(time_list[max_index], mean, color='C0',
                         yerr=std, ecolor=errorbar_color)
        plt.title(graphTitle)
        plt.xlabel('Time (s)')
        plt.ylabel(yLabel)
        if SaveFig:
            plt.savefig('mean_complex.png', dpi=500)
        plt.show()
    return time_list[0], mean, std


