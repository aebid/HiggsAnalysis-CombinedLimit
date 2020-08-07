import ROOT
import os
import sys
import Datacards

masslist = 	[260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
channellist =	["ElEl", "MuEl", "MuMu"]
trainlist =	["MTonly", "MTandMT2", "MTandMT2_MJJ"]
processlist = 	["TTbar","SingleTop","Drell_Yan","data_untagged","TTbar_untagged","SingleTop_untagged", "ttV","VV","Signal"]
statslist =     ["CMS_eff_b_heavy","CMS_eff_b_light","CMS_pu", "CMS_pdf", "CMS_eff_trigger","CMS_eff_e","CMS_eff_mu","CMS_iso_mu","QCDscale"]

autoMC = False
indir = "/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/1D_binsize_0p04/HHbbWW_20200401_NNoutput_MjjCR_NNcutstudy1D/"
indir = "/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p1/linear/"
out_folder = "/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p1/fitdiagnostics_autoMC_true"

out_prefix = "autoMC_false"  ##Outfile names are {prefix}_{channel}_M{mass}_shapes.root


os.system("mkdir -p {out_folder}".format(out_folder = out_folder))
os.system("mkdir -p "+out_folder+"/condor")
os.system("mkdir -p "+out_folder+"/condor/output")
os.system("mkdir -p "+out_folder+"/condor/error")
os.system("mkdir -p "+out_folder+"/condor/log")


for train in trainlist:
  os.system("mkdir -p {out_folder}/{tr}".format(out_folder = out_folder, tr = train))
  for mass in masslist:
    processnames = ["TT","sT","DY","data_untagged","TT_untagged","sT_untagged","ttV","VV", "RadionM{}".format(mass)]
    infile_name = indir+"linear_{tr}_M{m}.root".format(m = mass, tr = train)
    infile = ROOT.TFile.Open(infile_name)
    for channel in channellist:
      os.system("mkdir -p {out_folder}/{tr}/{m}".format(tr = train, m = mass, out_folder = out_folder))
      outfile_name = "{out_folder}/{tr}/{m}/{out_prefix}_{ch}_M{m}_shapes.root".format(out_prefix = out_prefix, tr = train, ch = channel, m = mass, out_folder = out_folder)

      if autoMC == False:
        command = 'root -b -q "writeworkspace1D.C ({m}, \\"{ch}\\", \\"NN\\", 0.0, 33.0, \\"{infile}\\", \\"{output}\\")"'.format(m = mass, ch = channel, infile = infile_name, output = outfile_name)
        os.system(command)

      if autoMC == True:
        outfile = ROOT.TFile.Open(outfile_name, "recreate")
        histname_data_obs = "data_obs_{ch}_M{m}".format(ch = channel, m = mass)
        hist_data_obs = infile.Get(histname_data_obs)
        hist_clone_data_obs = hist_data_obs.Clone("data_obs")
        outfile.Write()
        del hist_clone_data_obs
        for i, process in enumerate(processlist):
          if (channel == "MuMu" or channel == "ElEl") and process == "Drell_Yan":
            continue
          if channel == "MuEl" and ("untagged" in process):
            continue
          histname_nominal = processnames[i]+"_"+channel
          hist_nominal = infile.Get(histname_nominal)
          if "Signal" in process:
            hist_nominal.Scale(1e-3/5.0)
          hist_clone_nominal = hist_nominal.Clone(processlist[i])
          outfile.Write()
          del hist_clone_nominal
          if "data" in process:
            continue
          for stat in statslist:
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
            hist_clone_up = hist_up.Clone(histname_sys+"Up")
            hist_clone_down = hist_down.Clone(histname_sys+"Down")
            outfile.Write()
            del hist_clone_up
            del hist_clone_down
        outfile.Close()
    if autoMC == True:
      infile.Close()


datacard = Datacards.Datacards()
for train in trainlist:
  for mass in masslist:
    channels_rootfile = {}
  
    for channel in channellist:
      channels_rootfile[channel] = "{out_folder}/{tr}/{m}/{out_prefix}_{ch}_M{m}_shapes.root".format(tr = train, ch = channel, m = mass, out_folder = out_folder, out_prefix = out_prefix)
      outfile = "{out_folder}/{tr}/{m}/{out_prefix}_{ch}_M{m}.dat".format(tr = train, m = mass, ch = channel, out_folder = out_folder, out_prefix = out_prefix)

      datacard.generateDatacard(outfile, channels_rootfile[channel], channel, mass, True, autoMC)

    outfile_all = "{out_folder}/{tr}/{m}/{out_prefix}_ElEl_MuEl_MuMu_M{m}.dat".format(tr = train, m = mass, out_folder = out_folder, out_prefix = out_prefix)

    datacard.generateDatacard_multichannels(outfile_all, channels_rootfile, channellist, mass, True, autoMC)



channellist = ["ElEl", "MuEl", "MuMu", "ElEl_MuEl_MuMu"]

fname_all = out_folder+"/Run_all_scripts.sh"
cname_all = out_folder+"/Run_all_condors.sh"

script_all = open(fname_all, "write")
script_all.write("#!/bin/bash\n")
script_all.write("cd "+out_folder+"\n")
script_all.write("eval `scramv1 runtime -sh`\n")

condor_all = open(cname_all, "write")
condor_all.write("#!/bin/bash\n")
condor_all.write("cd "+out_folder+"/condor\n")
condor_all.write("eval `scramv1 runtime -sh`\n")

for train in trainlist:
  for mass in masslist:
    for channel in channellist:
      massdir = "{out_folder}/{tr}/{m}/".format(tr = train, m = mass, out_folder = out_folder)
      fname = massdir + "Run_{ch}_M{m}.sh".format(ch = channel, m = mass)
      script_all.write("source "+fname + "\n")
      script = open(fname, "write")
      script.write("#!/bin/bash\n")
      script.write("echo 'start channel {ch}'\n".format(ch = channel))
      script.write("pushd "+massdir+"\n")
      script.write("eval `scramv1 runtime -sh`\n")
      script.write("# If workspace does not exist, create it once\n")
      script.write("if [ ! -f {out_prefix}_{ch}_M{m}_combine_workspace.root ]; then\n".format(ch = channel, m = mass, out_prefix = out_prefix))
      script.write("text2workspace.py {out_prefix}_{ch}_M{m}.dat -m {m} -o {out_prefix}_{ch}_M{m}_combine_workspace.root -P HiggsAnalysis.CombinedLimit.DYEstimationCombineModelTao:DYDataDrivenEstimationModelInstance\n".format(ch = channel, m = mass, out_prefix = out_prefix))
      script.write("fi\n\n")
      script.write("echo 'finished text2workspace, starting combine' \n")
      script.write("date \n\n")
      script.write("#Run limit\n\n")
      script.write("combine -M FitDiagnostics -m {m} {out_prefix}_{ch}_M{m}_combine_workspace.root &> {out_prefix}_{ch}_M{m}.log\n".format(m = mass, ch = channel, out_prefix = out_prefix))
      #script.write("combine -M AsymptoticLimits -t -1 -m {m} -n {ch}_M{m} {out_prefix}_{ch}_M{m}_combine_workspace.root &> {out_prefix}_{ch}_M{m}.log\n".format(m = mass, ch = channel, out_prefix = out_prefix))
      script.write("popd\n")
      script.write("echo 'finish channel {ch}'\n".format(ch = channel))
      script.write("date \n\n")

      os.system("chmod 775 "+fname)

      condorname = out_folder+"/condor/Condor_{tr}_{ch}_M{m}.sh".format(tr = train, ch = channel, m = mass)
      script_condor = open(condorname, "write")
      script_condor.write("""universe                = vanilla
executable              = {fname}
arguments               = no
output                  = {out_folder}/condor/output/{out_prefix}_{tr}_{ch}_M{m}.$(ClusterId).$(ProcId).out
error                   = {out_folder}/condor/error/{out_prefix}_{tr}_{ch}_M{m}.$(ClusterId).$(ProcId).err
log                     = {out_folder}/condor/log/{out_prefix}_{tr}_{ch}_M{m}.$(ClusterId).log
request_memory          = 4000M
+JobFlavour             = "workday"
queue""".format(fname = fname, out_prefix = out_prefix, tr = train, ch = channel, m = mass, out_folder = out_folder))
      os.system("chmod 755 "+condorname)

      condor_all.write("condor_submit "+condorname + "\n")


os.system("chmod 775 "+fname_all)
os.system("chmod 775 "+cname_all)

