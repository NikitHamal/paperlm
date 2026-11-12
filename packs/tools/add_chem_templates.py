#!/usr/bin/env python3
"""v18: +7 chem11 and +8 chem12 grade-pure numericals (computed from the formula, never LM-written). Idempotent; updates engine/param_templates.json,
docs/model/templates.json and appends ids to packs/pack_specs.json[chem11|chem12].numeric. Unit names are the real syllabus_graph unit names."""
import json, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def T(id, unit, kw, vars_, stem, ans, wrong, law, lawname, sol, u="", sig=3, cond="ans>0"):
    return dict(id=id, dom="chemistry", lv="H", unit=unit, kw=kw, vars=vars_, derived="", stem=stem, ans=ans, u=u, wrong=wrong, law=law, lawname=lawname, sol=sol, sig=sig, cond=cond)


C11 = [
    T("c11_limiting", "Stoichiometry", ["limiting", "reagent", "ammonia", "nitrogen", "hydrogen"], ["x=[1,2,3,4]", "y=[3,4,6,9,12]"],
      r"In $\text{N}_2 + 3\text{H}_2 \rightarrow 2\text{NH}_3$, $@x@\ \text{mol}$ of $\text{N}_2$ reacts with $@y@\ \text{mol}$ of $\text{H}_2$. How many moles of $\text{NH}_3$ can form at most?", "min(2*x,2*y/3)",
      ["max(2*x,2*y/3)", "x+y", "2*(x+y)/4", "min(x,y/3)"], r"The limiting reagent decides the yield: $\text{N}_2$ gives $2x$ mol, $\text{H}_2$ gives $\tfrac{2y}{3}$ mol of $\text{NH}_3$.", "the limiting reagent",
      [r"From $\text{N}_2$: $2\times@x@$; from $\text{H}_2$: $\dfrac{2\times@y@}{3}$", r"$n(\text{NH}_3) = @ans@\ \text{mol}$"], u=r"\text{mol}", cond="2*x!=2*y/3 and ans>0"),
    T("c11_gas_density", "States of Matter", ["density", "gas", "ideal", "molar", "mass"], ["P=[1,2,0.5]", "M=[2,16,28,32,44]", "Tk=[273,300,350]"],
      r"Find the density of a gas of molar mass $@M@\ \text{g mol}^{-1}$ at $@P@\ \text{atm}$ and $@Tk@\ \text{K}$ ($R = 0.0821\ \text{L atm K}^{-1}\text{mol}^{-1}$).", "P*M/(0.0821*Tk)",
      ["P*M*0.0821*Tk", "P*M/Tk", "0.0821*Tk/(P*M)", "P/(0.0821*Tk*M)"], r"From $PV = nRT$: $d = \dfrac{PM}{RT}$.", "the density of an ideal gas", [r"$d = \dfrac{@P@\times@M@}{0.0821\times@Tk@}$", r"$d = @ans@\ \text{g L}^{-1}$"], u=r"\text{g L}^{-1}"),
    T("c11_kp_kc", "Chemical equilibrium", ["kp", "kc", "equilibrium", "constant", "gaseous"], ["Kc=[0.5,2,4,10]", "dn=[1,2]", "Tk=[300,400,500]"],
      r"For a gaseous reaction with $\Delta n = @dn@$ the value of $K_c$ is $@Kc@$ at $@Tk@\ \text{K}$. Find $K_p$ ($R = 0.0821\ \text{L atm K}^{-1}\text{mol}^{-1}$).", "Kc*(0.0821*Tk)**dn",
      ["Kc*(0.0821*Tk)**(-dn)", "Kc*0.0821*Tk*dn", "Kc/(0.0821*Tk)**dn", "Kc*Tk**dn"], r"$K_p = K_c(RT)^{\Delta n}$.", "the relation between $K_p$ and $K_c$", [r"$K_p = @Kc@\times(0.0821\times@Tk@)^{@dn@}$", r"$K_p = @ans@$"]),
    T("c11_wavelength", "Atomic Structure", ["frequency", "wavelength", "radiation", "light", "speed"], ["nu=[5,6,7.5,10]"],
      r"Calculate the wavelength of radiation of frequency $@nu@\times10^{14}\ \text{Hz}$ ($c = 3\times10^{8}\ \text{m s}^{-1}$).", "3000/nu", ["3000*nu", "nu/3000", "300/nu", "30000/nu"], r"$c = \nu\lambda$, so $\lambda = \dfrac{c}{\nu}$.", "the wave relation",
      [r"$\lambda = \dfrac{3\times10^{8}}{@nu@\times10^{14}}\ \text{m}$", r"$\lambda = @ans@\ \text{nm}$"], u=r"\text{nm}"),
    T("c11_spec_lines", "Atomic Structure", ["spectral", "lines", "hydrogen", "transitions", "shell"], ["n=[3,4,5,6]"],
      r"An excited hydrogen atom in the $n=@n@$ level can fall to lower levels in all possible ways. How many different spectral lines can be emitted?", "n*(n-1)/2", ["n*(n+1)/2", "n*(n-1)", "n-1", "n**2"],
      r"The number of lines $= \dfrac{n(n-1)}{2}$.", "the number of spectral lines", [r"Lines $= \dfrac{@n@(@n@-1)}{2}$", r"Lines $= @ans@$"]),
    T("c11_shell_e", "Atomic Structure", ["shell", "electrons", "maximum", "principal", "quantum"], ["n=[2,3,4,5]"],
      r"What is the maximum number of electrons in the shell with principal quantum number $n = @n@$?", "2*n**2", ["n**2", "2*n", "2**n", "2*(n-1)**2"], r"A shell holds at most $2n^2$ electrons.", "the capacity of a shell",
      [r"Maximum electrons $= 2n^2 = 2\times@n@^2$", r"Maximum electrons $= @ans@$"]),
    T("c11_mass_ca", "Foundation and Fundamentals", ["mass", "calcium", "carbonate", "composition", "percentage"], ["m=[25,50,100,200,500]"],
      r"How many grams of calcium are present in $@m@\ \text{g}$ of $\text{CaCO}_3$? ($\text{Ca}=40$, $\text{C}=12$, $\text{O}=16$)", "m*40/100", ["m*60/100", "m*40", "m*100/40", "m*12/100"],
      r"The molar mass of $\text{CaCO}_3$ is $100\ \text{g mol}^{-1}$ and it contains $40\ \text{g}$ of Ca per mole.", "mass composition", [r"$m_{Ca} = \dfrac{40}{100}\times@m@$", r"$m_{Ca} = @ans@\ \text{g}$"], u=r"\text{g}"),
]
C12 = [
    T("c12_k_first", "Chemical Kinetics", ["first", "order", "rate", "constant", "decomposed"], ["t=[10,20,30,50]", "x=[20,50,75,90]"],
      r"A first-order reaction is $@x@\%$ complete in $@t@\ \text{min}$. Find the rate constant ($\log$ is to the base 10).", "2.303/t*log10(100/(100-x))",
      ["2.303/t*log10(100/x)", "1/t*log10(100/(100-x))", "2.303*t*log10(100/(100-x))", "2.303/t*(100-x)/100"], r"$k = \dfrac{2.303}{t}\log\dfrac{a}{a-x}$.", "the first-order integrated rate law",
      [r"$k = \dfrac{2.303}{@t@}\log\dfrac{100}{100-@x@}$", r"$k = @ans@\ \text{min}^{-1}$"], u=r"\text{min}^{-1}"),
    T("c12_rate_law", "Chemical Kinetics", ["rate", "law", "order", "concentration", "constant"], ["k=[0.1,0.2,0.5,2]", "A=[0.1,0.2,0.5]", "B=[0.1,0.2,0.4]"],
      r"For a reaction with rate law $\text{rate} = k[\text{A}]^2[\text{B}]$, $k = @k@$ (units consistent), $[\text{A}] = @A@\ \text{M}$ and $[\text{B}] = @B@\ \text{M}$. Find the rate.", "k*A**2*B",
      ["k*A*B", "k*A*B**2", "k*(A+B)**2", "k*A**2"], r"Insert the concentrations into the rate law.", "the rate law", [r"$\text{rate} = @k@\times(@A@)^2\times@B@$", r"$\text{rate} = @ans@\ \text{M s}^{-1}$"], u=r"\text{M s}^{-1}"),
    T("c12_ksp_a2b", "Ionic Equilibrium", ["solubility", "product", "ksp", "sparingly", "soluble"], ["e=[3,4,5]"],
      r"The molar solubility of $\text{CaF}_2$ is $s = 10^{-@e@}\ \text{mol L}^{-1}$. Calculate its solubility product $K_{sp}$.", "4*10**(-3*e)", ["10**(-2*e)", "2*10**(-3*e)", "4*10**(-2*e)", "27*10**(-4*e)"],
      r"$\text{CaF}_2 \rightleftharpoons \text{Ca}^{2+} + 2\text{F}^-$, so $K_{sp} = s(2s)^2 = 4s^3$.", "the solubility product", [r"$K_{sp} = 4s^3 = 4\times(10^{-@e@})^3$", r"$K_{sp} = @ans@\ \text{mol}^3\text{L}^{-3}$"], u=r"\text{mol}^3\text{L}^{-3}"),
    T("c12_ka_ph", "Ionic Equilibrium", ["weak", "acid", "dissociation", "constant", "ph"], ["pH=[3,4]", "C=[0.1,0.5,1]"],
      r"A $@C@\ \text{M}$ solution of a weak monobasic acid has $\text{pH} = @pH@$. Find its dissociation constant $K_a$.", "10**(-2*pH)/C", ["10**(-pH)/C", "10**(-2*pH)*C", "10**(-pH)*C", "10**(-pH)"],
      r"$[\text{H}^+] = 10^{-\text{pH}}$ and $K_a = \dfrac{[\text{H}^+]^2}{C}$ for a weak acid.", "the dissociation constant of a weak acid", [r"$K_a = \dfrac{(10^{-@pH@})^2}{@C@}$", r"$K_a = @ans@$"]),
    T("c12_hess", "Thermodynamics", ["enthalpy", "formation", "reaction", "hess", "products"], ["r=[-75,-85,-200]", "p1=[-110,-393,-286]", "p2=[-242,-286,-130]"],
      r"For $\text{A} \rightarrow \text{B} + \text{C}$ the standard enthalpies of formation are $\Delta H_f(\text{A}) = @r@\ \text{kJ mol}^{-1}$, $\Delta H_f(\text{B}) = @p1@\ \text{kJ mol}^{-1}$ and $\Delta H_f(\text{C}) = @p2@\ \text{kJ mol}^{-1}$. Find $\Delta H^\circ$ of the reaction.",
      "p1+p2-r", ["p1+p2+r", "r-p1-p2", "p1-p2-r", "(p1+p2)/r"], r"$\Delta H^\circ = \sum\Delta H_f(\text{products}) - \sum\Delta H_f(\text{reactants})$.", "Hess's law", [r"$\Delta H^\circ = (@p1@) + (@p2@) - (@r@)$", r"$\Delta H^\circ = @ans@\ \text{kJ mol}^{-1}$"],
      u=r"\text{kJ mol}^{-1}", cond="ans!=0"),
    T("c12_entropy_ph", "Thermodynamics", ["entropy", "phase", "transition", "enthalpy", "equilibrium"], ["dH=[6.0,40.7,2.5,30]", "Tk=[273,298,373]"],
      r"A phase change at $@Tk@\ \text{K}$ absorbs $@dH@\ \text{kJ mol}^{-1}$ of heat reversibly. Find the entropy change.", "dH*1000/Tk", ["dH/Tk", "dH*1000*Tk", "Tk/(dH*1000)", "dH*Tk"], r"At equilibrium $\Delta S = \dfrac{\Delta H}{T}$.", "the entropy of a phase change",
      [r"$\Delta S = \dfrac{@dH@\times1000}{@Tk@}$", r"$\Delta S = @ans@\ \text{J K}^{-1}\text{mol}^{-1}$"], u=r"\text{J K}^{-1}\text{mol}^{-1}"),
    T("c12_nernst", "Electrochemistry", ["nernst", "equation", "cell", "potential", "reaction", "quotient"], ["E0=[1.10,0.76,0.34,1.56]", "n=[1,2]", "Q=[10,100,1000]"],
      r"A cell has $E^\circ_{cell} = @E0@\ \text{V}$ for a reaction with $n = @n@$. Find $E_{cell}$ at $298\ \text{K}$ when the reaction quotient is $Q = @Q@$.", "E0-0.0592/n*log10(Q)",
      ["E0+0.0592/n*log10(Q)", "E0-0.0592*n*log10(Q)", "E0-0.0592/n*ln(Q)", "E0-0.0592/n*Q"], r"$E = E^\circ - \dfrac{0.0592}{n}\log Q$.", "the Nernst equation", [r"$E = @E0@ - \dfrac{0.0592}{@n@}\log @Q@$", r"$E = @ans@\ \text{V}$"], u=r"\text{V}", cond="ans>0"),
    T("c12_c14_age", "Nuclear Chemistry and Applications of Radioactivity", ["carbon", "dating", "half", "life", "age", "fossil"], ["r=[2,4,8]"],
      r"A fossil contains $\dfrac{1}{@r@}$ of the $^{14}\text{C}$ activity of a living sample. Find its age (half-life of $^{14}\text{C} = 5730\ \text{years}$).", "5730*ln(r)/0.693", ["5730*r", "5730/r", "5730*ln(r)", "5730*(r-1)/0.693"],
      r"$t = \dfrac{t_{1/2}}{0.693}\ln\dfrac{N_0}{N}$.", "radiocarbon dating", [r"$t = \dfrac{5730}{0.693}\ln @r@$", r"$t = @ans@\ \text{years}$"], u=r"\text{years}"),
]


def apply(path):
    D = json.load(open(path, encoding="utf-8")); mine = {t["id"]: t for t in C11 + C12}; have = {t["id"] for t in D["templates"]}
    D["templates"] = [mine.get(t["id"], t) for t in D["templates"]] + [t for t in mine.values() if t["id"] not in have]
    json.dump(D, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); return len(mine) - len(have & set(mine))


if __name__ == "__main__":
    for p in ("engine/param_templates.json", "docs/model/templates.json"): print(p, "added", apply(os.path.join(R, p)))
    sp = os.path.join(R, "packs", "pack_specs.json"); cur = json.load(open(sp))
    for pid, ts in (("chem11", C11), ("chem12", C12)):
        for t in ts:
            if t["id"] not in cur[pid].setdefault("numeric", []): cur[pid]["numeric"].append(t["id"])
    json.dump(cur, open(sp, "w"), indent=1)
