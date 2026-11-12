#!/usr/bin/env python3
"""v17: +13 grade-pure biology numericals (bio12 had 10, bio11 14). Idempotent; appends ids to packs/pack_specs.json[bio11|bio12].numeric
and updates engine/param_templates.json + docs/model/templates.json. Unit names are the real syllabus_graph unit names."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_bio_templates import T, R

B12 = [
    T("bio_dna_len", "Genetics", ["dna", "base", "pairs", "length", "helix"], ["bp=[10,100,1000,5000,10000]"],
      r"A DNA segment contains $@bp@$ base pairs. If the rise per base pair is $0.34\ \text{nm}$, what is its length in nm?", "bp*0.34", ["bp*3.4", "bp*0.034", "bp/0.34", "bp*0.34*2"],
      r"In B-DNA the rise per base pair is $0.34\ \text{nm}$.", "the length of a DNA segment", [r"$L = @bp@\times 0.34$", r"$L = @ans@\ \text{nm}$"], u=r"\text{nm}"),
    T("bio_codon_aa", "Genetics", ["codon", "mrna", "amino", "translation", "triplet"], ["n=[30,60,90,150,300,900]"],
      r"A coding region of mRNA (start codon to the last sense codon, stop codon excluded) has $@n@$ nucleotides. How many amino acids does the polypeptide contain?",
      "n/3", ["n", "n*3", "n/3+1", "n/2"], r"The genetic code is a triplet code: three nucleotides specify one amino acid.", "the triplet nature of the genetic code",
      [r"Amino acids $= \dfrac{@n@}{3}$", r"Amino acids $= @ans@$"]),
    T("bio_f2_dom", "Genetics", ["monohybrid", "dominant", "phenotype", "offspring", "f2"], ["N=[80,120,160,200,400]"],
      r"A monohybrid cross $Aa \times Aa$ produces $@N@$ offspring. How many are expected to show the dominant phenotype?", "3*N/4", ["N/4", "N/2", "3*N/16", "N"],
      r"The F2 phenotypic ratio of a monohybrid cross is $3:1$, so $\dfrac34$ show the dominant trait.", "the monohybrid phenotypic ratio", [r"$\dfrac{3}{4}\times @N@$", r"Dominant offspring $= @ans@$"]),
    T("bio_transform_eff", "Biotechnology", ["transformation", "efficiency", "colonies", "plasmid", "dna"], ["c=[200,300,600,1200]", "d=[0.1,0.2,0.5,2]"],
      r"After transformation with $@d@\ \mu\text{g}$ of plasmid DNA, $@c@$ colonies grow on the selective plate. What is the transformation efficiency (colonies per $\mu\text{g}$)?",
      "c/d", ["c*d", "d/c", "c+d", "c/(d*10)"], r"Transformation efficiency $=$ number of transformants $/$ amount of DNA used (in $\mu\text{g}$).", "transformation efficiency",
      [r"$\dfrac{@c@}{@d@}$", r"Efficiency $= @ans@\ \text{colonies}/\mu\text{g}$"], u=r"\text{colonies}/\mu\text{g}"),
    T("bio_rq", "Plant Physiology", ["respiratory", "quotient", "carbon", "dioxide", "oxygen"], ["co=[6,8,10,12,14]", "o2=[6,8,10,12,14]"],
      r"A germinating seed releases $@co@\ \text{mL}$ of $\text{CO}_2$ and consumes $@o2@\ \text{mL}$ of $\text{O}_2$. Calculate its respiratory quotient.", "co/o2", ["o2/co", "co*o2", "co-o2", "co+o2"],
      r"$\text{RQ} = \dfrac{\text{volume of CO}_2\text{ released}}{\text{volume of O}_2\text{ consumed}}$.", "the respiratory quotient", [r"$\text{RQ} = \dfrac{@co@}{@o2@}$", r"$\text{RQ} = @ans@$"], cond="co!=o2 and ans>0.3"),
    T("bio_cleavage", "Embryology", ["cleavage", "blastomere", "zygote", "divisions", "cells"], ["n=[2,3,4,5,6]"],
      r"A zygote undergoes $@n@$ successive cleavage divisions. How many blastomeres are present?", "2**n", ["2*n", "n**2", "2**(n-1)", "2**n-1"],
      r"Each cleavage division doubles the number of cells, so $n$ divisions give $2^n$ blastomeres.", "cleavage doubling", [r"Blastomeres $= 2^{@n@}$", r"Blastomeres $= @ans@$"]),
    T("bio_map_pressure", "Human Biology", ["blood", "pressure", "systolic", "diastolic", "mean"], ["s=[110,120,130,140]", "d=[60,70,80,90]"],
      r"A person has a systolic pressure of $@s@\ \text{mm Hg}$ and a diastolic pressure of $@d@\ \text{mm Hg}$. Find the pulse pressure.", "s-d", ["s+d", "(s+d)/2", "s/d", "d-s"],
      r"Pulse pressure $=$ systolic pressure $-$ diastolic pressure.", "the pulse pressure", [r"$@s@ - @d@$", r"Pulse pressure $= @ans@\ \text{mm Hg}$"], u=r"\text{mm Hg}"),
    T("bio_bmi", "Human Population and Health Disorders", ["bmi", "body", "mass", "index", "obesity"], ["m=[50,60,70,80,90]", "h=[1.5,1.6,1.7,1.8]"],
      r"A person has a mass of $@m@\ \text{kg}$ and a height of $@h@\ \text{m}$. Calculate the body mass index (BMI).", "m/h**2", ["m/h", "m*h", "m/(2*h)", "m*h**2"],
      r"$\text{BMI} = \dfrac{\text{mass (kg)}}{\text{height (m)}^2}$.", "the body mass index", [r"$\text{BMI} = \dfrac{@m@}{(@h@)^2}$", r"$\text{BMI} = @ans@\ \text{kg m}^{-2}$"], u=r"\text{kg m}^{-2}"),
    T("bio_doubling", "Human Population and Health Disorders", ["population", "doubling", "growth", "rate", "seventy"], ["r=[1,2,2.5,3.5,5,7]"],
      r"A population grows at $@r@\%$ per year. Using the rule of 70, estimate its doubling time in years.", "70/r", ["r/70", "70*r", "100/r+1", "35/r"],
      r"Doubling time $\approx \dfrac{70}{\text{growth rate in } \%}$.", "the rule of 70", [r"$t_d \approx \dfrac{70}{@r@}$", r"$t_d \approx @ans@\ \text{years}$"], u=r"\text{years}"),
]
B11 = [
    T("bio_ten_pct", "Ecology", ["energy", "trophic", "ten", "percent", "pyramid"], ["E=[1000,2000,10000,20000]", "k=[1,2,3]"],
      r"A producer level fixes $@E@\ \text{kJ}$ of energy. By the ten percent law, how much energy reaches the trophic level $@k@$ step(s) above it?", "E*0.1**k", ["E*0.1", "E/k", "E*0.9**k", "E*0.01*k"],
      r"Only about $10\%$ of the energy is passed on at each trophic transfer (Lindeman's ten percent law).", "the ten percent law", [r"$E = @E@\times(0.1)^{@k@}$", r"$E = @ans@\ \text{kJ}$"], u=r"\text{kJ}", cond="ans>=1"),
    T("bio_npp", "Ecology", ["primary", "productivity", "gross", "respiration", "net"], ["g=[800,1200,2000,3500]", "r=[200,300,500,900]"],
      r"A community has a gross primary productivity of $@g@\ \text{kcal m}^{-2}\text{yr}^{-1}$ and plant respiration of $@r@\ \text{kcal m}^{-2}\text{yr}^{-1}$. Find the net primary productivity.", "g-r", ["g+r", "g/r", "r-g", "(g-r)/2"],
      r"$\text{NPP} = \text{GPP} - R$.", "net primary productivity", [r"$\text{NPP} = @g@ - @r@$", r"$\text{NPP} = @ans@\ \text{kcal m}^{-2}\text{yr}^{-1}$"], u=r"\text{kcal m}^{-2}\text{yr}^{-1}"),
    T("bio_lincoln", "Ecology", ["lincoln", "index", "mark", "recapture", "population"], ["M=[20,40,50,100]", "C=[30,40,60,80]", "R=[4,5,8,10]"],
      r"In a mark-recapture study, $@M@$ animals were marked and released. A later sample of $@C@$ contained $@R@$ marked animals. Estimate the population size by the Lincoln index.", "M*C/R", ["M*R/C", "C*R/M", "M+C-R", "M*C*R"],
      r"Lincoln index: $N = \dfrac{M\times C}{R}$.", "the Lincoln index", [r"$N = \dfrac{@M@\times @C@}{@R@}$", r"$N = @ans@$"], cond="M*C%R==0"),
    T("bio_peptide", "Biomolecules and Cell Biology", ["peptide", "bond", "amino", "acids", "protein"], ["n=[3,5,10,20,50,100]"],
      r"A polypeptide chain is made of $@n@$ amino acids. How many peptide bonds does it contain?", "n-1", ["n", "n+1", "2*n", "n/2"],
      r"Joining $n$ amino acids in a single chain forms $n-1$ peptide bonds.", "peptide bond count", [r"Bonds $= @n@ - 1$", r"Bonds $= @ans@$"]),
    T("bio_mitosis_cells", "Biomolecules and Cell Biology", ["mitosis", "cell", "division", "daughter", "cycle"], ["n=[3,4,5,6,8,10]"],
      r"A single cell undergoes $@n@$ successive mitotic divisions. How many cells result?", "2**n", ["2*n", "n**2", "2**(n-1)", "2**n-2"],
      r"Each mitosis doubles the cell number, so $n$ divisions give $2^n$ cells.", "exponential cell division", [r"Cells $= 2^{@n@}$", r"Cells $= @ans@$"]),
]


def apply(path):
    L = json.load(open(path, encoding="utf-8")); mine = {t["id"]: t for t in B11 + B12}; have = {t["id"] for t in L["templates"]}
    L["templates"] = [mine.get(t["id"], t) for t in L["templates"]] + [t for t in mine.values() if t["id"] not in have]
    json.dump(L, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); return len(mine) - len(have & set(mine))


if __name__ == "__main__":
    for p in ("engine/param_templates.json", "docs/model/templates.json"): print(p, "added", apply(os.path.join(R, p)))
    sp = os.path.join(R, "packs", "pack_specs.json"); cur = json.load(open(sp))
    for pid, ts in (("bio11", B11), ("bio12", B12)):
        for t in ts:
            if t["id"] not in cur[pid].setdefault("numeric", []): cur[pid]["numeric"].append(t["id"])
    json.dump(cur, open(sp, "w"), indent=1)
