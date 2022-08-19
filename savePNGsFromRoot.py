import ROOT 
import argparse 
 
ROOT.gROOT.SetBatch(True) # sets visual display off (i.e. no graphs/TCanvas)

if __name__ == "__main__": 

  parser = argparse.ArgumentParser(description='Open a .root file') 
  parser.add_argument('-i', '--inputRootFile', dest='inFilename', action='store', 
                    help='the input .root file\'s name') 
  args = parser.parse_args() 

  inFile = ROOT.TFile.Open(args.inFilename,"READ") 

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

  # Don't end your final directory with /
  # It causes a null-pointer for some reason

  directory = "DQMData/Run 357612/HLT/Run summary/TAU/TagAndProbe"
  listOfHLTs = inFile.Get(directory).GetListOfKeys()
  # to print your keys, use the Print() function on the object
  #inFile.Get(directory).GetListOfKeys().Print()

  # generate same graphs for every HLT path in TagAndProbe  
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
      c1.Print(graphFilename, "png")



