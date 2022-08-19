git clone https://github.com/brallmond/ResourcesForTemporaryTauDQM.git

This is a repo containing useful info about how to run Tau DQM

Start in the ```instructions``` directory with ```DownloadInstructionsTauDQM.txt```
to get a clean repo with Vinaya's PR in place. Then go to ```ListOfFilesAndTestRun.txt```
to do a test run. Finally, go to ```FullDataRun.txt```. Some info may need to be updated
if you use newer runs than when this repo was written.

The ```images``` repo has some pictures of what output from the DQM_.root file
made in "step_3" might look like under different conditions.

The ```generated_text_files``` repo has the relevant text files that are generated
by the first set of commands in ```instructions/ListOfFilesAndTestRun.txt```

In the top directory, ```cmsCondorStep2toStep3.py``` is used to submit jobs to
Condor as described in ```FullDataRun.txt```

```savePNGsFromRoot.py``` is a small script that saves all the graphs from 
the final DQM file under the TAU/TagAndProbe directory as .png files to the directory
it is executed in. I found this easier to do than looking through them with TBrowser.

This is a temporary repo! Hopefully we only have to do this one or two more times.

Once this PR is integrated, this repo should no longer be used.

https://github.com/cms-sw/cmssw/pull/38863

