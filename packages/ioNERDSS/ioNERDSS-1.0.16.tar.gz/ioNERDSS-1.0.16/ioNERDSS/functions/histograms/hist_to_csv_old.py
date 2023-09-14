import numpy as np


def hist_to_csv_old(FullHist: list, SpeciesList: list, OpName: str):
    """WARNING: THIS FUNCTION CURRENTLY HAS TO BE GIVEN FILES OF THE SAME SIZE OR ELSE IT WILL BREAK. (if given multiple)
    Creates a .csv (spreadsheet) file from a histogram.dat file (multi-species)

    Args:
        FullHist (list): holds all of the histogram data
        OpName (str): name of the outputted .csv file

    Returns:
        histogram.csv file: Each row is a different time stamp (all times listed in column A). Each column is a different size of complex molecule (all sizes listed in row 1). Each box 
        is the number of that complex molecule at that time stamp.
    
    """
    
    column_list = [] #holds the name of each column (Time + each complex name)
    time_list = [] #holds each time. Index corresponds to a sublist in name_count_dict_List
    name_count_dict_list = [] #holds each name/count. Index corresponds with size_list

    #determine longest file
    length = 0
    for file_index,file in enumerate(FullHist):
        if len(file) > length:
            length = len(file)
            length_index = file_index 
    

    #create list with dictionaries for each timestep
    for na in range(0,length+1):
        name_count_dict_list.append({})


    #Creates list with every complex type/size
    for file_index,file in enumerate(FullHist):
        
        for time_index,time in enumerate(file):

            #get timestamps
            if time[0] not in time_list:
                time_list.append(time[0])

            #get complex names and counts
            for complex_index,complexes in enumerate(time[1:]):
                
                #get name
                name = ""
                for index_sp,species in enumerate(complexes[:-1]):
                    name = f"{name}{SpeciesList[index_sp]}: {species}.  "
                    if name not in name_count_dict_list[time_index].keys():
                        name_count_dict_list[time_index][name] = []
                        
                #get count
                name_count_dict_list[time_index][name].append(complexes[-1])

                #creates a list of every 'name'
                if name not in column_list:
                    column_list.append(name)

    #takes mean of each complex type at each timestep
    for time_index,time in enumerate(name_count_dict_list):
        for key in time.keys():
            
            #will add 0s to a list if it does not have data from each file.
            if len(time[key]) < len(FullHist):
                for na in range(len(time[key]), len(FullHist)):
                    time[key].append(0)

            #takes mean of list
            name_count_dict_list[time_index][key] = np.round(np.mean(time[key]),5)
            



    #write the file!
    with open(f'{OpName}.csv', 'w') as write_file:
        
        #create column names
        head = 'Time(s):'
        for column in column_list:
            head += ','
            head += column
        head += '\n'
        write_file.write(head)

        #write the bulk of the file
        for index,timestep in enumerate(time_list):
            
            #initilize writing
            write = ''

            #write time to string
            write += f"{str(timestep)}"

            #write data to string
            for column in column_list:
                write += ','
                if column in name_count_dict_list[index].keys():
                    write += str(name_count_dict_list[index][column])
                else:
                    write += '0'
            
            #commit to file
            write += '\n'
            write_file.write(write)



