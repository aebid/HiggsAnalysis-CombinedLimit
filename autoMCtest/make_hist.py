import ROOT
import os

branchlist = ["_MC_statistical_", "_CMS_pu_", "_CMS_eff_b_light", "_CMS_eff_trigger_", "_CMS_pdf_", "_CMS_eff_e", "_CMS_iso_mu_", "_CMS_eff_mu_", "_QCDscale_", "_CMS_eff_b_heavy_"]

channellist = ["MuMu", "MuEl", "ElEl"]
bgtypes = ["TT", "DY", "sT", "VV", "ttV"]
untagged = ["data_unntagged", "TT_untagged", "sT_untagged"]
colorlist = [800-4, 820-3, 900-3, 860-3, 616-7, 432+2, 400+2]

HMElist = [250.0, 287, 330, 379, 435, 500, 575, 661, 760, 873, 1003, 1200.0]
masslist = [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
masslist = [550]

fitlist = ["MTonly", "MTandMT2", "MTandMT2_MJJ"]

dimensions = 2

indir = '/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p1/linear'
outdir = '/afs/cern.ch/user/d/daebi/public/diHiggs/CMSSW_8_1_0/src/HiggsAnalysis-CombinedLimit/autoMCtest/2D_HMEv4_1p15_dnn_0p1/linear'

os.system("mkdir -p {outdir}/plots/".format(outdir = outdir))
for fit in fitlist:
  os.system("mkdir -p {outdir}/plots/{fit}".format(outdir = outdir, fit = fit))
  for mass in masslist:
    os.system("mkdir -p {outdir}/plots/{fit}/{m}".format(outdir = outdir, m = mass, fit = fit))

    f = ROOT.TFile.Open(indir+"/linear_{fit}_M{m}.root".format(m = mass, fit = fit))

    signal = "RadionM{m}".format(m = mass)

    for channel in channellist:
      legend = ROOT.TLegend(0.74,0.62,0.84,0.65+len(bgtypes)*.04)
      legend.SetTextSize(0.045)
      legend.SetTextFont(42)
      legend.SetBorderSize(0)
      legend2 = ROOT.TLegend(0.45,0.75,0.67,0.78+2*.05)
      legend2.SetTextSize(0.045)
      legend2.SetTextFont(42)
      legend2.SetBorderSize(0)

      stack = ROOT.THStack("bgs_"+channel, "")
      for i in range(len(bgtypes)):
        if bgtypes[i] == "DY" and (channel == "MuMu" or channel == "ElEl"):
          data_un = f.Get("data_untagged_"+channel)
          TT_un = f.Get("TT_untagged_"+channel)
          sT_un = f.Get("sT_untagged_"+channel)
          xBins = data_un.GetNbinsX()
          h = ROOT.TH1F("h", "h", xBins, data_un.GetXaxis().GetXmin(), data_un.GetXaxis().GetXmax()) 
          for bins in range(xBins):
            h.SetBinContent(bins, data_un.GetBinContent(bins) - TT_un.GetBinContent(bins) - sT_un.GetBinContent(bins))
        else:
          h = f.Get(bgtypes[i]+"_"+channel)
        h.SetFillColor(colorlist[i])
        h.SetLineColor(colorlist[i])
        stack.Add(h)
        legend.AddEntry(h, bgtypes[i], "f")
        del h

      h_data = f.Get("data_obs_"+channel+"_M{m}".format(m = mass))
      h_data.SetMarkerStyle(20)
      h_data.SetMarkerColor(1)
      h_data.SetLineColor(1)
      h_data_blind = ROOT.TH1F("hdata", "hdata", h_data.GetNbinsX(), h_data.GetXaxis().GetXmin(), h_data.GetXaxis().GetXmax())
      for bins in range(h_data.GetNbinsX()):
        if dimensions == 1:
          if 3.0*(bins)/(h_data.GetNbinsX()) >= 1.6 and 3.0*(bins)/(h_data.GetNbinsX()) <= 2.0:
            continue
          else:
            h_data_blind.SetBinContent(bins, h_data.GetBinContent(bins))
            h_data_blind.SetBinError(bins, h_data.GetBinError(bins))
        if dimensions == 2:
          if 3.0*(bins%(h_data.GetNbinsX()/11.0))/(h_data.GetNbinsX()/11.0) >= 1.6 and 3.0*(bins%(h_data.GetNbinsX()/11.0))/(h_data.GetNbinsX()/11.0) <= 2.0:
            continue
          else:
            h_data_blind.SetBinContent(bins, h_data.GetBinContent(bins))
            h_data_blind.SetBinError(bins, h_data.GetBinError(bins))

      h_data_blind.SetMarkerStyle(20)
      h_data_blind.SetMarkerColor(1)
      h_data_blind.SetLineColor(1)
      legend2.AddEntry(h_data, "Data", "p")
      h_bg_all = f.Get("bg_all_"+channel+"_M{m}".format(m = mass))
      h_bg_all.SetLineColor(0)
      h_bg_all.SetFillStyle(3244)
      h_bg_all.SetFillColor(14)
      h_signal = f.Get(signal+"_"+channel)
      h_signal.SetLineColor(colorlist[-1])
      h_signal.SetLineWidth(2)
      legend2.AddEntry(h_signal, "Signal M{m}".format(m = mass), "l")


      hratio_framework = h_data.Clone()
      hratio_framework.SetName("hratio_framework")
      hratio = h_data.Clone()
      hratio.SetName("ratio")
      hratio.SetMarkerStyle(20)
      hratio.SetMarkerColor(1)
      h_errorband = h_data.Clone()
      h_errorband.SetName("errband")
      h_errorband.SetFillStyle(3244)
      h_errorband.SetFillColor(14)
      h_errorband.SetMarkerColor(0)
      h_errorband.SetMarkerSize(0)
      hratio.Divide(h_bg_all)

      for i in range(hratio.GetNbinsX()):
        value_den = h_bg_all.GetBinContent(i+1)
        err_den = h_bg_all.GetBinError(i+1)
        value_num = h_data.GetBinContent(i+1)
        err_num = h_data.GetBinError(i+1)
        ratio = hratio.GetBinContent(i+1)

        h_errorband.SetBinContent(i+1, 1.0)
        if abs(value_den) > 0.0:
          h_errorband.SetBinError(i+1, 1.0*err_den/value_den)
        else:
          h_errorband.SetBinError(i+1, 0.0)

        if abs(value_num) > 0.0:
          hratio.SetBinError(i+1, ratio*err_num/value_num)
        else:
          hratio.SetBinError(i+1, 0.0)

        hratio_framework.SetBinContent(i+1, -1.0)

      h_errorband.SetStats(0)
      hratio.SetStats(0)
      hratio_framework.SetStats(0)

      hratio_blind = ROOT.TH1F("hratio", "hratio", hratio.GetNbinsX(), hratio.GetXaxis().GetXmin(), hratio.GetXaxis().GetXmax())
      for bins in range(hratio.GetNbinsX()):
        if dimensions == 1:
          if 3.0*(bins)/(hratio.GetNbinsX()) >= 1.6 and 3.0*(bins)/(hratio.GetNbinsX()) <= 2.0:
            continue
          else:
            hratio_blind.SetBinContent(bins, hratio.GetBinContent(bins))
            hratio_blind.SetBinError(bins, hratio.GetBinError(bins))
        if dimensions == 2:
          if 3.0*(bins%(hratio.GetNbinsX()/11.0))/(hratio.GetNbinsX()/11.0) >= 1.6 and 3.0*(bins%(hratio.GetNbinsX()/11.0))/(hratio.GetNbinsX()/11.0) <= 2.0:
            continue
          else:
            hratio_blind.SetBinContent(bins, hratio.GetBinContent(bins))
            hratio_blind.SetBinError(bins, hratio.GetBinError(bins))

      hratio_blind.SetName("ratio")
      hratio_blind.SetMarkerStyle(20)
      hratio_blind.SetMarkerColor(1)

      deltaY = 0.49
      hratio_framework.SetTitle("")
      hratio_framework.SetMaximum(1.0 + deltaY)
      hratio_framework.SetMinimum(1.0 - deltaY)

      hrYaxis = hratio_framework.GetYaxis()
      hrXaxis = hratio_framework.GetXaxis()
      hrXaxis.SetTitle("DNN output")
      hrXaxis.SetTitleSize(35)
      hrXaxis.SetTitleFont(43)
      hrXaxis.SetTitleOffset(3.0)
      hrXaxis.SetLabelSize(30)
      hrXaxis.SetLabelFont(43)
      hrYaxis.SetTitle("Data/MC")
      hrYaxis.SetNdivisions(505)
      hrYaxis.CenterTitle()
      hrYaxis.SetTitleSize(25)
      hrYaxis.SetTitleFont(43)
      hrYaxis.SetTitleOffset(1.3)
      hrYaxis.SetLabelSize(25)
      hrYaxis.SetLabelFont(43)



      ROOT.gStyle.SetPadLeftMargin(0.13)
      c1 = ROOT.TCanvas("c1", "c1", 1600, 800)
      c1.Clear()
      pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
      pad1.SetBottomMargin(.02)
      pad1.Draw()
      pad1.cd()
      stack.Draw("hist")
      h_bg_all.Draw("e2same")
      h_signal.Draw("samehist")
      #h_data.Draw("epsame")
      h_data_blind.Draw("epsame")
      pad1.SetLogy()
      legend.Draw("same")
      legend2.Draw("same")

      if channel == "ElEl":
        ch = "e e"
      elif channel == "MuMu":
        ch = "#mu #mu"
      else:
        ch = "#mu e"
      tex1 = ROOT.TLatex(0.17,0.8, "{ch} channel".format(ch = ch))
      tex1.SetNDC()
      tex1.SetTextSize(.045)
      tex1.Draw("same")

      tex0 = ROOT.TLatex(0.1,0.92, " #scale[1.4]{#font[61]{CMS}} Internal"+"  "*16+"35.87 fb^{-1} (13 TeV),2016")
      tex0.SetNDC(); tex0.SetTextSize(.045); tex0.SetTextFont(62)
      tex0.Draw("same")

      stackYaxis = stack.GetHistogram().GetYaxis()
      stackXaxis = stack.GetHistogram().GetXaxis()
      for i in range(stack.GetHistogram().GetNbinsX()):
        stackXaxis.SetBinLabel(i+1, "")
      stackYaxis.SetTitle("Events")
      stackYaxis.SetTitleSize(.05)
      stackYaxis.SetLabelFont(42)
      stackYaxis.SetLabelSize(.045)
      stackYaxis.SetTitleOffset(1.1)
      stack.SetMaximum(10000)

      c1.cd()
      #c1.Update()

      pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, .29)
      pad2.SetTopMargin(0.0)
      pad2.SetBottomMargin(.35)
      pad2.SetTicks(1,1)
      pad2.SetGridy()
      pad2.Draw()
      pad2.cd()
      hratio_framework.Draw()
      h_errorband.Draw("e2same")
      #hratio.Draw("psame")
      hratio_blind.Draw("psame")


      c1.SetTitle(channel+" channel")
      c1.SaveAs(outdir+"/plots/{fit}/{m}/{ch}_M{m}.pdf".format(ch = channel, m = mass, fit = fit))
      del c1



