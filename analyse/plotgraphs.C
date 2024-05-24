#include <iostream>
#include <string>
#include <sstream>

#include <TFile.h>
#include <TEfficiency.h>

// Usage:
//     Plot efficiency VS pt, eta, multiplicity
// root plotgraphs.C("out.root", eff, pt)
// root plotgraphs.C("out.root", eff, eta)
// root plotgraphs.C("out.root", eff, mult)
// root plotgraphs.C("out.root", eff, mult, hits)
// root plotgraphs.C("out.root", eff, mult, charged)

//     Plot duplicate rate VS pt, eta, multiplicity
// root plotgraphs.C("out.root", duplicates, pt)
// root plotgraphs.C("out.root", duplicates, eta)
// root plotgraphs.C("out.root", duplicates, mult)
// root plotgraphs.C("out.root", duplicates, mult, hits)
// root plotgraphs.C("out.root", duplicates, mult, charged)

//     Plot fake rate VS multiplicity
// root plotgraphs.C("out.root", fakes, mult)
// root plotgraphs.C("out.root", fakes, mult, hits)
// root plotgraphs.C("out.root", fakes, mult, charged)

enum GraphType {
  efficiency,
  duplicateRate,
  fakeRate
};

enum GraphArgument {
  pt,
  eta,
  multiplicity
};

constexpr auto eff = GraphType::efficiency;
constexpr auto duplicates = GraphType::duplicateRate;
constexpr auto fakes = GraphType::fakeRate;
constexpr auto mult = GraphArgument::multiplicity;

const std::string PGM = "PGM";
const std::string HCF = "HCF";
const std::string NNS = "NNS";
const std::string PGS = "PGS";
const std::string PWM = "PWM";
const std::string PWS = "PWS";
const std::string RAW = "RAW";

TEfficiency *createTEff(
    std::string name,
    std::string description,
    Int_t nBins,
    Double_t minArgument,
    Double_t maxArgument,
    Int_t lineWidth,
    Color_t color,
    Style_t markerStyle)
{
  auto *eff = new TEfficiency(
      name.c_str(), description.c_str(), nBins, minArgument, maxArgument);

  eff->SetLineColor(color);
  eff->SetMarkerStyle(markerStyle);
  eff->SetMarkerColor(color);
  eff->SetLineWidth(lineWidth);

  return eff;
}

void setYMinMax(TEfficiency *eff, Double_t min, Double_t max) {
  auto graph = eff->GetPaintedGraph();
  if (min >= 0)
    graph->SetMinimum(min);
  if (max >= 0)
    graph->SetMaximum(max);
}

void fill_teff_from_file(
    TEfficiency *eff, Int_t argumentIdx, Int_t valueIdx, std::string fname) {

  std::ifstream fIn(fname);
  if (!fIn.good()) {
    std::cout << "fill_teff_from_file(): Cannot open file " << fname <<
        std::endl;
    return;
  }

  std::string line;

  while (std::getline(fIn, line)) {

    if (line[0] == '#') {
      continue;
    }

    std::istringstream iss(line);
    int i = -1;
    Double_t argument;
    Int_t valueInt;
    Bool_t value;
    Bool_t findArgument = false;
    Bool_t findValue = false;
    while (iss.good()) {
      i++;
      std::string substr;
      getline(iss, substr, ',');

      if (i == argumentIdx) {
        argument = std::stod(substr);
        findArgument = true;
      } else if (i == valueIdx) {
        valueInt = std::stoi(substr);
        value = (valueInt == 1);
      }
    }
    assert(findArgument);
    assert(findValue);

    eff->Fill(value, argument);
  }
}

enum MultType {
  hits,
  charged
};

