import os
import ROOT
import re
import numpy as np
import datetime
import sys 
import csv
sys.argv.append( '-b' )

def extranumber(s):
    num = []
    for t in s.split():
        try:
            num.append(float(t))
        except ValueError:
            pass

    return num


def extractlimitfromtxtfile(logfile):
    logopen = open(logfile, "read")
    signal_xsec = 1.0
    percents = [2.5, 16.0, 50.0, 84.0, 97.5, -1]
    limits_lines = {}
    limits = {}
    for key in percents:
        limits_lines[key] = []
    for line in logopen:
        if line.startswith("Expected "):
	    for key in [2.5, 16.0, 50.0, 84.0, 97.5]:
	        keystr = "Expected %4.1f"%key
	        if keystr in line:
		    limits_lines[key].append(line)
        elif line.startswith("Observed Limit:"):
	    limits_lines[-1].append(line)
    for key in percents:
        if len(limits_lines[key]) == 0:
	    continue
        line = limits_lines[key][-1] 
	if key != -1:
	    line = line.replace("Expected %4.1f%%:"%key, "")
	nums = extranumber(line)
        if len(nums)>0:
	    limits[key]  = nums[0] * signal_xsec
    return limits


def CombineLimitplots(filelist, histlist, masspoints, xtitle, legends, text, plotname):

    colors = [ROOT.kRed, ROOT.kMagenta+2,ROOT.kBlue+1, ROOT.kBlack, ROOT.kOrange]
    markers = [21,22,23, 20, 24]
    tfilelist = []
    for f in filelist:
        tfilelist.append( ROOT.TFile(f, "READ"))


    c1 = ROOT.TCanvas("c1","c1",600, 800)
    c1.SetLogy()
    c1.SetGridx()  
    c1.SetGridy()  
    c1.SetTickx()  
    c1.SetTicky()  
    minx = min(masspoints)*0.8
    maxx = max(masspoints)*1.3
    b1 = ROOT.TH1F("b2","b2", len(masspoints)*2, minx, maxx)
    b1.SetTitle(" ")
    b1.GetYaxis().SetTitle("95% C.L. limits on production rate (fb)")
    b1.GetXaxis().SetTitle(xtitle)
    yhigh = 2000.0 #2000.0
    ylow = 1.0#1.0
    b1.GetYaxis().SetRangeUser(ylow, yhigh)
    b1.SetStats(0)
    b1.Draw()


    leg0 = ROOT.TLegend(0.65,0.8,0.9,0.90)
    leg0.SetFillColor(ROOT.kWhite)
    leg0.SetTextFont(42)
    leg0.SetHeader( legends[-1] )

    drawUncertainty = True
    if drawUncertainty:
	i =  len(tfilelist)- 1
	tf = tfilelist[i]
        tf.cd()
	g_central = tf.Get(histlist[i]+"_central")
	g_central.SetLineColor(colors[i])
	g_central.SetMarkerColor(colors[i])
	g_central.SetMarkerStyle(markers[i])
	g_onesigma = tf.Get(histlist[i]+"_onesigma")
	g_twosigma = tf.Get(histlist[i]+"_twosigma")
	g_twosigma.SetFillColorAlpha(ROOT.kOrange, 0.5)
	g_twosigma.SetLineStyle(2)
	g_onesigma.SetFillColorAlpha(ROOT.kGreen+2, 0.5)
	g_onesigma.SetLineStyle(2)
	leg0.AddEntry(g_central,"Expected 95% upper limit","l")
	leg0.AddEntry(g_onesigma,"1 std. deviation, Expected","f")
	leg0.AddEntry(g_twosigma,"2 std. deviation, Expected","f")
	g_twosigma.Draw("fe3same")
	g_onesigma.Draw("fe3same")


    leg = ROOT.TLegend(0.17,0.2,0.4,0.2+0.045*len(tfilelist))
    leg.SetFillColor(ROOT.kWhite)
    leg.SetTextFont(42)
    leg.SetHeader("Expected Limits")
    for i, tf in enumerate(tfilelist):
        tf.cd()
        g_data = tf.Get(histlist[i]+"_data")
        g_data.SetLineColor(colors[i])
        g_data.SetMarkerColor(colors[i])
        g_data.SetMarkerStyle(markers[i])
    for i, tf in enumerate(tfilelist):
        tf.cd()
        g_data = tf.Get(histlist[i]+"_data")
        g_data.SetLineColor(colors[i])
        g_data.SetMarkerColor(colors[i])
        g_data.SetMarkerStyle(markers[i])
	g_central = tf.Get(histlist[i]+"_central")
	g_central.SetLineColor(colors[i])
	g_central.SetLineStyle(2)
	g_central.SetMarkerColor(colors[i])
	g_central.SetMarkerStyle(markers[i])
	g_central.Draw("lsame")
        g_data.Draw("lpsame")
        thisleg = leg.AddEntry(g_data, legends[i],"p")
        thisleg.SetTextColor(colors[i])
    tex0 = ROOT.TLatex(0.08,0.91, "#scale[1.4]{#font[61]{CMS}} Internal"+" "*5+"35.87 fb^{-1}(13 TeV),2016")
    tex0.SetNDC(); tex0.SetTextSize(.04); tex0.SetTextFont(42)
    tex0.Draw("same")
    tex1 = ROOT.TLatex(0.2,0.21, text)
    tex1.SetNDC(); tex1.SetTextSize(.04); tex1.SetTextFont(42)
    
    leg0.Draw("same")
    leg.Draw("same")
    c1.SaveAs(plotname+"_95Upperlmit_data_HHbbWW_combined_v2.pdf")
    c1.SaveAs(plotname+"_95Upperlmit_data_HHbbWW_combined_v2.C")

