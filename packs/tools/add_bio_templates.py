#!/usr/bin/env python3
"""v13: grade-pure BIOLOGY numeric templates for the parametric engine (bio11 / bio12 had 0 numeric templates).
Every answer is computed from a standard formula in the NEB Class 11/12 syllabus; distractors come from typical student mistakes.
Idempotent: appends domain 'biology' + templates to engine/param_templates.json and docs/model/templates.json.
Unit names equal the real syllabus_graph unit names so assign_templates.py binds each template only to the pack that teaches it."""
import json, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
Q = lambda s: s  # raw strings keep LaTeX backslashes intact


def T(id, unit, kw, vars_, stem, ans, wrong, law, lawname, sol, u="", sig=3, cond="ans>0", derived=""):
    return dict(id=id, dom="biology", lv="H", unit=unit, kw=kw, vars=vars_, derived=derived, stem=stem, ans=ans, u=u, wrong=wrong,
                law=law, lawname=lawname, sol=sol, sig=sig, cond=cond)


B11 = [
    T("bio_magnif", "Introduction to Biology", ["microscope", "magnification"], ["obj=[4,10,40,100]", "eye=[5,10,15]"],
      r"A compound microscope has an objective lens of $@obj@\times$ and an eyepiece of $@eye@\times$. What is the total magnification?",
      "obj*eye", ["obj+eye", "obj*eye*10", "obj*eye/10", "obj*eye*2"], r"Total magnification equals the objective magnification multiplied by the eyepiece magnification.",
      "the total magnification of a compound microscope", [r"$M = M_{obj}\times M_{eye} = @obj@\times @eye@$", r"$M = @ans@\times$"], u=r"\times"),
    T("bio_actual_size", "Introduction to Biology", ["microscope", "magnification", "cell"], ["img=[10,15,20,25,30,40]", "M=[100,200,400,500,1000]"],
      r"A cell measures $@img@\ \text{mm}$ in a drawing made at a magnification of $@M@\times$. What is its actual length in micrometres?",
      "img*1000/M", ["img/M", "img*M/1000", "img*100/M", "img*M"], r"Actual size = image size / magnification, and $1\ \text{mm} = 1000\ \mu\text{m}$.",
      "the relation between image size, actual size and magnification", [r"Actual size $= \dfrac{@img@\ \text{mm}}{@M@} = \dfrac{@img@\times 1000\ \mu\text{m}}{@M@}$", r"Actual size $= @ans@\ \mu\text{m}$"],
      u=r"\mu\text{m}", cond="ans>=1"),
    T("bio_surf_vol", "Biomolecules and Cell Biology", ["cell", "surface", "volume"], ["l=[1,2,3,5,10]"],
      r"A cuboidal cell has a side length of $@l@\ \mu\text{m}$. What is its surface area to volume ratio?",
      "6/l", ["6*l", "l/6", "1/l", "6*l*l"], r"For a cube of side $l$, surface area $=6l^2$ and volume $=l^3$, so SA:V $= 6/l$.",
      "the surface area to volume ratio of a cube", [r"SA $= 6l^2$, $V = l^3$", r"SA:V $= \dfrac{6}{@l@} = @ans@\ \mu\text{m}^{-1}$"], u=r"\mu\text{m}^{-1}"),
    T("bio_gamete_chr", "Biomolecules and Cell Biology", ["meiosis", "chromosome", "gamete"], ["n2=[8,14,20,24,46]"],
      r"An organism has $2n = @n2@$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?",
      "n2/2", ["n2", "n2*2", "n2/4"], r"Meiosis halves the chromosome number, so a gamete is haploid ($n$).", "the chromosome number of a gamete",
      [r"$n = \dfrac{2n}{2} = \dfrac{@n2@}{2}$", r"$n = @ans@$"]),
    T("bio_gamete_comb", "Biomolecules and Cell Biology", ["meiosis", "chromosome", "gamete"], ["n2=[6,8,10,12,14]"],
      r"A diploid cell has $2n = @n2@$ chromosomes. How many different chromosome combinations can its gametes carry through independent assortment (no crossing over)?",
      "2**(n2/2)", ["n2**2", "(n2/2)**2", "2*n2", "n2/2"], r"Independent assortment of $n$ chromosome pairs gives $2^n$ gamete combinations.",
      "the number of gamete combinations from independent assortment", [r"$n = \dfrac{@n2@}{2}$ pairs", r"Combinations $= 2^n = @ans@$"]),
    T("bio_hw_het", "Evolutionary Biology", ["hardy", "weinberg", "allele"], ["q=[0.1,0.2,0.3,0.4,0.5]"],
      r"In a population in Hardy-Weinberg equilibrium the frequency of the recessive allele $a$ is $q = @q@$. What is the expected frequency of heterozygous ($Aa$) individuals?",
      "2*q*(1-q)", ["q*q", "(1-q)**2", "2*q", "q*(1-q)"], r"Hardy-Weinberg: $p^2 + 2pq + q^2 = 1$ with $p = 1-q$; heterozygotes occur at $2pq$.",
      "the Hardy-Weinberg principle", [r"$p = 1 - q = 1 - @q@$", r"$2pq = 2\times p\times @q@ = @ans@$"]),
    T("bio_hw_rec_count", "Evolutionary Biology", ["hardy", "weinberg", "recessive"], ["q=[0.1,0.2,0.3,0.4]", "N=[200,500,1000,2000]"],
      r"In a Hardy-Weinberg population of $@N@$ individuals the frequency of the recessive allele is $q = @q@$. How many individuals are expected to show the recessive phenotype ($aa$)?",
      "q*q*N", ["2*q*(1-q)*N", "q*N", "(1-q)**2*N"], r"The recessive phenotype is the genotype $aa$, with frequency $q^2$.",
      "the Hardy-Weinberg principle", [r"$q^2 = @q@^2$", r"Number $= q^2\times @N@ = @ans@$"]),
    T("bio_hw_q", "Evolutionary Biology", ["hardy", "weinberg", "allele"], ["pct=[1,4,9,16,25,36,49]"],
      r"In a Hardy-Weinberg population $@pct@\%$ of individuals show a recessive trait. What is the frequency of the recessive allele $q$?",
      "sqrt(pct/100)", ["pct/100", "1-sqrt(pct/100)", "sqrt(pct/100)/2"], r"The recessive phenotype frequency equals $q^2$, so $q=\sqrt{q^2}$.",
      "the Hardy-Weinberg principle", [r"$q^2 = \dfrac{@pct@}{100}$", r"$q = \sqrt{q^2} = @ans@$"]),
    T("bio_simpson_d", "Ecology", ["simpson", "diversity", "index", "community"], ["n1=[10,20,30,40,50]", "n2=[5,10,15,20,25]", "n3=[5,10,15,20,30]"],
      r"A community has three species with $@n1@$, $@n2@$ and $@n3@$ individuals. Calculate Simpson's index of dominance $D = \dfrac{\sum n(n-1)}{N(N-1)}$.",
      "(n1*(n1-1)+n2*(n2-1)+n3*(n3-1))/(N*(N-1))", ["1-(n1*(n1-1)+n2*(n2-1)+n3*(n3-1))/(N*(N-1))", "(n1*n1+n2*n2+n3*n3)/(N*N)", "(n1*(n1-1)+n2*(n2-1)+n3*(n3-1))/(N*N)"],
      r"Simpson's index of dominance is $D = \sum n(n-1) / N(N-1)$.", "Simpson's index of dominance",
      [r"$N = @n1@ + @n2@ + @n3@ = @N@$", r"$D = @ans@$"], derived="N=n1+n2+n3", cond="ans>0 and ans<1"),
    T("bio_simpson_div", "Ecology", ["simpson", "diversity", "index", "community"], ["n1=[10,20,30,40,50]", "n2=[5,10,15,20,25]", "n3=[5,10,15,20,30]"],
      r"A community has three species with $@n1@$, $@n2@$ and $@n3@$ individuals and Simpson's index of dominance $D = \dfrac{\sum n(n-1)}{N(N-1)}$. Find Simpson's index of diversity ($1-D$).",
      "1-(n1*(n1-1)+n2*(n2-1)+n3*(n3-1))/(N*(N-1))", ["(n1*(n1-1)+n2*(n2-1)+n3*(n3-1))/(N*(N-1))", "1-(n1*n1+n2*n2+n3*n3)/(N*N)", "1/((n1*(n1-1)+n2*(n2-1)+n3*(n3-1))/(N*(N-1)))"],
      r"Simpson's index of diversity is $1-D$ and rises with diversity.", "Simpson's index of diversity",
      [r"$N = @N@$", r"$1-D = @ans@$"], derived="N=n1+n2+n3", cond="ans>0 and ans<1"),
    T("bio_pop_size", "Ecology", ["population", "natality", "mortality", "immigration"], ["N=[500,1000,2000]", "B=[50,100,150,200]", "D=[30,60,90]", "I=[10,20,40]", "E=[5,15,30]"],
      r"A population of $@N@$ individuals has $@B@$ births, $@D@$ deaths, $@I@$ immigrants and $@E@$ emigrants in one year. What is the population size at the end of the year?",
      "N+B-D+I-E", ["N+B-D-I+E", "N+B+D+I+E", "N+B-D", "N-B+D+I-E"], r"$N_{t+1} = N_t + (B + I) - (D + E)$.", "the population size equation",
      [r"$N_{t+1} = @N@ + (@B@ + @I@) - (@D@ + @E@)$", r"$N_{t+1} = @ans@$"], sig=6),
    T("bio_pop_density", "Ecology", ["population", "density", "area"], ["N=[120,240,360,480]", "A=[2,4,6,8]"],
      r"@N@ individuals of a species live in an area of $@A@\ \text{ha}$. Find the population density.",
      "N/A", ["N*A", "N/(A*10)", "A/N"], r"Population density $=$ number of individuals / area.", "population density",
      [r"Density $= \dfrac{@N@}{@A@}$", r"Density $= @ans@\ \text{ha}^{-1}$"], u=r"\text{ha}^{-1}"),
    T("bio_birth_rate", "Ecology", ["population", "natality", "birth"], ["P=[20000,40000,50000,80000]", "B=[600,800,1000,1200,1500]"],
      r"A town of $@P@$ people records $@B@$ births in a year. Find the crude birth rate per 1000 people.",
      "B/P*1000", ["B/P*100", "B/P", "B*P/1000"], r"Crude birth rate $=$ (births / mid-year population) $\times 1000$.", "the crude birth rate",
      [r"CBR $= \dfrac{@B@}{@P@}\times 1000$", r"CBR $= @ans@$ per 1000"], u=r"\text{per 1000}"),
    T("bio_bact_growth", "Introductory Microbiology", ["bacteria", "generation", "growth", "culture"], ["N0=[100,500,1000]", "g=[20,30]", "n=[2,3,4,5]"],
      r"A bacterial culture starts with $@N0@$ cells and the generation time is $@g@\ \text{min}$. How many cells are present after $@t@\ \text{min}$?",
      "N0*2**n", ["N0*2*n", "N0*n**2", "N0*2**(n+1)", "N0*n"], r"Binary fission doubles the number every generation: $N = N_0\times 2^n$.", "exponential bacterial growth",
      [r"$n = \dfrac{@t@}{@g@}$ generations", r"$N = @N0@\times 2^n = @ans@$"], derived="t=g*n", sig=6),
]
B12 = [
    T("bio_chargaff_g", "Genetics", ["chargaff", "dna", "adenine", "guanine"], ["A=[15,20,22,26,28,30,32]"],
      r"In a double-stranded DNA sample adenine makes up $@A@\%$ of the bases. What percentage is guanine?",
      "50-A", ["100-A", "A", "100-2*A"], r"Chargaff's rules: $A = T$ and $G = C$, so $2A + 2G = 100\%$.", "Chargaff's rules",
      [r"$T = A = @A@\%$, so $G + C = 100 - 2\times @A@$", r"$G = \dfrac{100 - 2A}{2} = @ans@\%$"], u=r"\%"),
    T("bio_dna_hbonds", "Genetics", ["dna", "hydrogen", "base", "pairing"], ["at=[20,30,40,50,60]", "gc=[10,20,30,40]"],
      r"A DNA fragment has $@at@$ A-T base pairs and $@gc@$ G-C base pairs. How many hydrogen bonds hold the two strands together?",
      "2*at+3*gc", ["3*at+2*gc", "at+gc", "2*(at+gc)"], r"A-T pairs are joined by 2 hydrogen bonds and G-C pairs by 3.", "base pairing in DNA",
      [r"$2\times @at@ + 3\times @gc@$", r"Total $= @ans@$"]),
    T("bio_mono_f2", "Genetics", ["monohybrid", "cross", "mendel", "dominant"], ["N=[160,240,320,480,640]"],
      r"A monohybrid cross $Tt \times Tt$ produces $@N@$ offspring. How many are expected to show the dominant phenotype?",
      "N*3/4", ["N/4", "N/2", "N*9/16"], r"The F2 phenotypic ratio of a monohybrid cross is $3:1$.", "Mendel's law of segregation",
      [r"Dominant fraction $= \dfrac{3}{4}$", r"Number $= \dfrac{3}{4}\times @N@ = @ans@$"]),
    T("bio_dihybrid", "Genetics", ["dihybrid", "cross", "mendel", "independent"], ["N=[160,320,480,640,800]"],
      r"A dihybrid cross $AaBb \times AaBb$ gives $@N@$ offspring. How many are expected to show both dominant traits?",
      "N*9/16", ["N*3/16", "N/16", "N*3/4"], r"The dihybrid F2 phenotypic ratio is $9:3:3:1$; both dominant traits form $9/16$.", "Mendel's law of independent assortment",
      [r"Double-dominant fraction $= \dfrac{9}{16}$", r"Number $= \dfrac{9}{16}\times @N@ = @ans@$"]),
    T("bio_recomb", "Genetics", ["linkage", "recombination", "crossing", "testcross"], ["rec=[20,30,45,60,90]", "tot=[300,400,500,600,900]"],
      r"A test cross gives $@rec@$ recombinant offspring out of $@tot@$. Find the recombination frequency.",
      "rec/tot*100", ["rec/tot", "(tot-rec)/tot*100", "rec/(tot-rec)*100"], r"Recombination frequency $= \dfrac{\text{recombinants}}{\text{total offspring}}\times 100$.", "recombination frequency",
      [r"$RF = \dfrac{@rec@}{@tot@}\times 100$", r"$RF = @ans@\%$"], u=r"\%", cond="ans>0 and ans<50"),
    T("bio_pcr", "Biotechnology", ["pcr", "polymerase", "amplification", "dna"], ["n=[5,8,10,12,15]"],
      r"A PCR starts with one DNA molecule. How many copies exist after $@n@$ cycles?",
      "2**n", ["2*n", "n**2", "2**(n-1)", "2**(n+1)"], r"Each PCR cycle doubles the DNA, so copies $=2^n$.", "PCR amplification",
      [r"Copies $= 2^{@n@}$", r"Copies $= @ans@$"], sig=6),
    T("bio_cardiac_out", "Human Biology", ["heart", "cardiac", "stroke", "output"], ["HR=[60,70,72,75,80]", "SV=[60,65,70,75,80]"],
      r"A person has a heart rate of $@HR@\ \text{beats min}^{-1}$ and a stroke volume of $@SV@\ \text{mL}$. What is the cardiac output in litres per minute?",
      "HR*SV/1000", ["HR*SV", "HR/SV", "HR*SV/100"], r"Cardiac output $=$ heart rate $\times$ stroke volume.", "cardiac output",
      [r"$CO = @HR@\times @SV@\ \text{mL min}^{-1}$", r"$CO = @ans@\ \text{L min}^{-1}$"], u=r"\text{L min}^{-1}"),
    T("bio_water_pot", "Plant Physiology", ["water", "potential", "osmotic", "pressure"], ["s=[0.6,0.8,1.0,1.2,1.5]", "p=[0.2,0.3,0.4,0.5]"],
      r"A plant cell has a solute potential $\Psi_s = -@s@\ \text{MPa}$ and a pressure potential $\Psi_p = +@p@\ \text{MPa}$. Find its water potential $\Psi_w$.",
      "p-s", ["-(s+p)", "-s", "-(s+2*p)", "2*(p-s)"], r"Water potential $\Psi_w = \Psi_s + \Psi_p$.", "the water potential equation",
      [r"$\Psi_w = -@s@ + @p@$", r"$\Psi_w = @ans@\ \text{MPa}$"], u=r"\text{MPa}", cond="ans<0"),
    T("bio_glycolysis_atp", "Plant Physiology", ["glycolysis", "respiration", "atp", "glucose"], ["g=[2,3,4,5,10]"],
      r"Glycolysis breaks down $@g@$ glucose molecules. What is the net gain of ATP?",
      "2*g", ["4*g", "g", "38*g"], r"Glycolysis yields a net gain of 2 ATP per glucose (4 produced, 2 used).", "the net ATP gain of glycolysis",
      [r"Net ATP $= 2\times @g@$", r"Net ATP $= @ans@$"]),
]


def apply(path):
    L = json.load(open(path, encoding="utf-8")); have = {t["id"] for t in L["templates"]}
    if not any(r[1] == ["biology"] for r in L["domains"]): L["domains"].insert(0, ["^biology$", ["biology"]])
    mine = {t["id"]: t for t in B11 + B12}; new = [t for t in mine.values() if t["id"] not in have]
    L["templates"] = [mine.get(t["id"], t) for t in L["templates"]] + new  # update in place so re-runs apply fixes
    json.dump(L, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=None, separators=(",", ":")); return len(new)


if __name__ == "__main__":
    for p in ("engine/param_templates.json", "docs/model/templates.json"): print(p, "added", apply(os.path.join(R, p)))
