

#probably broken because of changes to other things. I added in the old functions under 'fake' to try and get it working again


import pandas as pd



def fake_PDB_pdb_to_df(file_name, drop_COM):
    df = pd.DataFrame(columns=['Protein_Num', 'Protein_Name',
                      'Cite_Name', 'x_coord', 'y_coord', 'z_coord'])
    with open(file_name, 'r') as file:
        index = 0
        for line in file.readlines():
            line = line.split(' ')
            if line[0] == 'ATOM':
                info = []
                for i in line:
                    if i != '':
                        info.append(i)
                df.loc[index, 'Protein_Num'] = int(info[4])
                df.loc[index, 'Protein_Name'] = info[3]
                df.loc[index, 'Cite_Name'] = info[2]
                df.loc[index, 'x_coord'] = float(info[5])
                df.loc[index, 'y_coord'] = float(info[6])
                df.loc[index, 'z_coord'] = float(info[7])
            index += 1
        df = df.dropna()
        if drop_COM:
            df = df.drop(index=df[(df.Cite_Name == 'COM')].index.tolist())
        df = df.reset_index(drop=True)
    return df


def fake_RESTART_read_restart(file_name_restart):
    with open(file_name_restart, 'r') as file:
        status = False
        count = 0
        complex_lst = []
        for line in file.readlines():
            if line == '#All Complexes and their components \n':
                status = True
            if status:
                if count % 8 == 7:
                    info = line.split()
                    temp_lst = []
                    for i in range(len(info)):
                        if i != 0:
                            temp_lst.append(int(info[i]))
                    complex_lst.append(temp_lst)
                count += 1
            if line == '#Observables \n':
                break
    print('The total number of complexes is', len(complex_lst))
    return complex_lst

def single_restart_to_df(FileNamePdb, ComplexSizeList, FileNameRestart='restart.dat', SerialNum=0):
    """
    Returns a pandas dataframe of protein complex structure data and an updated serial number based on the input parameters.

    Args:
        FileNamePdb (str): file path of the PDB file containing protein complex structure data
        ComplexSizeList (list[int]): a list of integers specifying desired sizes of protein complexes
        FileNameRestart (str): file path of RESTART file containing the protein complex's restart data (default is 'restart.dat')
        SerialNum (int): the starting index of the desired protein complex in the restart file (default is 0)

    Returns:
        tuple: A tuple containing a pandas dataframe of the desired protein complex structure data and an updated serial number. If the desired size is not found, (0,-1) will be returned.
    """
    if SerialNum == -1:
        return 0, -1
    complex_list = fake_RESTART_read_restart(FileNameRestart)
    index = 0
    protein_remain = []
    for i in range(len(ComplexSizeList)):
        for j in range(len(complex_list)):
            if len(complex_list[j]) == ComplexSizeList[i]:
                index += 1
                if SerialNum == index-1:
                    protein_remain = complex_list[j]
                    SerialNum += 1
                    complex_pdb_df = fake_PDB_pdb_to_df(FileNamePdb, False)
                    complex_pdb_df = complex_pdb_df[complex_pdb_df['Cite_Name'] == 'COM']
                    complex_pdb_df = complex_pdb_df[complex_pdb_df['Protein_Num'].isin(
                        protein_remain)]
                    if 0 in complex_pdb_df.index:
                        complex_pdb_df = complex_pdb_df.drop(0)
                    return complex_pdb_df, SerialNum
    print('Cannot find more desired size of comolex!')
    return 0, -1