def makeBrazilPlot(masspoints_v0, alllimits, xtitle, text, plotname):
    drawData = False
    onesigma_up = []
    twosigma_up = []
    onesigma_low = []
    twosigma_low = []
    central = []
    data = []
    masspoints = []
    for mass in masspoints_v0:
        limits = alllimits[mass]	
        if len(limits.keys()) < 6:
            print("warning!!!!!!, not all limits found on mass %d"%mass, limits)
            continue
        central.append(limits[50.0])
        twosigma_low.append(limits[2.5])
        onesigma_low.append(limits[16.0])
        onesigma_up.append(limits[84.0])
        twosigma_up.append(limits[97.5])
    	data.append(limits[-1])
        masspoints.append(mass)
    fakeerrors = [0.0]*len(masspoints)
    c1 = ROOT.TCanvas("c1","c1",600, 800)
    outfilename = plotname+".root"
    tfile = ROOT.TFile(outfilename,"UPDATE")
    
    c1.SetLogy()
    c1.SetGridx()  
    c1.SetGridy()  
    c1.SetTickx()  
    c1.SetTicky()  
    onesigma_low.reverse()
    twosigma_low.reverse()
    onesigma_all = onesigma_up + onesigma_low
    twosigma_all = twosigma_up + twosigma_low
    masspoints_all = masspoints + list(reversed(masspoints))
    masspoints_f =  np.array(masspoints)+0.0
    g_data = ROOT.TGraph(len(masspoints),  np.array(masspoints)+0.0,  np.array(data))
    g_central = ROOT.TGraph(len(masspoints),  np.array(masspoints)+0.0,  np.array(central))
    g_onesigma = ROOT.TGraph(len(masspoints)*2,  np.array(masspoints_all)+0.0,  np.array(onesigma_all))
    g_twosigma = ROOT.TGraph(len(masspoints)*2,  np.array(masspoints_all)+0.0,  np.array(twosigma_all))


    g_twosigma.SetFillColorAlpha(ROOT.kOrange, 0.5)
    g_twosigma.SetLineStyle(2)
    g_onesigma.SetFillColorAlpha(ROOT.kGreen+2, 0.5)
    g_onesigma.SetLineStyle(2)
    g_central.SetLineWidth(2)
    g_central.SetLineStyle(7)
    g_central.SetLineColor(9)
    g_central.SetMarkerStyle(20)
    g_central.SetMarkerSize(1)
    g_central.SetMarkerColor(9)
    g_data.SetLineWidth(2)
    g_data.SetLineStyle(1)
    g_data.SetLineColor(ROOT.kBlack)
    g_data.SetMarkerStyle(20)
    g_data.SetMarkerSize(1)
    g_data.SetMarkerColor(ROOT.kBlack)

    minx = min(masspoints)*0.9
    maxx = max(masspoints)*1.3
    b1 = ROOT.TH1F("b2","b2", len(masspoints)*2, minx, maxx)
    b1.SetTitle(" ")
    b1.GetYaxis().SetTitle("95% C.L. limits on production rate (fb)")
    b1.GetXaxis().SetTitle(xtitle)
    yhigh = 2000.0 #10000.0
    ylow = 1.0#10.0
    b1.GetYaxis().SetRangeUser(ylow, yhigh)
    b1.SetStats(0)

    b1.Draw()
    g_twosigma.Draw("fe3same")
    g_onesigma.Draw("fe3same")
    g_central.Draw("lpsame")
    if drawData :
	g_data.Draw("lpsame")
    suffixname =  plotname.split("/")[-1]
    g_data.SetName("%s_data"%suffixname)
    g_central.SetName("%s_central"%suffixname)
    g_onesigma.SetName("%s_onesigma"%suffixname)
    g_twosigma.SetName("%s_twosigma"%suffixname)
    g_central.Write()
    g_data.Write()
    g_onesigma.Write()
    g_twosigma.Write()

    
    leg = ROOT.TLegend(0.65,0.8,0.9,0.90)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetTextFont(42)
    if drawData :
	leg.AddEntry(g_data,"Observed","pl")
    leg.AddEntry(g_central,"Expected 95% upper limit","l")
    leg.AddEntry(g_onesigma,"1 std. deviation, Expected","f")
    leg.AddEntry(g_twosigma,"2 std. deviation, Expected","f")
    tex0 = ROOT.TLatex(0.08,0.91, "#scale[1.4]{#font[61]{CMS}} Internal"+" "*5+"35.87 fb^{-1}(13 TeV),2016")
    tex0.SetNDC(); tex0.SetTextSize(.04); tex0.SetTextFont(42)
    tex0.Draw("same")
    tex1 = ROOT.TLatex(0.2,0.21, text)
    tex1.SetNDC(); tex1.SetTextSize(.04); tex1.SetTextFont(42)
    tex1.Draw("same")
    
    leg.Draw("same")
    c1.SaveAs(plotname+"_95Upperlmit_data_HHbbWW.pdf")
    c1.SaveAs(plotname+"_95Upperlmit_data_HHbbWW.C")



