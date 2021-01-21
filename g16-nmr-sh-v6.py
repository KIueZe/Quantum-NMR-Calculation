#####################################################################
#                                                                   #
#                     ZJS @ Jan/08th/2021                           #
#                                                                   #
#                excecute the main sh: sh *.sh                      #
#                                                                   #
#        change "NPROC" attribute to change core numbers            #
#                                                                   #
#                                                                   #
#  This python script is intended to be run from the Maestro        #
#  Command Input Area.                                              #
#                                                                   #
#  While in the command input area enter:                           #
#            pythonimport "title of this script"                    #
#                                                                   #
#  If you can't see the command input area then open Maestro,       #
#  select "Window" and check the box to the left of                 #
#  "Command Input Area"                                             #
#                                                                   #
#####################################################################



from __future__ import print_function
from schrodinger import maestro
from schrodinger import structure
from schrodinger import project
import os
from math import exp as exp

def main ():
#  Dictionary holding column names for project table properties depending on the force field being used
    columns = {'mm2' : ['r_mmod_Potential_Energy-MM2*', 'r_mmod_Relative_Potential_Energy-MM2*'], 
    'mm3': ['r_mmod_Potential_Energy-MM3*', 'r_mmod_Relative_Potential_Energy-MM3*'], 
    'amber': ['r_mmod_Potential_Energy-AMBER*', 'r_mmod_Relative_Potential_Energy-AMBER*'], 
    'opls': ['r_mmod_Potential_Energy-OPLSA*', 'r_mmod_Relative_Potential_Energy-OPLSA*'], 
    'amber94': ['r_mmod_Potential_Energy-AMBER94', 'r_mmod_Relative_Potential_Energy-AMBER94'], 
    'mmff': ['r_mmod_Potential_Energy-MMFF94', 'r_mmod_Relative_Potential_Energy-MMFF94'], 
    'mmffs': ['r_mmod_Potential_Energy-MMFF94s', 'r_mmod_Relative_Potential_Energy-MMFF94s'], 
    'opls2001': ['r_mmod_Potential_Energy-OPLS-AA', 'r_mmod_Relative_Potential_Energy-OPLS-AA'], 
    'opls2005': ['r_mmod_Potential_Energy-OPLS-2005', 'r_mmod_Relative_Potential_Energy-OPLS-2005'], 
    'opls3': ['r_mmod_Potential_Energy-OPLS3', 'r_mmod_Relative_Potential_Energy-OPLS3'], 
    'opls3e': ['r_mmod_Potential_Energy-OPLS3e', 'r_mmod_Relative_Potential_Energy-OPLS3e']}

#  Start by selecting all entries in the project table, and making sure the first entry is in the workspace
    maestro.command("eplayergotofirst")

#  Grab the entire project table
    pt = maestro.project_table_get()
    
    currentforcefield = ''
    for forcefield in list(columns):
        if not pt[1][columns[forcefield][0]] == None :
            currentforcefield = forcefield
            break

#  Create a directory to store the input files.
    os.popen( "mkdir " + str( pt[1]['s_m_title']+'-gaussian_files' ) )

    optsh_outputfile = str(pt[1]['s_m_title'])+'-opt_freq'
    nmrsh_outputfile = str(pt[1]['s_m_title'])+'-nmr'

    opt_lst = []
    nmr_lst = []
    
#  Create a dictionary with keys being each conformer name and a list of the
#  absolute and relative MM energies for the conformer.
    energies = {}
   
#  Make a loop to operate on every conformation in the project table.
#  This loop operates on one conformation.
    for row in pt.selected_rows:
        structure = maestro.workspace_get()
        conf_num = str(row).split(' ')[-1]       
        
#  Open the output file for writing
        outputfile = open( row['s_m_title'] + "-opt_freq-conf-" + conf_num + ".com", 'w' )
        nmr_outputfile = open( row['s_m_title'] + "-nmr-conf-" + conf_num + '.com', 'w' )

        opt_lst.append('g16 ' + row['s_m_title'] + "-opt_freq-conf-" + conf_num + ".com")
        nmr_lst.append('g16 ' + row['s_m_title'] + "-nmr-conf-" + conf_num + ".com")
        
#  Add the conformer energy to the dictionary of energies
        energies[ str( row['s_m_title'] + row['s_m_entry_id'] ) ] =[ row[columns[currentforcefield][0]], row[columns[currentforcefield][1]] ]
        
