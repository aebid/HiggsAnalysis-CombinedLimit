import ROOT
import os

masslist =      [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
channellist = 	["ElEl", "MuEl", "MuMu"]
processlist = 	["TTbar","SingleTop","Drell_Yan","data_untagged","TTbar_untagged","SingleTop_untagged", "ttV","VV","Signal"]
statslist = 	["CMS_eff_b_heavy","CMS_eff_b_light","CMS_pu", "CMS_pdf", "CMS_eff_trigger","CMS_eff_e","CMS_eff_mu","CMS_iso_mu","QCDscale"]
traininglist = 	["MTonly", "MTandMT2", "MTandMT2_MJJ"]

indir = "1D/"

for training in traininglist:
  outdir = "GGToX0ToHHTo2B2L2Nu_nnout_{training}_nnstep0p04_nncut0p0_limits/".format(training = training)
  for mass in masslist:
    processnames = ["TT","sT","DY","data_untagged","TT_untagged","sT_untagged","ttV","VV", "RadionM{}".format(mass)]
    infile = ROOT.TFile.Open(indir+"Hhh_FinalBGYield_xsec1pb_NN_nnout_{training}_nnstep0p04_nncut0p0_SignalM{mass}.root".format(mass = mass, training = training))
    print "Loading file ", indir, "Hhh_FinalBGYield_xsec1pb_NN_nnout_{training}_nnstep0p04_nncut0p0_SignalM{mass}.root".format(mass = mass, training = training)
    for channel in channellist:
      outfile = ROOT.TFile.Open(outdir+"M{m}/GGToX0ToHHTo2B2L2Nu_M{m}_{ch}_shapes.root".format(m = mass, ch = channel), "recreate")
      print "Creating file ", outdir, "M{m}/GGToX0ToHHTo2B2L2Nu_M{m}_{ch}_shapes.root".format(m = mass, ch = channel)
      histname_data_obs = "data_obs_{ch}_M{m}".format(ch = channel, m = mass)
      hist_data_obs = infile.Get(histname_data_obs)
      hist_clone_data_obs = hist_data_obs.Clone("data_obs")
      outfile.Write()
      del hist_clone_data_obs

      for i, process in enumerate(processlist):
        #print "channel ", channel, " process ", process, " start to import this process"
        if (channel == "MuMu" or channel == "ElEl") and process == "Drell_Yan":
          #print "Drell Yan"
          continue
        if channel == "MuEl" and ("untagged" in process):
          #print "Untagged"
          continue

        histname_nominal = processnames[i]+"_"+channel
        #print "about to load ", histname_nominal
        hist_nominal = infile.Get(histname_nominal)
        #print hist_nominal
        if "Signal" in process:
          hist_nominal.Scale(1e-3/5.0)

        hist_clone_nominal = hist_nominal.Clone(processlist[i])
        outfile.Write()
        del hist_clone_nominal

        if "data" in process:
          continue #This seems useless? But its in writeworkspace1D.C


        for stat in statslist:
          #print i, mass, channel, process, stat
          histname_up = processnames[i]+"_"+channel+"_"+stat+"_up"
          histname_down = processnames[i]+"_"+channel+"_"+stat+"_down"
          histname_sys = process+"_"+stat

          hist_up = infile.Get(histname_up)
          hist_down = infile.Get(histname_down)

          if "QCDscale" in histname_sys and "untagged" in histname_sys:
            histname_sys = process+"_"+stat+process.replace("_untagged", "")
          elif "QCDscale" in histname_sys and "untagged" not in histname_sys:
            histname_sys = process+"_"+stat+process

          if "CMS_eff_trigger" in histname_sys:
            histname_sys = process+"_"+stat+"_"+channel

          #if "Signal" in process and "CMS_pdf" in stat:
            #print "process ", histname_sys, " up entries ", hist_up.Integral(), " down ", hist_down.Integral()
          #print "saving ", histname_sys
          hist_clone_up = hist_up.Clone(histname_sys+"Up")
          hist_clone_down = hist_down.Clone(histname_sys+"Down")
          outfile.Write()
          del hist_clone_up
          del hist_clone_down

      outfile.Close()
    infile.Close()
