import ROOT 
import argparse 
import sys
import os
 
ROOT.gROOT.SetBatch(True) # sets visual display off (i.e. no graphs/TCanvas)

if __name__ == "__main__": 

  parser = argparse.ArgumentParser(description='Open a .root file') 
  parser.add_argument('-i', '--inputRootFile', dest='inFilename', action='store', 
                    help='the input .root file\'s name') 
  parser.add_argument('-t', '--tauDirectory', dest='tauDirectory', action='store', default='TagAndProbe',
                    help='which tau directory do you want to save images from?')
  parser.add_argument('-o', '--outputDirectoyr', dest='outputDirectory', action='store', default='images',
                    help='name a directory to store the output.')
  args = parser.parse_args() 

  inFile = ROOT.TFile.Open(args.inFilename,"READ") 

  possibleTauDirs = ["Inclusive", "PFTaus", "TagAndProbe"]
  if (args.tauDirectory not in possibleTauDirs):
    print("Not a directory. Choose one of these: {}".format(possibleTauDirs))
    sys.exit()


  #   ^^^^ getting a file
  #   vvvv PyROOT file stuff

  # Summary
  # There are two ways to access root directories.
  # Either dir.subdir.subsubdir.etc
  # Or dir.Get("subdir")
  # Notably, these can be mixed.

  # Above works fine if you know the directory names.
  # If you don't, you can always do .GetListOfKeys().Print()
  # on the end of a directory (or tree) (like dir.GetListOfKeys().Print())
  # When executed, this lists all the names of the objects present.

  # DON'T end your final directory with "/"
  # It causes a null-pointer for some reason

  directory = "DQMData/Run 357612/HLT/Run summary/TAU/" + args.tauDirectory
  listOfHLTs = inFile.Get(directory).GetListOfKeys()

  os.mkdir(args.outputDirectory)
  # generate same graphs for every HLT path in given tauDirectory
  for HLT in listOfHLTs:
    pathToHLT = directory + "/" + HLT.GetName()
    print(pathToHLT)
    listOfGraphs = inFile.Get(pathToHLT).GetListOfKeys()

    for graph in listOfGraphs:
      # don't want helper graphs (num/denom), or the graphs with <> in their name
      if (graph.GetName() == "helpers" or "<" in graph.GetName()): continue

      pathToGraph = pathToHLT + "/" + graph.GetName()
      graphFilename = (HLT.GetName() + graph.GetName()).replace("/","_")+".png"

      c1 = ROOT.TCanvas("c1", "", 600, 400)
      inFile.Get(pathToGraph).Draw()
      # canvas holds whatever you drew last, Printing a canvas saves it
      c1.Print(args.outputDirectory+'/'+graphFilename, "png")



