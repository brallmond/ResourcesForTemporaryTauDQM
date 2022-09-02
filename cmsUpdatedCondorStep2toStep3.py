# originally written by Vinaya Krishna for the Tau POG
# changed by Braden for his own use

#!/usr/bin/env python3
import imp # imp module is deprecated in favor of importlib
import math
import argparse
import os
import sys

# cms specific  
import FWCore.ParameterSet.Config as cms

parser = argparse.ArgumentParser(description='Submit condor jobs for Tau DQM step2') 

parser.add_argument('-i', '--inConfFile', dest='inConfFile', action='store', required='True',
                    help='the input configuration.py file')
parser.add_argument('-o', '--outDir', dest='outDir', action='store', required='True',
                    help='output directory for finished condor jobs (should be an EOS directory)')
parser.add_argument('-f', '--fileList', dest='fileList', action='store', required='True',
                    help='list of RAW root files to be processed')
parser.add_argument('-p', '--proxyPath', dest='proxyPath', action='store', required='True',
                    help='the location of your proxy (the file generated when you initialize your grid certificate)')
parser.add_argument('-n', '--nFilesPerJob', dest='nFilesPerJob', action='store', default=1,
                    help='number of files in config per job (1 is default)')
parser.add_argument('-j', '--jobType', dest='jobType', action='store', default='tomorrow',
                    help='type of condor job (longlunch, workday, tomorrow)')
parser.add_argument('-b', '--condorJobDir', dest='condorJobDir', action='store', default='CondorJob',
                    help='name of directory you\'d like condor jobs stored')

args = parser.parse_args()

inConfFile = args.inConfFile
outDir = args.outDir
fileList = open(str(args.fileList), 'r')
proxyPath = args.proxyPath
nFilesPerJob = int(args.nFilesPerJob) #opt
if nFilesPerJob <= 0:
  print("nFilesPerJob must be greater than zero! Exiting")
  sys.exit()

jobType = args.jobType #opt
condorJobDir = args.condorJobDir

# Show user all the inputs they set
print("input configuration file:  {}".format(inConfFile)) #{:>} right-aligns
print("output directory:          {}".format(outDir))
print("path to proxy:             {}".format(proxyPath))
print("number of files per job:   {}".format(nFilesPerJob))
# it's dumb that these are called flavors/flavours 
print("condor job type:           {}".format(jobType))
print("directory to store jobs:   {}".format(condorJobDir))


# Make directories for the jobs to submit, don't overwrite existing directory
# used this stackoverflow (3rd answer) 
# https://stackoverflow.com/questions/18973418/os-mkdirpath-returns-oserror-when-directory-does-not-exist
if not os.path.exists(condorJobDir):
  os.makedirs(condorJobDir)
else:
  print("Directory {} exists! Will not overwrite. Exiting".format(condorJobDir))
  sys.exit()

# make fileList entries into python array by removing the '\n' at the end of each line
rootFiles = [entry[:-1] for entry in fileList]
if len(rootFiles) == 0:
  print("No input root files! Exiting")
  sys.exit()

# load the input python file as "process" so poolsource input files can be appended
# TODO: update so imp is no longer used
handle = open(inConfFile, 'r')
cfo = imp.load_source("pycfg", inConfFile, handle)
process = cfo.process
handle.close()

# add all root files to process PoolSource
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(rootFiles),
)

# keep track of the original source 
fullSource = process.source.clone()

print("Number of files in the source: {}".format(len(process.source.fileNames)))
print(process.source.fileNames)

# smallest number of jobs to get all input files in requested number of jobs
nJobs = math.ceil( len(process.source.fileNames) / nFilesPerJob)

print("Number of jobs to be created: {}".format(nJobs))
    
# assign path to requested jobDirectory to MYDIR
currentDir = os.getcwd() 

# make job scripts      
for i in range(nJobs):
    i = str(i)
    jobDir = currentDir + '/' + condorJobDir + '/Job_%s/' %i
    os.system('mkdir %s' %jobDir)
    tmp_jobname = "sub_%s.sh" %i
    tmp_job = open(jobDir + tmp_jobname, 'w')
    tmp_job.write("#!/bin/sh\n")

    # if a proxy is given, write info in the run script to use the proxy
    if proxyPath != "noproxy":
        tmp_job.write("export X509_USER_PROXY=$1\n")
        tmp_job.write("voms-proxy-info -all\n")
        tmp_job.write("voms-proxy-info -all -file $1\n")

    tmp_job.write("cd $TMPDIR\n")
    tmp_job.write("mkdir Job_%s\n" %i)
    tmp_job.write("cd Job_%s\n" %i)
    tmp_job.write("cd %s\n" %currentDir)
    tmp_job.write("eval `scramv1 runtime -sh`\n")
    tmp_job.write("cd -\n")
    tmp_job.write("cp -f %s* .\n" %jobDir) # -f forces copying
    tmp_job.write("cp %s/run_cfg_%s.py .\n" %(outDir, i))
    tmp_job.write("cmsRun run_cfg_%s.py\n" %i)
    tmp_job.write("echo 'sending the file back'\n")
    tmp_job.write("cp step2_RAW2DIGI_L1Reco_RECO_DQM.root %s/step2_RAW2DIGI_L1Reco_RECO_DQM_%s.root\n" %(outDir, i))
    tmp_job.write("rm step2_RAW2DIGI_L1Reco_RECO_DQM.root\n")
    tmp_job.close()
    os.system("chmod +x %s" %(jobDir + tmp_jobname))

    print ("preparing job number %s/%s" %(i, nJobs-1))
    i = int(i)
    iFileMin = i*nFilesPerJob
    iFileMax = (i+1)*nFilesPerJob

    process.source.fileNames = fullSource.fileNames[iFileMin:iFileMax]

    tmp_cfgFile = open(outDir + '/run_cfg_%s.py' %str(i), 'w')
    tmp_cfgFile.write(process.dumpPython())
    tmp_cfgFile.close()

# write condor file for job
condor_str = "executable = $(filename)\n"
if proxyPath != "noproxy":
    condor_str += "Proxy_path = %s\n" %proxyPath
    condor_str += "arguments = $(Proxy_path) $Fp(filename) $(ClusterID) $(ProcId)\n"
else:
    condor_str += "arguments = $Fp(filename) $(ClusterID) $(ProcId)\n"
condor_str += "output = $Fp(filename)hlt.stdout\n"
condor_str += "error = $Fp(filename)hlt.stderr\n"
condor_str += "log = $Fp(filename)hlt.log\n"
condor_str += '+JobFlavour = "%s"\n' %jobType
condor_str += "queue filename matching (" + currentDir + '/' + condorJobDir + "/Job_*/*.sh)"
condor_name = currentDir + "/condor_cluster.sub"
condor_file = open(condor_name, "w")
condor_file.write(condor_str)

# write file to submit jobs
sub_total = open("sub_total.jobb", "w")
sub_total.write("condor_submit %s\n" %condor_name)
os.system("chmod +x sub_total.jobb")
