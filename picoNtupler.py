import ROOT

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()

ROOT.gInterpreter.Declare('''
#include "ROOT/RVec.hxx"
using Vec_t = const ROOT::RVec<float>&;
using Vec_i = const ROOT::RVec<int>&;
float ZInvariantMass(Vec_t pt_1, Vec_t eta_1, Vec_t phi_1, Vec_t mass_1,Vec_t pt_2, Vec_t eta_2, Vec_t phi_2, Vec_t mass_2) {
    const ROOT::Math::PtEtaPhiMVector p1(pt_1[0], eta_1[0], phi_1[0], mass_1[0]);
    const ROOT::Math::PtEtaPhiMVector p2(pt_2[0], eta_2[0], phi_2[0], mass_2[0]);
    return (p1 + p2).M();
}
float deltaR(float eta_1, float eta_2, float phi_1, float phi_2){
   const float deta = eta_1 - eta_2;
   const float dphi = ROOT::Math::VectorUtil::Phi_mpi_pi(phi_1 - phi_2);
   const float dRsq = std::pow(deta,2) + std::pow(dphi,2);

   return sqrt(dRsq);
}
bool PassMuTauFilter(UInt_t ntrig,Vec_i trig_id,Vec_i trig_bits,Vec_t trig_pt,Vec_t trig_eta,Vec_t trig_phi,float tau_pt,float tau_eta,float tau_phi){
   
   for(int it=0; it < ntrig; it++){
     const ROOT::Math::PtEtaPhiMVector trig(trig_pt[it],trig_eta[it],trig_phi[it],0);
     float dR = deltaR(trig.Eta(),tau_eta,trig.Phi(),tau_phi);
     if (dR < 0.5){
      if((trig_bits[it] & 512) != 0 && (trig_bits[it] & 1024) != 0 && trig_id[it] == 15){
           return true;
      }
   }
  }
  return false;
}
bool PassTagFilter(UInt_t ntrig,Vec_i trig_id,Vec_i trig_bits,Vec_t trig_pt,Vec_t trig_eta,Vec_t trig_phi,float tau_pt,float tau_eta,float tau_phi){
   
   for(int it=0; it < ntrig; it++){
     const ROOT::Math::PtEtaPhiMVector trig(trig_pt[it],trig_eta[it],trig_phi[it],0);
     float dR = deltaR(trig.Eta(),tau_eta,trig.Phi(),tau_phi);
     if (dR < 0.5){
      if((trig_bits[it] & 2) != 0 && trig_id[it] == 13){
           return true;
      }
   }
  }
  return false;
}
float LeadingTauPT(Vec_t tau_pt,Vec_t tau_eta,Vec_t tau_phi,Vec_t tau_m){
   const ROOT::Math::PtEtaPhiMVector tau(tau_pt[0],tau_eta[0],tau_phi[0],tau_m[0]);
   return tau.Pt();
}
''')

inputFiles = (f'/eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/anayak/2022NanoAOD/SingleMuonV1/Files2/nano_aod_{i}.root' for i in range(0,79))


df = ROOT.RDataFrame("Events",inputFiles)

# select muon+tau pair
df_mutau =  df.Filter("nMuon == 1 && nTau == 1 && (Muon_charge[0] != Tau_charge[0]) && Muon_pt[0] > 20 && Tau_pt[0] > 20 && deltaR(Muon_eta[0],Tau_eta[0],Muon_phi[0],Tau_phi[0]) > 0.5", "Events with muon-tau pair")

# select taus with DeepTauID 


pass_mutau = "PassMuTauFilter(nTrigObj,TrigObj_id,TrigObj_filterBits,TrigObj_pt,TrigObj_eta,TrigObj_phi,Tau_pt[0],Tau_eta[0],Tau_phi[0]) > 0"
pass_tag   = "PassTagFilter(nTrigObj,TrigObj_id,TrigObj_filterBits,TrigObj_pt,TrigObj_eta,TrigObj_phi,Muon_pt[0],Muon_eta[0],Muon_phi[0]) > 0"
tau_id   = "Tau_idDeepTau2017v2p1VSjet[0] >=16 && Tau_idDeepTau2017v2p1VSmu[0] >=8 && Tau_idDeepTau2017v2p1VSe[0] >=2"


df_pass= df_mutau.Filter(pass_mutau+" && "+tau_id).Define("tau_pt","LeadingTauPT(Tau_pt,Tau_eta,Tau_phi,Tau_mass)")
df_all = df_mutau.Filter(pass_tag+" && "+tau_id).Define("tau_pt","LeadingTauPT(Tau_pt,Tau_eta,Tau_phi,Tau_mass)")

h_num = df_pass.Histo1D(("all_tau_pt","",100,0.25,300),"tau_pt")
h_den = df_all.Histo1D(("all_tau_pt","",100,0.25,300),"tau_pt")
# Request cut-flow report
report = df_pass.Report()

# Produce plot
ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTextFont(42)
c = ROOT.TCanvas("c", "", 800, 700)


gr = ROOT.TEfficiency(h_num.GetPtr(),h_den.GetPtr()) 
gr.SetTitle("")
#gr.GetXaxis().SetTitleSize(0.04)
#gr.GetYaxis().SetTitleSize(0.04)
gr.Draw()
 
label = ROOT.TLatex(); label.SetNDC(True)
label.DrawLatex(0.755, 0.680, "Efficiency")
label.SetTextSize(0.040); label.DrawLatex(0.100, 0.920, "#bf{CMS Run3 Data}")
label.SetTextSize(0.030); label.DrawLatex(0.630, 0.920, "#sqrt{s} = 13.6 TeV, L_{int} = 10 fb^{-1}")
 
c.SaveAs("MuTau.pdf")
 
# Print cut-flow report
report.Print() 
