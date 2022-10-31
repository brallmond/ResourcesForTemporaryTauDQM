# Braden Allmond, October 31st 2022
# push-button submission of one run from one dataset to Condor using Tau DQM workflow

import subprocess # use instead of os, needed for dasgoclient, mkdir, and wc


###### GET USER INPUT
print("Common datasets are /Muon/Run2022E-v1/RAW and /Muon/Run2022F-v1/RAW ...")
print("Remember to copy your voms-proxy into this directory before proceeding ...")
DATASET = input("Please enter the dataset you'd like to use: ")
RUN     = input("Please enter the run number you'd like to use: ")

###### CHECK NUMBER OF FILES AVAILABLE AT VIABLE SITES
# this is technically vulnerable to arbitrary code-injection from the user (DATASET can be anything)
print("The dataset is at least partially available at the following sites ...")
command_dataset_sites = "dasgoclient --query \"site dataset=" + DATASET + "\""
# run the command via commandline, and capture the stdout, assigning it to a variable below and then processing the string to an array
command_dataset_sites = subprocess.run(command_dataset_sites, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
output_dataset_sites  = command_dataset_sites.stdout.split('\n')
output_dataset_sites.pop(-1) # remove empty string
output_dataset_sites = [site for site in output_dataset_sites if (("T2" in site) or (site == "T0_CH_CERN_Disk"))]
print(f"Viable sites are {output_dataset_sites} ...")

# find site with most files
site_with_most_files = ""
most_number_of_files = -1
output_filelist_name = "filelist_"+RUN+".txt"
first_file = ""
for SITE in output_dataset_sites:
  command_files_at_site = "dasgoclient --query \"file dataset=" + DATASET + " run in [" + RUN +"] site=" + SITE + "\""
  command_files_at_site = subprocess.run(command_files_at_site, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
  output_files_at_site  = command_files_at_site.stdout.split('\n')
  output_files_at_site.pop(-1)
  number_of_files = len(output_files_at_site)
  print(f"At {SITE} there are {len(output_files_at_site)} files")
  if number_of_files != 0 and number_of_files > most_number_of_files: 
    most_number_of_files = number_of_files
    site_with_most_files = SITE
    first_file = output_files_at_site[0]
    print(f"Writing files to {output_filelist_name} ...")
    print(f"Best site so far is {site_with_most_files} ...")
    # make output file, if there is another site with more files later this output file will be overwritten
    with open(output_filelist_name, "w") as output_filelist:
      for line in output_files_at_site:
        output_filelist.write("".join(line) + "\n")

# generate python config file
print(f"Generating python config file ...")
command_generate_python_config_file = """\
cmsDriver.py step2 -s RAW2DIGI,L1Reco,RECO,DQM --eventcontent DQM \
--datatier DQMIO --conditions 124X_dataRun3_v9 --era Run3 \
--geometry DB:Extended --process reRECO -n -1 --data \
--filein """ + first_file + """ --no_exec"""
print(command_generate_python_config_file)
command_generate_python_config_file = subprocess.run(command_generate_python_config_file, shell=True)

# set up steps before executing condor command
output_EOS = "/eos/user/b/ballmond/DQM/run_" + RUN
command_mkdir_output_EOS = "mkdir " + output_EOS
print(f"Making new DQM directory on EOS here {output_EOS} ...")
command_mkdir_output_EOS = subprocess.run(command_mkdir_output_EOS, shell=True)

command_generate_condor_jobs="""\
python3 condor_handling_standard_DQM.py \
-i step2_RAW2DIGI_L1Reco_RECO_DQM.py \
-o """ + output_EOS + """ \
-f """ + output_filelist_name + """ \
-p /afs/cern.ch/user/b/ballmond/public/DQM_CMSSW_12_4_0/src/x509up_u134427 \
-n 1 -j tomorrow \
-b DQM_run_""" + RUN
command_generate_condor_jobs = subprocess.run(command_generate_condor_jobs, shell=True)

print("Run ./sub_total.jobb to submit")


