import ROOT
import os

masslist =      [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
process = 	["ElEl", "MuEl", "MuMu"]
varlist = 	["MTonly", "MTandMT2", "MTandMT2_MJJ"]

workdir = "/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p04/"
indir = workdir+"HHbbWW_20200401_NNoutput_MjjCR_NNcutstudy2D_HMEbinsv4_1p15/"
outdir = workdir+"linear/"
os.system("mkdir -p "+outdir)

mjj_CR = True #Using mjj control regions or not

for var in varlist:
  for mass in masslist:
    f = ROOT.TFile.Open(indir+"Hhh_FinalBGYield_xsec1pb_NNvsHME_nnout_{var}_nnstep0p04_nncut0p0_SignalM{m}.root".format(m = mass, var = var))
    t = ROOT.TFile.Open(outdir+"linear_{var}_M{m}.root".format(var = var, m = mass), "recreate")

    for key in f.GetListOfKeys():
      branch = f.Get(key.GetName())
      xBins = branch.GetNbinsX()
      yBins = branch.GetNbinsY()

      print "there are ", yBins, " ybins in", var, mass

      if mjj_CR:
        new_xFinal = 3.0*yBins #If mjj control regions used, 3 per y bin
      if not mjj_CR:
        new_xFinal = 1.0*yBins #If they aren't used, only 1 per y bin
      hist = ROOT.TH1F("{name}".format(name = key.GetName()), "{name}".format(name = key.GetName()), xBins*yBins, 0, new_xFinal)
      for i in range(xBins):
        for j in range(yBins):
          hist.SetBinContent((i+1)+(xBins*j), branch.GetBinContent(i+1, j+1))
          hist.SetBinError((i+1)+(xBins*j), branch.GetBinError(i+1, j+1))

      hist.Write()
      del branch
      del hist

    t.Close()