void plotgraphs(
    std::string outFName,
    GraphType graphType,
    GraphArgument graphArgument,
    MultType multType = charged,
    Bool_t ifRAW = false) {

  Int_t argumentIdx;
  Int_t valueIdx;

  std::string fname_pre;
  std::string yLabel;

  std::string pngPrefix;

  std::string rootNamePrefix;

  Double_t yMin = -1;
  Double_t yMax = -1;

  if (graphType == efficiency) {
    valueIdx = 6;

    fname_pre = "real_tracks_";
    pngPrefix = "efficiency";
    rootNamePrefix = "Efficiency";
    yLabel = "Efficiency";

    yMax = 1;

    if (graphArgument == pt) {
      argumentIdx = 3;
      yMax = 1.02;

//    yMin = 0.35; // for compare chi2 20 30
    } else if (graphArgument == eta) {
      argumentIdx = 4;
      yMin = 0.94;
      yMax = 1;
    } else if (graphArgument == multiplicity) {
      if (multType == hits) {
        argumentIdx = 7;
      } else if (multType == charged) {
        argumentIdx = 5;
      } else {
        std::cout << "Error: wrong multType!" << std::endl;
        return;
      }
      yMin = 0.70;
//    yMax = 0.965;
      yMax = 1.;
    } else {
      std::cout << "Error: wrong graphArgument!" << std::endl;
      return;
    }
  }
  else if (graphType == duplicateRate){
    valueIdx = 3;

    fname_pre = "track_candidates_";
    pngPrefix = "dup";
    rootNamePrefix = "DuplicateRate";
    yLabel = "Duplicate rate";

    yMin = 0;

    if (graphArgument == pt) {
      argumentIdx = 4;
      yMax = 0.3;
      if (ifRAW) {
        yMin = 0;
        yMax = 1;
      }
    } else if (graphArgument == eta) {
      argumentIdx = 5;
      yMax = 0.52;
      if (ifRAW) {
        yMin = 0;
        yMax = 1;
      }
    } else if (graphArgument == multiplicity) {
      if (multType == hits) {
        argumentIdx = 9;
      } else if (multType == charged) {
        argumentIdx = 6;
      } else {
        std::cout << "Error: wrong multType!" << std::endl;
        return;
      }
      //yMax = 0.3;
      yMin =  -0.2;
      yMax =   0.2;
      if (ifRAW) {
        yMin = 0;
        yMax = 1;
      }
    } else {
      std::cout << "Error: wrong graphArgument!" << std::endl;
      return;
    }
  } else if (graphType == fakeRate) {
    valueIdx = 2;

    fname_pre = "track_candidates_";
    pngPrefix = "fakeRate";
    rootNamePrefix = "FakeRate";
    yLabel = "Fake rate";

    yMin = 0;
    yMax = 0.013;

//  yMax = 1;

    std::string error =
        "Error: Fake rate plot can only be built VS multiplicity";

    if (graphArgument == pt) {
      std::cout << error << std::endl;
      return;
    } else if (graphArgument == eta) {
      std::cout << error << std::endl;
      return;
    } else if (graphArgument == multiplicity) {
      if (multType == hits) {
        argumentIdx = 9;
      } else if (multType == charged) {
        argumentIdx = 6;
      } else {
        std::cout << "Error: wrong multType!" << std::endl;
        return;
      }
    } else {
      std::cout << "Error: wrong graphArgument!" << std::endl;
      return;
    }
  }

  Double_t minArgument;
  Double_t maxArgument;
  std::string xLabel;

  std::string pngPostfix;
  std::string rootNamePostfix;

  if (graphArgument == pt) {
    minArgument = 0.1; // 100 MeV
    maxArgument = 3.0; // max = 3.7... ;

    xLabel = "Truth pT [GeV/c]";

    pngPostfix = "pt";
    rootNamePostfix = "pt";

  } else if (graphArgument == eta) {
    minArgument = -1.5;
    maxArgument =  1.5;
    xLabel = "Truth #eta";

    pngPostfix = "eta";
    rootNamePostfix = "eta";

  } else if (graphArgument == multiplicity) {
    minArgument = 100;
    maxArgument = 900;
    xLabel = "Truth multiplicity";

    pngPostfix = "multiplicity";
    if (multType == hits) {
      pngPostfix += "_hits";
    } else if (multType == charged) {
      pngPostfix += "_ch";
    }
    rootNamePostfix = "multiplicity";
  } else {
    assert(0 && "Wrong graphArgument!");
  }

  std::string pngFName = pngPrefix + "_" + pngPostfix + ".png";

  std::cout << "argumentIdx : " << argumentIdx << std::endl;
  std::cout << "valueIdx : " << valueIdx << std::endl;

  Int_t nBins = 31;

  auto *fOut = new TFile(outFName.c_str(), "update");

  auto *canv = new TCanvas("Efficiency", "", 2048, 1496);

  std::cout << "minArgument: " << minArgument << "; " <<
               "maxArgument: " << maxArgument << "; " <<
               "nBins: "       << nBins       <<
               std::endl;

  Int_t lineWidth = 3;
  TEfficiency *teffHCF = createTEff("HCF", "HCF;" + xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kRed, kFullCircle);
  TEfficiency *teffPGM = createTEff("PGM", "PGM;"  + xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kBlue, kFullCircle);
  TEfficiency *teffNNS = createTEff("NNS", "NNS;" + xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kCyan, kFullSquare);
  TEfficiency *teffPGS = createTEff("PGS", "PGS;" + xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kGreen, kFullSquare);
  TEfficiency *teffPWM = createTEff("PWM", "PWM;" + xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kMagenta, kFullSquare);
  TEfficiency *teffPWS = createTEff("PWS", "PWS;" + xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kGreen - 2, kFullSquare);
  TEfficiency *teffRAW = createTEff("RAW", "RAW;"+ xLabel + ";" + yLabel,
      nBins, minArgument, maxArgument, lineWidth, kBlack, kFullSquare);

  fill_teff_from_file(teffPGM, argumentIdx, valueIdx, fname_pre + PGM + ".txt");
  fill_teff_from_file(teffHCF, argumentIdx, valueIdx, fname_pre + HCF + ".txt");
  fill_teff_from_file(teffNNS, argumentIdx, valueIdx, fname_pre + NNS + ".txt");
  fill_teff_from_file(teffPGS, argumentIdx, valueIdx, fname_pre + PGS + ".txt");
  fill_teff_from_file(teffPWM, argumentIdx, valueIdx, fname_pre + PWM + ".txt");
  fill_teff_from_file(teffPWS, argumentIdx, valueIdx, fname_pre + PWS + ".txt");
  fill_teff_from_file(teffRAW, argumentIdx, valueIdx, fname_pre + RAW + ".txt");

  teffPGM->Draw("");
  teffNNS->Draw("same");
  teffPGS->Draw("same");
  teffPWM->Draw("same");
  teffPWS->Draw("same");
  if (ifRAW) {
    teffRAW->Draw("same");
  }
  teffHCF->Draw("same");

  gPad->BuildLegend();

  gPad->Update();

  setYMinMax(teffPGM, yMin, yMax);
  setYMinMax(teffNNS, yMin, yMax);
  setYMinMax(teffPGS, yMin, yMax);
  setYMinMax(teffPWM, yMin, yMax);
  setYMinMax(teffPWS, yMin, yMax);
  setYMinMax(teffHCF, yMin, yMax);

  gPad->Update();

  canv->Print(pngFName.c_str());

  std::string rootName = rootNamePrefix + "_" + rootNamePostfix + "_";

  fOut->WriteObject(teffPGM, (rootName + "PGM").c_str());
  fOut->WriteObject(teffNNS, (rootName + "NNS").c_str());
  fOut->WriteObject(teffPGS, (rootName + "PGS").c_str());
  fOut->WriteObject(teffPWM, (rootName + "PWM").c_str());
  fOut->WriteObject(teffPWS, (rootName + "PWS").c_str());
  fOut->WriteObject(teffHCF, (rootName + "HCF").c_str());
  fOut->WriteObject(teffRAW, (rootName + "RAW").c_str());
}
