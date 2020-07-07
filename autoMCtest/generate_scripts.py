import os

masslist =	[260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]

channels =	["ElEl","MuEl","MuMu","MuMu_ElEl_MuEl"]

dirnames =	["MTonly", "MTandMT2", "MTandMT2_MJJ"]

pointlist =	["0", "04", "12", "2", "28", "36", "4", "48", "56", "6", "72"]
pointlist = 	["0"]

workdir = "/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/"

if os.path.exists(workdir) == False:
  os.mkdir(workdir)
 

fname_all = workdir+"Radion_allinOne_run_asymptotic.sh"

script_all = open(fname_all, "write")
script_all.write("#!/bin/bash\n")
script_all.write("cd "+workdir+"\n")
script_all.write("eval `scramv1 runtime -sh`\n")

for dirname in dirnames:
  for point in pointlist:

    for mass in masslist:
      massdir = workdir + "GGToX0ToHHTo2B2L2Nu_nnout_{name}_nnstep0p04_nncut0p{point}_limits/".format(name = dirname, point = point) + "M{0}/".format(mass)
      if os.path.exists(massdir) == False:
        os.mkdir(massdir)
      for channel in channels:
        ch = channel
        fname = massdir + "Radion_M{0}_{1}_run_asymptotic.sh".format(mass, ch)
        script_all.write("source "+fname + "\n")
        script = open(fname, "write")
        script.write("#!/bin/bash\n")
        script.write("echo 'start channel {0}'\n".format(ch))
        script.write("pushd "+massdir+"\n")
        script.write("# If workspace does not exist, create it once\n")
        script.write("if [ ! -f GGToX0ToHHTo2B2L2Nu_M{0}_{1}_combine_workspace.root ]; then\n".format(mass, ch))
        script.write("text2workspace.py GGToX0ToHHTo2B2L2Nu_M{0}_{1}.dat -m {0} -o GGToX0ToHHTo2B2L2Nu_M{0}_{1}_combine_workspace.root -P HiggsAnalysis.CombinedLimit.DYEstimationCombineModelTao:DYDataDrivenEstimationModelInstance\n".format(mass, ch))
        script.write("fi\n\n")
        script.write("# Run limit\n\n")
        script.write("combine --rMax 500 -m {0} -t -1 -n GGToX0ToHHTo2B2L2Nu_M{0}_{1} GGToX0ToHHTo2B2L2Nu_M{0}_{1}_combine_workspace.root &> GGToX0ToHHTo2B2L2Nu_M{0}_{1}.log\n".format(mass, ch))
        script.write("popd\n")
        script.write("echo 'finish channel {0}'\n".format(ch))

        os.system("chmod 775 "+fname)
os.system("chmod 775 "+fname_all)