#  Write the Gaussian stuff that goes into every input deck.
        print(gaussian_input( "link", str( pt[1]['s_m_title']),  str( conf_num )), file=outputfile) 
        print(gaussian_nmr_input( "link", str( pt[1]['s_m_title']),  str( conf_num ) ), file=nmr_outputfile) 
        print(gaussian_input( "route" ), file=outputfile)
        print(gaussian_nmr_input( "route" ), file=nmr_outputfile)
        print(gaussian_input( "title", str( pt[1]['s_m_title']),  str( conf_num )), file=outputfile)
        print(gaussian_nmr_input( "title", str( pt[1]['s_m_title']),  str( conf_num )), file=nmr_outputfile)
        print(gaussian_input( "molecule" ), file=outputfile)
        print(gaussian_nmr_input( "molecule" ), file=nmr_outputfile)
        print(gaussian_nmr_input( "readline" ), file=nmr_outputfile)
        print(gaussian_nmr_input( "end" ), file=nmr_outputfile)

#  This loop operates on one atom.
        for atom in structure.atom:
            outputstring = "%2s %10.6f %10.6f %10.6f" % (atom.element, atom.x, atom.y, atom.z)
            print(outputstring, file=outputfile)

        print(gaussian_input( "readline" ), file=outputfile)
        print(gaussian_input("end"), file=outputfile)
        
#  Close the opened output file.

        outputfile.flush()
        outputfile.close()
        nmr_outputfile.flush()
        nmr_outputfile.close()
        maestro.command("eplayerstepahead")

    ######## to write_to
    write_optsh(opt_lst, optsh_outputfile)
    write_nmrsh(nmr_lst, nmrsh_outputfile)

    # print('top',file=optsh_outputfile)
    # print('top',file=nmrsh_outputfile)
    
    # optsh_outputfile.flush()
    # optsh_outputfile.close()
    # nmrsh_outputfile.flush()
    # nmrsh_outputfile.close()

#  Move the created input files "-gaussian_files" directory.
    os.popen( "mv " + str(pt[1]['s_m_title'] + '*conf* ') + str(pt[1]['s_m_title']+'-gaussian_files'))
    os.popen( "mv " + str(pt[1]['s_m_title']+'*.sh ') + str(pt[1]['s_m_title']+'-gaussian_files'))
        
def convert_mmat_symbol(mmat):
#    mmat2Number = {1:'C',2:'C',3:'C',15:'O',16:'O',24:'N',25:'N',26:'N',41:'H',42:'H',43:'H',49:'S',56:'F',57:'Cl',58:'Br',59:'I'}
#    symbol = mmat2Number[mmat]
#    return symbol
    return {1:'C',2:'C',3:'C',15:'O',16:'O',24:'N',25:'N',26:'N',41:'H',42:'H',43:'H',49:'S',56:'F',57:'Cl',58:'Br',59:'I'}[mmat]

def gaussian_input(which_section,candidate_filename="X", conformer_number="Y"):

    NPROC     = 8  # 4,8,16 are recommended
    ENDLINE   = "\n"
    LINK1     = "%mem={}gb\n".format(2 * NPROC)
    LINK2     = "%nproc={}\n".format(NPROC)
    LINK3     = "%%chk=%s \n" % (candidate_filename +'-conf-' + conformer_number + ".chk")
    LINK4     = "\nradii=UA0\n"
    ROUTE1    = "# b3lyp/6-31G(d) opt freq=noraman em=gd3bj integral(ultrafinegrid) scrf=(iefpcm,read,solvent=chloroform)"
    TITLE1    = "Candidate Structure: %s, Conformer: %s geometry optimization and frequency calculation with chloroform solvation" % (candidate_filename,conformer_number)
    MOL1      = "0 1"
    
    LINKZERO = LINK1 + LINK2 + LINK3
    ROUTE    = ROUTE1 + ENDLINE
    TITLE    = TITLE1 + ENDLINE
    MOLECULE = MOL1 
    READLINE = LINK4 +ENDLINE
    END      = ENDLINE
    
    if (which_section == "link"): return LINKZERO
    if (which_section == "route"): return ROUTE
    if (which_section == "title"): return TITLE
    if (which_section == "molecule"): return MOLECULE
    if (which_section == "readline"): return READLINE
    if (which_section == "end"): return END
    if (which_section == "NPROC"): return NPROC

    return "There is a problem generating the input files."
    
