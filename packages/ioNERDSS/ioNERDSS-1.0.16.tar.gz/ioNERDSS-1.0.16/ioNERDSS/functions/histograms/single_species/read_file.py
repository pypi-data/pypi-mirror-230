def read_file(FileName: str, SpeciesName: str):
    """Will take in a histogram.dat (single-species) and turn it into a list of lists

    Args:
        FileName (str): Path to the histogram.dat file
        SpeciesName (str): The name of the specific species you want to examine. Should be in the .dat file.

    Returns:
        list of lists: Has many lists, where each sub-list is a new time stamp that includes time at list[i][0]. You can find list 
        of number of each complex type in list[i][1]. List of the number of species count in complex in list[i][2].
    """
    
    #general vars 
    hist = [] # main list that holds each timestamp
    hist_temp = [] # holds all info in 1 timestamp.
    hist_conv = [] # number of species in this complex type at 1 timestamp
    hist_count = [] # num of this complex type at 1 timestamp
    
    #eads through the file
    with open(FileName, 'r') as file:
        for line in file.readlines():
            
            #determining what the line holds
            if line[0:4] == 'Time':
                
                #if this is NOT the first run, add the temp lists to the main list
                if hist_count != [] and hist_conv != []:
                    hist_temp.append(hist_count)
                    hist_temp.append(hist_conv)
                    hist.append(hist_temp)
                
                #reset the temp lists
                hist_count = []
                hist_conv = []
                hist_temp = []

                #set time to start of new temp list
                hist_temp.append(float(line.strip('Time (s): ')))
            
            #if the line holds species information
            else:

                #split the line and determine if it has the right species name
                string = '	' + str(SpeciesName) + ': '
                line = line.strip('. \n').split(string)
                if len(line) != 2:
                    raise Exception('invalid species name')
                
                #adds values to the sub - temp list
                else:
                    hist_count.append(int(line[0]))
                    hist_conv.append(int(line[1]))
    
    #if it is the last run, add it in (needs to be here b/c temps are added at start of new time, not end of previous time)
    hist_temp.append(hist_count)
    hist_temp.append(hist_conv)
    hist.append(hist_temp)
    
    return hist