def makeLimitsPlots(masslist, workdir, plotsuffix=""):
    channels =   ["ElEl","MuEl","MuMu", "ElEl_MuEl_MuMu"]
    chnames = ["ElEl","MuEl","MuMu", "all channels"]

    out_prefix = "autoMC_true"
    #out_prefix = "autoMC_false"
    scriptsuffix = "linear"
    alllimits = {}
    skippedscript = []
    for channel in channels:
	alllimits[channel] = {}
    for mass in masslist:
	thisdir = workdir + "{m}/".format(m = mass)
	limits = {}
	for channel in channels:
	    fname = thisdir+"Radion_M%d_%s_run_asymptotic_%s.sh"%(mass, channel, scriptsuffix)
	    #print "ch ",channel, " fname ",fname

            logfile = os.path.join(thisdir,  "{out_prefix}_{ch}_M{m}.log".format(m = mass, ch = channel, out_prefix = out_prefix))
	    if not os.path.exists(logfile):
		print("file does not exist, skipped!!! : ", logfile)
		skippedscript.append(fname)
		continue
	    limits = extractlimitfromtxtfile(logfile) 
	    if len(limits) != 6:
		print("+++++++++++  Warning!!!, Failed to get limits!!  ", limits," +++++++++++")
	    alllimits[channel][mass] = limits
    allplots = []
    rfiles = []
    histlist = []
    csvfile = open(workdir+'limits_%s.csv'%scriptsuffix, 'wb')
    writer = csv.writer(csvfile)
    writer.writerow([ ["channel_Mass"]  + [key for key in [-1, 2.5, 16.0, 50.0, 84.0, 97.5]] ])
    for i, channel in enumerate(channels):
	for mass in masslist:
	    rowname =  channel+"_%d"%mass
	    writer.writerow([ [rowname]  + [alllimits[channel][mass][key] for key in [-1, 2.5, 16.0, 50.0, 84.0, 97.5] if key in alllimits[channel][mass].keys()] ])
	print("start work on brazil plot "+"Radion_"+channel+"_"+scriptsuffix+"_"+plotsuffix)
	plotname = os.path.join(workdir, "Radion_"+channel+"_"+scriptsuffix+"_"+plotsuffix)
	makeBrazilPlot(masslist, alllimits[channel], "Radion Mass [GeV]", chnames[i], plotname)
	allplots.append(plotname)
	rfiles.append(plotname+".root")
	histlist.append("Radion_"+channel+"_"+scriptsuffix+"_"+plotsuffix)
    rootfile =  os.path.join(workdir, "Radion_allchannels_"+scriptsuffix+"_"+plotsuffix+".root")
    os.system("hadd -f "+rootfile+" "+' '.join(rfiles))
    allplotname = os.path.join(workdir, "Radion_final_"+scriptsuffix+"_"+plotsuffix)
    CombineLimitplots(rfiles, histlist, masslist, "Radion Mass [GeV]", chnames, "HH#rightarrow bbWW #rightarrow bbl#nul#nu", allplotname)

	    



masslist = [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
pwd = '/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/1D_binsize_0p04/output_autoMC_true/'
pwd = '/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/1D_binsize_0p04/output_autoMC_false/'
pwd = '/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p04/output_autoMC_false/'
pwd = '/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p04/output_autoMC_true/'
proclist = ["MTonly", "MTandMT2", "MTandMT2_MJJ"]
for proc in proclist:
  makeLimitsPlots(masslist, pwd+proc+"/", "")