def gaussian_nmr_input(which_section,candidate_filename="X",conformer_number="Y"):

    NPROC     = 8  # 4,8,16 are recommended
    ENDLINE   = "\n"
    LINK1     = "%mem={}gb\n".format(2 * NPROC)
    LINK2     = "%nproc={}\n".format(NPROC)
    LINK3     = "%%chk=%s \n" % (candidate_filename + '-conf-' + conformer_number + '.chk')
    LINK4     = "radii=bondi\n"
    ROUTE1    = "# mPW1PW91/6-31+G(d,p) nmr guess=read geom=check integral(ultrafinegrid) scrf=(iefpcm,read,solvent=chloroform)"
    TITLE1    = "Candidate Structure: %s, Conformer: %s, nmr calculation with chloroform solvation" % (candidate_filename,conformer_number)
    MOL1      = "0 1"
    
    LINKZERO = LINK1 + LINK2 + LINK3
    ROUTE    = ROUTE1 + ENDLINE
    TITLE    = TITLE1 + ENDLINE
    MOLECULE = MOL1 + ENDLINE
    READLINE = LINK4 + ENDLINE
    END      = ENDLINE

    if (which_section == "link"): return LINKZERO
    if (which_section == "route"): return ROUTE
    if (which_section == "title"): return TITLE
    if (which_section == "molecule"): return MOLECULE
    if (which_section == "readline"): return READLINE
    if (which_section == "end"): return END
    if (which_section == "NPROC"): return NPROC

    return "There is a problem generating the input files."

def write_optsh(lst, file_to_write_to):
    
    nthread = int(64//gaussian_input("NPROC"))
    i = 0
    opt_shlst = [str(file_to_write_to) + str('-') + str(m) + str('.sh') for m in range(1,65)]
    shcaller = str(file_to_write_to) + str('.sh')
    write_to_shcaller = ''

    while i < len(lst):
        temp = ''
        for j in range(nthread):
            if i + j < len(lst):
                temp += lst[i+j] + '&\n'
        temp = temp[0:-2] + ';\n'
        with open(opt_shlst[int(i//nthread)], 'w') as tempfile:
            print('#!/bin/sh\n',file=tempfile)
            print('''echo "{} Group {} is running. Please wait and do not add in new missions!";\n'''.format(file_to_write_to, int(i//nthread + 1)), file=tempfile)
            print(temp, file=tempfile)
            print('''echo "{} Group {} is finished.";\n'''.format(file_to_write_to, int(i//nthread + 1)), file=tempfile)
            print('exit 0', file=tempfile)
        
        write_to_shcaller += str('sh ' + opt_shlst[int(i//nthread)] + ' && ')

        i += nthread

    write_to_shcaller = write_to_shcaller[0:-4]
    with open(shcaller, 'w') as sh:
        print('#!/bin/sh\n', file=sh)
        print(write_to_shcaller, file=sh)

def write_nmrsh(lst, file_to_write_to):
    
    nthread = int(64//gaussian_nmr_input("NPROC"))
    i = 0
    nmr_shlst = [str(file_to_write_to) + str('-') + str(m) + str('.sh') for m in range(1,65)]
    shcaller = str(file_to_write_to) + str('.sh')
    write_to_shcaller = ''

    while i < len(lst):
        temp = ''
        for j in range(nthread):
            if i + j < len(lst):
                temp += lst[i+j] + '&\n'
        temp = temp[0:-2] + ';\n'
        with open(nmr_shlst[int(i//nthread)], 'w') as tempfile:
            print('#!/bin/sh\n',file=tempfile)
            print('''echo "{} Group {} is running. Please wait and do not add in new missions!";\n'''.format(file_to_write_to, int(i//nthread + 1)), file=tempfile)
            print(temp, file=tempfile)
            print('''echo "{} Group {} is finished.";\n'''.format(file_to_write_to, int(i//nthread + 1)), file=tempfile)
            print('exit 0', file=tempfile)

        write_to_shcaller += str('sh ' + nmr_shlst[int(i//nthread)] + ' && ')

        i += nthread
    
    write_to_shcaller = write_to_shcaller[0:-4]
    with open(shcaller, 'w') as sh:
        print('#!/bin/sh\n', file=sh)
        print(write_to_shcaller, file=sh)

main()
