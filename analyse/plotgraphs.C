#include <iostream>
#include <string>
#include <sstream>

#include <TFile.h>
#include <TEfficiency.h>

// Usage:
//     Plot efficiency VS pt, eta, multiplicity
// root plotgraphs.C("out.root", "", eff, pt)
// root plotgraphs.C("out.root", "", eff, eta)
// root plotgraphs.C("out.root", "", eff, mult)
// root plotgraphs.C("out.root", "", eff, mult, hits)
// root plotgraphs.C("out.root", "", eff, mult, charged)

//     Plot duplicate rate VS pt, eta, multiplicity
// root plotgraphs.C("out.root", "", duplicates, pt)
// root plotgraphs.C("out.root", "", duplicates, eta)
// root plotgraphs.C("out.root", "", duplicates, mult)
// root plotgraphs.C("out.root", "", duplicates, mult, hits)
// root plotgraphs.C("out.root", "", duplicates, mult, charged)

//     Plot fake rate VS multiplicity
// root plotgraphs.C("out.root", "", fakes, mult)
// root plotgraphs.C("out.root", "", fakes, mult, hits)
// root plotgraphs.C("out.root", "", fakes, mult, charged)

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
    Double_t minArg,
    Double_t maxArg,
    Int_t lineWidth,
    Color_t color,
    Style_t markerStyle)
{
  auto *eff = new TEfficiency(
      name.c_str(), description.c_str(), nBins, minArg, maxArg);

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
    TEfficiency *eff, Int_t argIdx, Int_t valueIdx, std::string fname,
    Bool_t selectorEnabled, Int_t ptArgIdx, Int_t etaArgIdx, Int_t selectedIdx,
    Double_t selPtMin = 0, Double_t selEtaMax = 0) {

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
    Double_t absEta;
    Double_t pt;
    std::string selectedStr;
    Bool_t selected = true;

    Int_t valueInt;
    Bool_t value;
    Bool_t findArgument = false;
    Bool_t findValue = false;
    Bool_t findPt = false;
    Bool_t findEta = false;

    while (iss.good()) {
      i++;
      std::string substr;
      getline(iss, substr, ',');

      if (i == argIdx) {
        argument = std::stod(substr);
        findArgument = true;
      } else if (i == valueIdx) {
        valueInt = std::stoi(substr);
        value = (valueInt == 1);
      }
      if (i == ptArgIdx) {
        pt = std::stod(substr);
        findPt = true;
      } else if (i == etaArgIdx) {
        absEta = fabs(std::stod(substr));
        findEta = true;
      } else if (i == selectedIdx) {
        selectedStr = substr;
        if (selectedStr == "True") {
          selected = 1;
        } else if (selectedStr == "False") {
          selected = 0;
        } else if (selectedStr == "None") {
          selected = 1;
        } else {
            std::cout << "selected: actual: " << selectedStr << ", " <<
                         "expected [True, False, None]" << std::endl;
            assert(0);
        }
      }
    }
    assert(findArgument);
    assert(findValue);
    assert(findPt);
    assert(findEta);

    // Corresponding trackId does not exist, i.e. for fake track-candidates
    Bool_t unknPt  = (pt < 0.)      ? true : false;
    Bool_t unknEta = (absEta > 100) ? true : false;

    if (!selected) {
      continue;
    }
    if (!selectorEnabled ||
        selectorEnabled && (pt > selPtMin) && (absEta < selEtaMax ) ||
        selectorEnabled && unknPt && unknEta) {
      eff->Fill(value, argument);
    }
  }
}

enum MultType {
  hits,
  charged
};

