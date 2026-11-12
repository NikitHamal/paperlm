#!/usr/bin/env python3
"""v17: more grade-pure computed numericals (chem11 / chem12 / cs11 / cs12 had 7-12 templates). Every answer is computed from a standard NEB formula;
distractors are typical student slips. Unit names equal real syllabus_graph unit names. Idempotent: updates engine/param_templates.json,
docs/model/templates.json and appends the ids to packs/pack_specs.json[<pack>].numeric."""
import json, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def T(id, dom, unit, kw, vars_, stem, ans, wrong, law, lawname, sol, u="", sig=3, cond="ans>0", derived=""):
    return dict(id=id, dom=dom, lv="HE", unit=unit, kw=kw, vars=vars_, derived=derived, stem=stem, ans=ans, u=u, wrong=wrong,
                law=law, lawname=lawname, sol=sol, sig=sig, cond=cond)


C = "chemistry"
CH12 = [
    T("c12_buffer", C, "Ionic Equilibrium", ["buffer", "henderson", "pka", "salt"], ["pk=[4.74,4.76,9.25]", "s=[0.2,0.5,1,2]", "a=[0.1,0.2,0.5]"],
      r"A buffer contains $@s@\ \text{mol L}^{-1}$ of salt and $@a@\ \text{mol L}^{-1}$ of weak acid with $\text{p}K_a = @pk@$. Calculate its pH.",
      "pk+log10(s/a)", ["pk-log10(s/a)", "pk+log10(a/s)", "pk", "pk+s/a"], r"Henderson equation: $\text{pH} = \text{p}K_a + \log_{10}\dfrac{[\text{salt}]}{[\text{acid}]}$.",
      "the Henderson equation for a buffer", [r"$\text{pH} = @pk@ + \log_{10}\dfrac{@s@}{@a@}$", r"$\text{pH} = @ans@$"], cond="ans>0 and s!=a"),
    T("c12_ph_poh", C, "Ionic Equilibrium", ["ph", "poh", "ionic", "product", "water"], ["p=[1,2,3,4,5,9.5,10.5,11,12]"],
      r"The $\text{pOH}$ of an aqueous solution at $25^\circ\text{C}$ is $@p@$. Calculate its pH.",
      "14-p", ["p", "14+p", "7-p", "p-7"], r"At $25^\circ\text{C}$, $\text{pH} + \text{pOH} = 14$.", "the relation between pH and pOH",
      [r"$\text{pH} = 14 - \text{pOH} = 14 - @p@$", r"$\text{pH} = @ans@$"], cond="ans>0 and ans!=p"),
    T("c12_electrolysis", C, "Electrochemistry", ["electrolysis", "faraday", "copper", "mass", "deposited"], ["I=[1,2,3,5]", "t=[600,1200,1800,3600]"],
      r"A current of $@I@\ \text{A}$ is passed for $@t@\ \text{s}$ through $\text{CuSO}_4$ solution. Calculate the mass of copper deposited ($M = 63.5\ \text{g mol}^{-1}$, $F = 96500\ \text{C mol}^{-1}$).",
      "63.5*I*t/(2*96500)", ["63.5*I*t/96500", "63.5*I*t/(3*96500)", "2*63.5*I*t/96500", "I*t/96500"], r"By Faraday's first law $m = \dfrac{M I t}{n F}$ with $n = 2$ for $\text{Cu}^{2+}$.",
      "Faraday's first law of electrolysis", [r"$m = \dfrac{63.5\times @I@\times @t@}{2\times 96500}$", r"$m = @ans@\ \text{g}$"], u=r"\text{g}"),
    T("c12_ecell", C, "Electrochemistry", ["electrode", "potential", "cell", "emf", "standard"], ["c=[0.34,0.80,0.52,0.0]", "a=[-0.76,-0.44,-0.13,-2.37,-0.25]"],
      r"A cell has a cathode with $E^\circ = @c@\ \text{V}$ and an anode with $E^\circ = @a@\ \text{V}$. Calculate $E^\circ_{\text{cell}}$.",
      "c-a", ["c+a", "a-c", "(c-a)/2", "c*a"], r"$E^\circ_{\text{cell}} = E^\circ_{\text{cathode}} - E^\circ_{\text{anode}}$.", "the standard cell potential",
      [r"$E^\circ_{\text{cell}} = @c@ - (@a@)$", r"$E^\circ_{\text{cell}} = @ans@\ \text{V}$"], u=r"\text{V}"),
    T("c12_dg_nfe", C, "Electrochemistry", ["gibbs", "cell", "potential", "work", "electrons"], ["n=[1,2,3]", "E=[0.46,1.10,0.80,1.56]"],
      r"A cell transfers $n = @n@$ moles of electrons with $E^\circ_{\text{cell}} = @E@\ \text{V}$. Calculate $\Delta G^\circ$ in kJ ($F = 96500\ \text{C mol}^{-1}$).",
      "-n*96500*E/1000", ["n*96500*E/1000", "-n*96500*E", "-96500*E/1000", "-n*E/1000"], r"$\Delta G^\circ = -nFE^\circ_{\text{cell}}$.",
      "the relation between Gibbs energy and cell potential", [r"$\Delta G^\circ = -@n@\times 96500\times @E@\ \text{J}$", r"$\Delta G^\circ = @ans@\ \text{kJ}$"], u=r"\text{kJ}", cond="ans<0"),
    T("c12_remaining", C, "Chemical Kinetics", ["half", "life", "first", "order", "remaining"], ["A0=[100,80,64,40,160]", "th=[10,20,30,50]", "n=[2,3,4]"],
      r"A first-order reaction has a half-life of $@th@\ \text{min}$. What mass of a $@A0@\ \text{g}$ sample remains after $@T@\ \text{min}$?",
      "A0*0.5**n", ["A0/n", "A0*(1-0.5**n)", "A0*0.5*n", "A0/(2*n)"], r"After $n$ half-lives the amount left is $A_0\left(\dfrac12\right)^n$.",
      "the amount remaining after n half-lives", [r"$n = \dfrac{@T@}{@th@} = @n@$", r"$A = @A0@\times\left(\dfrac12\right)^{@n@} = @ans@\ \text{g}$"], u=r"\text{g}", derived="T=n*th"),
    T("c12_titration", C, "Volumetric Analysis", ["titration", "molarity", "neutralisation", "volume", "acid", "base"], ["M1=[0.1,0.2,0.5]", "V1=[10,20,25,50]", "M2=[0.1,0.25,0.4]"],
      r"$@V1@\ \text{mL}$ of $@M1@\ \text{M}$ HCl exactly neutralises a volume of $@M2@\ \text{M}$ NaOH. Calculate that volume of NaOH.",
      "M1*V1/M2", ["M2*V1/M1", "M1*M2/V1", "V1*(M1+M2)", "V1/(M1*M2)"], r"At the end point $M_1V_1 = M_2V_2$ for a 1:1 reaction.",
      "the titration equation M1V1 = M2V2", [r"$V_2 = \dfrac{M_1V_1}{M_2} = \dfrac{@M1@\times @V1@}{@M2@}$", r"$V_2 = @ans@\ \text{mL}$"], u=r"\text{mL}", cond="M1!=M2"),
    T("c12_eqwt", C, "Volumetric Analysis", ["equivalent", "weight", "normality", "nfactor"], ["M=[0.1,0.2,0.5,1]", "n=[1,2,3]"],
      r"A solution of an acid is $@M@\ \text{M}$ and its n-factor (basicity) is $@n@$. Calculate its normality.",
      "M*n", ["M/n", "M+n", "M*n*n", "n/M"], r"Normality $N = M\times$ n-factor.", "the relation between normality and molarity",
      [r"$N = @M@\times @n@$", r"$N = @ans@\ \text{N}$"], u=r"\text{N}", cond="n>1"),
]
CH11 = [
    T("c11_neutrons", C, "Atomic Structure", ["neutron", "mass", "number", "atomic", "nucleus"], ["A=[23,27,35,40,56,63,108]", "Z=[11,13,17,18,26,29,47]"],
      r"An atom has mass number $A = @A@$ and atomic number $Z = @Z@$. How many neutrons does it contain?",
      "A-Z", ["A+Z", "Z", "A", "A-2*Z"], r"Number of neutrons $= A - Z$.", "the neutron number", [r"$N = A - Z = @A@ - @Z@$", r"$N = @ans@$"], cond="A>Z+2 and A<3*Z"),
    T("c11_bohr_r", C, "Atomic Structure", ["bohr", "radius", "orbit", "hydrogen"], ["n=[1,2,3,4,5]"],
      r"Using $r_n = 0.529\,n^2\ \text{\AA}$, calculate the radius of the Bohr orbit with $n = @n@$ in hydrogen.",
      "0.529*n**2", ["0.529*n", "0.529/n**2", "0.529*n**3", "0.529*2*n"], r"Bohr radius of the $n$th orbit of hydrogen: $r_n = 0.529\,n^2\ \text{\AA}$.",
      "the radius of a Bohr orbit", [r"$r = 0.529\times @n@^2$", r"$r = @ans@\ \text{\AA}$"], u=r"\text{\AA}", cond="n>1"),
    T("c11_mole_ratio", C, "Stoichiometry", ["mole", "ratio", "ammonia", "equation", "haber"], ["n=[3,6,9,12,15]"],
      r"In $\text{N}_2 + 3\text{H}_2 \rightarrow 2\text{NH}_3$, how many moles of $\text{NH}_3$ form from $@n@$ mol of $\text{H}_2$ (excess $\text{N}_2$)?",
      "2*n/3", ["n", "3*n/2", "n/3", "2*n"], r"The balanced equation gives the ratio $\text{H}_2:\text{NH}_3 = 3:2$.",
      "mole ratios from a balanced equation", [r"$\text{NH}_3 = \dfrac{2}{3}\times @n@$", r"$\text{NH}_3 = @ans@\ \text{mol}$"], u=r"\text{mol}"),
    T("c11_dalton", C, "States of Matter", ["dalton", "partial", "pressure", "mole", "fraction"], ["n1=[1,2,3]", "n2=[1,2,3,4]", "P=[1,2,3]"],
      r"A gas mixture has $@n1@$ mol of A and $@n2@$ mol of B at a total pressure of $@P@\ \text{atm}$. Find the partial pressure of A.",
      "n1/(n1+n2)*P", ["n2/(n1+n2)*P", "n1*P", "P/n1", "(n1+n2)*P"], r"Dalton's law: $p_A = x_A P_{\text{total}}$ with $x_A = \dfrac{n_A}{n_A+n_B}$.",
      "Dalton's law of partial pressures", [r"$p_A = \dfrac{@n1@}{@n1@+@n2@}\times @P@$", r"$p_A = @ans@\ \text{atm}$"], u=r"\text{atm}", cond="n1!=n2"),
    T("c11_graham", C, "States of Matter", ["graham", "diffusion", "effusion", "rate", "molar"], ["M1=[2,4,16]", "M2=[32,64,128,16]"],
      r"Find the ratio $\dfrac{r_1}{r_2}$ of the rates of effusion of a gas of molar mass $@M1@\ \text{g mol}^{-1}$ to a gas of molar mass $@M2@\ \text{g mol}^{-1}$.",
      "sqrt(M2/M1)", ["M2/M1", "sqrt(M1/M2)", "M1/M2", "sqrt(M2*M1)"], r"Graham's law: $\dfrac{r_1}{r_2} = \sqrt{\dfrac{M_2}{M_1}}$.",
      "Graham's law of effusion", [r"$\dfrac{r_1}{r_2} = \sqrt{\dfrac{@M2@}{@M1@}}$", r"$\dfrac{r_1}{r_2} = @ans@$"], cond="M2>M1"),
]
K = "cs"
CS11 = [
    T("cs11_octal", K, "Number System and Boolean Logic", ["octal", "decimal", "conversion", "number", "system"], ["a=1:7:1", "b=0:7:1", "c=0:7:1"],
      r"Convert the octal number $(@a@@b@@c@)_8$ into decimal.", "a*64+b*8+c", ["a*100+b*10+c", "a*8+b*4+c", "a+b+c", "a*64+b*16+c"],
      r"Octal to decimal: multiply each digit by a power of 8.", "octal to decimal conversion", [r"$@a@\times 8^2 + @b@\times 8^1 + @c@\times 8^0$", r"$= @ans@$"], cond="ans>0"),
    T("cs11_truth", K, "Number System and Boolean Logic", ["truth", "table", "boolean", "variables", "rows"], ["n=[2,3,4,5,6]"],
      r"How many rows are needed in the truth table of a Boolean function with $@n@$ input variables?", "2**n", ["2*n", "n**2", "2**n-1", "n"],
      r"A function of $n$ variables has $2^n$ input combinations.", "the size of a truth table", [r"Rows $= 2^{@n@}$", r"Rows $= @ans@$"]),
    T("cs11_signed", K, "Number System and Boolean Logic", ["signed", "complement", "range", "bits", "integer"], ["n=[4,8,12,16]"],
      r"What is the largest positive integer that can be stored in an $@n@$-bit signed (two's complement) number?", "2**(n-1)-1", ["2**n-1", "2**(n-1)", "2**n", "2**(n-1)+1"],
      r"An $n$-bit two's complement integer ranges from $-2^{n-1}$ to $2^{n-1}-1$.", "the range of two's complement numbers", [r"Maximum $= 2^{@n@-1} - 1$", r"Maximum $= @ans@$"]),
    T("cs11_colors", K, "Multimedia", ["colour", "depth", "bits", "pixel", "image"], ["n=[1,2,4,8,16,24]"],
      r"An image uses a colour depth of $@n@$ bits per pixel. How many different colours can it display?", "2**n", ["2*n", "n**2", "2**(n-1)", "n*8"],
      r"A colour depth of $n$ bits gives $2^n$ colours.", "colour depth", [r"Colours $= 2^{@n@}$", r"Colours $= @ans@$"]),
    T("cs11_audio", K, "Multimedia", ["audio", "sampling", "rate", "file", "size"], ["sr=[8000,22050,44100]", "b=[8,16]", "t=[10,30,60]"],
      r"Mono audio is sampled at $@sr@\ \text{Hz}$ with $@b@$ bits per sample for $@t@\ \text{s}$. Find the uncompressed size in kilobytes ($1\ \text{KB} = 1000\ \text{B}$).",
      "sr*b*t/8/1000", ["sr*b*t/1000", "sr*b*t/8", "sr*t/8/1000", "sr*b/8/1000"], r"Size $=$ sampling rate $\times$ bits per sample $\times$ time $\times$ channels, divided by 8 for bytes.",
      "the size of uncompressed audio", [r"$\dfrac{@sr@\times @b@\times @t@}{8}\ \text{bytes}$", r"$= @ans@\ \text{KB}$"], u=r"\text{KB}"),
]
CS12 = [
    T("cs12_cartesian", K, "Database Management System", ["cartesian", "product", "relation", "tuples", "rows"], ["r1=[3,4,5,6,8]", "r2=[2,3,5,7]"],
      r"Relation A has $@r1@$ tuples and relation B has $@r2@$ tuples. How many tuples are in the Cartesian product $A \times B$?", "r1*r2", ["r1+r2", "r1", "r1**r2", "r1*r2-1"],
      r"The Cartesian product pairs every tuple of A with every tuple of B.", "the Cartesian product of relations", [r"$@r1@\times @r2@$", r"Tuples $= @ans@$"], cond="r1!=r2"),
    T("cs12_degree", K, "Database Management System", ["degree", "cartesian", "attributes", "columns", "relation"], ["c1=[2,3,4,5]", "c2=[2,3,4,6]"],
      r"Relation A has $@c1@$ attributes and relation B has $@c2@$ attributes. What is the degree of $A \times B$?", "c1+c2", ["c1*c2", "c1", "c1+c2-1", "max(c1,c2)"],
      r"The degree (number of attributes) of $A \times B$ is the sum of the degrees.", "the degree of a Cartesian product", [r"$@c1@ + @c2@$", r"Degree $= @ans@$"], cond="c1!=c2"),
    T("cs12_subnets", K, "Data Communication and Networking", ["subnet", "prefix", "network", "borrowed", "bits"], ["p=[25,26,27,28,29]"],
      r"A /24 network is divided using prefix length $/@p@$. How many equal subnets are created?", "2**(p-24)", ["2**p", "2**(32-p)", "p-24", "2*(p-24)"],
      r"Borrowing $p-24$ host bits creates $2^{p-24}$ subnets.", "subnetting", [r"Borrowed bits $= @p@ - 24$", r"Subnets $= 2^{@p@-24} = @ans@$"]),
    T("cs12_array", K, "Programming in C", ["array", "int", "memory", "bytes", "declaration"], ["n=[5,10,20,50,100]"],
      r"How many bytes does the C declaration \texttt{int a[@n@];} occupy if \texttt{int} is 4 bytes?", "4*n", ["n", "2*n", "4*n+4", "4*(n-1)"],
      r"An array occupies (number of elements) $\times$ (size of one element).", "the size of an array", [r"$@n@\times 4$", r"Size $= @ans@\ \text{bytes}$"], u=r"\text{bytes}"),
    T("cs12_loop", K, "Programming in C", ["loop", "iteration", "for", "counter", "step"], ["a=[0,1,2]", "b=[10,20,30,50]", "s=[2,3,5]"],
      r"How many times does the body of \texttt{for(i=@a@; i<@b@; i+=@s@)} execute?", "ceil((b-a)/s)", ["floor((b-a)/s)", "ceil((b-a)/s)+1", "b-a", "ceil(b/s)+1"],
      r"The loop runs for each $i = a, a+s, \ldots$ while $i < b$, i.e. $\lceil (b-a)/s\rceil$ times.", "the iteration count of a for loop",
      [r"$\left\lceil\dfrac{@b@-@a@}{@s@}\right\rceil$", r"Iterations $= @ans@$"], cond="(b-a)%s!=0"),
]
PACKS = {"chem12": CH12, "chem11": CH11, "cs11": CS11, "cs12": CS12}


def apply(path):
    L = json.load(open(path, encoding="utf-8")); mine = {t["id"]: t for v in PACKS.values() for t in v}; have = {t["id"] for t in L["templates"]}
    L["templates"] = [mine.get(t["id"], t) for t in L["templates"]] + [t for t in mine.values() if t["id"] not in have]
    json.dump(L, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); return len(mine) - len(have & set(mine))


if __name__ == "__main__":
    for p in ("engine/param_templates.json", "docs/model/templates.json"): print(p, "added", apply(os.path.join(R, p)))
    sp = os.path.join(R, "packs", "pack_specs.json"); cur = json.load(open(sp))
    for pid, ts in PACKS.items():
        for t in ts:
            if t["id"] not in cur[pid].setdefault("numeric", []): cur[pid]["numeric"].append(t["id"])
    json.dump(cur, open(sp, "w"), indent=1)