void plotgraphs(
    std::string inputDir,
    std::string outputDir,
    std::string pngPostfix,
    GraphType graphType,
    GraphArgument graphArgument,
    MultType multType = charged,
    Bool_t ifRAW = false) {

  Int_t argIdx;
  Int_t ptArgIdx;
  Int_t etaArgIdx;

  Int_t valueIdx;
  Int_t selectedIdx;

  std::string fname_pre = inputDir + "/";
  std::string pngPrefix;
  std::string rootNamePrefix;

  std::string yLabel;

  Double_t yMin = -1;
  Double_t yMax = -1;

  if (graphType == efficiency) {
    valueIdx = 6;
    selectedIdx = -1;

    fname_pre += "real_tracks_";
    pngPrefix = "efficiency";
    rootNamePrefix = "Efficiency";
    yLabel = "Efficiency";

    yMax = 1;

    ptArgIdx = 3;
    etaArgIdx = 4;

    if (graphArgument == pt) {
      argIdx = ptArgIdx;
      yMax = 1.02;

//    yMin = 0.35; // for compare chi2 20 30
    } else if (graphArgument == eta) {
      argIdx = etaArgIdx;
      yMin = 0.94;
      yMax = 1;
    } else if (graphArgument == multiplicity) {
      if (multType == hits) {
        argIdx = 7;
      } else if (multType == charged) {
        argIdx = 5;
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
    selectedIdx = 7;

    fname_pre += "track_candidates_";
    pngPrefix = "dup";
    rootNamePrefix = "DuplicateRate";
    yLabel = "Duplicate rate";

    yMin = 0;

    ptArgIdx = 4;
    etaArgIdx = 5;

    if (graphArgument == pt) {
      argIdx = ptArgIdx;
      yMax = 0.3;
      if (ifRAW) {
        yMin = 0;
        yMax = 1;
      }
    } else if (graphArgument == eta) {
      argIdx = etaArgIdx;
      yMax = 0.52;
      if (ifRAW) {
        yMin = 0;
        yMax = 1;
      }
    } else if (graphArgument == multiplicity) {
      if (multType == hits) {
        argIdx = 9;
      } else if (multType == charged) {
        argIdx = 6;
      } else {
        std::cout << "Error: wrong multType!" << std::endl;
        return;
      }
      yMin =    0.;
      yMax =   0.4;
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
    selectedIdx = 7;

    fname_pre += "track_candidates_";
    pngPrefix = "fakeRate";
    rootNamePrefix = "FakeRate";
    yLabel = "Fake rate";

    yMin = 0;
    yMax = 0.025;

//  yMax = 1;

    ptArgIdx = 4;
    etaArgIdx = 5;

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
        argIdx = 9;
      } else if (multType == charged) {
        argIdx = 6;
      } else {
        std::cout << "Error: wrong multType!" << std::endl;
        return;
      }
    } else {
      std::cout << "Error: wrong graphArgument!" << std::endl;
      return;
    }
  }

  Double_t minArg;
  Double_t maxArg;
  std::string xLabel;

  std::string rootNamePostfix;

  if (graphArgument == pt) {
    minArg = 0.1; // 100 MeV
    maxArg = 3.0; // max = 3.7... ;

    xLabel = "Truth pT [GeV/c]";

    pngPostfix = "pt" + pngPostfix;
    rootNamePostfix = "pt";

  } else if (graphArgument == eta) {
    minArg = -1.2;
    maxArg =  1.2;
    xLabel = "Truth #eta";

    pngPostfix = "eta" + pngPostfix;
    rootNamePostfix = "eta";

  } else if (graphArgument == multiplicity) {
    minArg = 0;
    maxArg = 900;
    xLabel = "Truth multiplicity";

    std::string postfix = "multiplicity";
    if (multType == hits) {
      postfix += "_hits";
    } else if (multType == charged) {
      postfix += "_ch";
    }
    pngPostfix = postfix + pngPostfix;
    rootNamePostfix = "multiplicity";
  } else {
    assert(0 && "Wrong graphArgument!");
  }

  std::string pngFName = outputDir + "/"+ pngPrefix + "_" + pngPostfix + ".png";

  std::cout << "argIdx : " << argIdx << std::endl;
  std::cout << "valueIdx : " << valueIdx << std::endl;

  Int_t nBins = 31;

  std::string rootFname = outputDir + "/graphs.root";
  auto *fOut = new TFile(rootFname.c_str(), "update");

  auto *canv = new TCanvas("Efficiency", "", 2048, 1496);

  std::cout << "minArg: " << minArg << "; " <<
               "maxArg: " << maxArg << "; " <<
               "nBins: "       << nBins       <<
               std::endl;

  Int_t lineWidth = 3;
  TEfficiency *teffHCF = createTEff("HCF", "HCF;" + xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kRed, kFullCircle);
  TEfficiency *teffPGM = createTEff("PGM", "PGM;"  + xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kBlue, kFullCircle);
  TEfficiency *teffNNS = createTEff("NNS", "NNS;" + xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kCyan, kFullSquare);
  TEfficiency *teffPGS = createTEff("PGS", "PGS;" + xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kGreen, kFullSquare);
  TEfficiency *teffPWM = createTEff("PWM", "PWM;" + xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kMagenta, kFullSquare);
  TEfficiency *teffPWS = createTEff("PWS", "PWS;" + xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kGreen - 2, kFullSquare);
  TEfficiency *teffRAW = createTEff("RAW", "RAW;"+ xLabel + ";" + yLabel,
      nBins, minArg, maxArg, lineWidth, kBlack, kFullSquare);

  // Selector options
  Bool_t selectorEnabled = true;
  Double_t selPtMin = 0.1;
  Double_t selEtaMax = 1.5;

  fill_teff_from_file(teffPGM, argIdx, valueIdx,
      fname_pre + PGM + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);
  fill_teff_from_file(teffHCF, argIdx, valueIdx,
      fname_pre + HCF + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);
  fill_teff_from_file(teffNNS, argIdx, valueIdx,
      fname_pre + NNS + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);
  fill_teff_from_file(teffPGS, argIdx, valueIdx,
      fname_pre + PGS + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);
  fill_teff_from_file(teffPWM, argIdx, valueIdx,
      fname_pre + PWM + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);
  fill_teff_from_file(teffPWS, argIdx, valueIdx,
      fname_pre + PWS + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);
  fill_teff_from_file(teffRAW, argIdx, valueIdx,
      fname_pre + RAW + ".txt", selectorEnabled,
      ptArgIdx, etaArgIdx, selectedIdx, selPtMin, selEtaMax);

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
