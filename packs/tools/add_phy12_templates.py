#!/usr/bin/env python3
"""v18: +19 grade-pure PHYSICS numericals for phy12 (it had 24; every answer is computed from a standard NEB Class 12 formula, distractors are the
usual student slips). Idempotent: updates engine/param_templates.json + docs/model/templates.json and appends ids to packs/pack_specs.json[phy12].numeric.
Unit names are the real phy12 syllabus_graph unit names (never class 11 chapters)."""
import json, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def T(id, unit, kw, vars_, stem, ans, wrong, law, lawname, sol, u="", sig=3, cond="ans>0"):
    return dict(id=id, dom="physics", lv="H", unit=unit, kw=kw, vars=vars_, derived="", stem=stem, ans=ans, u=u, wrong=wrong, law=law, lawname=lawname, sol=sol, sig=sig, cond=cond)


MU = r"\mu"
L = [
    T("p12_ydse", "Interference", ["fringe", "width", "double", "slit", "young"], ["lam=[400,500,600,650,700]", "D=[1,1.5,2]", "d=[0.5,1,2]"],
      r"In Young's double-slit experiment light of wavelength $@lam@\ \text{nm}$ is used, the slits are $@d@\ \text{mm}$ apart and the screen is $@D@\ \text{m}$ away. Find the fringe width.",
      "lam*D/d*1e-3", ["lam*d/D*1e-3", "lam*D/d*1e-6", "lam*D*d*1e-3", "lam*D/d"], r"The fringe width is $\beta = \dfrac{\lambda D}{d}$.", "the fringe width in Young's experiment",
      [r"$\beta = \dfrac{\lambda D}{d} = \dfrac{@lam@\times10^{-9}\times@D@}{@d@\times10^{-3}}$", r"$\beta = @ans@\ \text{mm}$"], u=r"\text{mm}"),
    T("p12_brewster", "Polarization", ["brewster", "polarizing", "angle", "refractive", "index"], ["mu=[1.33,1.5,1.62,1.73,1.41]"],
      r"Light is reflected from a glass surface of refractive index $@mu@$. At what angle of incidence (in degrees) is the reflected light completely plane polarized?",
      "atan(mu)*180/pi", ["atan(1/mu)*180/pi", "90-atan(mu)*180/pi", "atan(mu)*90/pi", "mu*30"], r"Brewster's law: $\tan\theta_p = \mu$.", "Brewster's law",
      [r"$\theta_p = \tan^{-1}(@mu@)$", r"$\theta_p = @ans@^{\circ}$"], u=r"^{\circ}"),
    T("p12_capillary", "Fluid statics", ["capillary", "rise", "surface", "tension", "tube"], ["r=[0.2,0.5,1,2]"],
      r"Water (surface tension $0.072\ \text{N m}^{-1}$, density $1000\ \text{kg m}^{-3}$, zero angle of contact) rises in a capillary tube of radius $@r@\ \text{mm}$. Find the height of rise. Take $g=9.8\ \text{m s}^{-2}$.",
      "2*0.072*1000/(r*9.8)", ["0.072*1000/(r*9.8)", "4*0.072*1000/(r*9.8)", "2*0.072*1000*r/9.8", "2*0.072/(r*9.8)"], r"Jurin's law: $h = \dfrac{2T\cos\theta}{r\rho g}$.", "capillary rise",
      [r"$h = \dfrac{2\times0.072}{@r@\times10^{-3}\times1000\times9.8}\ \text{m}$", r"$h = @ans@\ \text{mm}$"], u=r"\text{mm}"),
    T("p12_zlcr", "Alternating Currents", ["impedance", "lcr", "series", "reactance", "resistance"], ["R=[30,40,60]", "XL=[50,80,100,120]", "XC=[20,50,80]"],
      r"A series LCR circuit has $R=@R@\ \Omega$, $X_L=@XL@\ \Omega$ and $X_C=@XC@\ \Omega$. Calculate its impedance.", "sqrt(R**2+(XL-XC)**2)",
      ["R+XL+XC", "sqrt(R**2+(XL+XC)**2)", "sqrt(R**2+XL**2+XC**2)", "R+XL-XC"], r"$Z = \sqrt{R^2+(X_L-X_C)^2}$.", "the impedance of a series LCR circuit",
      [r"$Z = \sqrt{@R@^2+(@XL@-@XC@)^2}$", r"$Z = @ans@\ \Omega$"], u=r"\Omega", cond="XL!=XC and ans>0"),
    T("p12_mutual", "Electromagnetic Induction", ["mutual", "inductance", "emf", "coil", "current"], ["M=[10,20,50,100]", "dI=[1,2,5]", "dt=[0.01,0.02,0.1,0.5]"],
      r"Two coils have a mutual inductance of $@M@\ \text{mH}$. The current in the primary changes by $@dI@\ \text{A}$ in $@dt@\ \text{s}$. Find the emf induced in the secondary.",
      "M*1e-3*dI/dt", ["M*dI/dt", "M*1e-3*dt/dI", "M*1e-3*dI*dt", "M*1e-6*dI/dt"], r"$\varepsilon = M\dfrac{dI}{dt}$.", "mutual induction", [r"$\varepsilon = @M@\times10^{-3}\times\dfrac{@dI@}{@dt@}$", r"$\varepsilon = @ans@\ \text{V}$"], u=r"\text{V}"),
    T("p12_lenergy", "Electromagnetic Induction", ["inductor", "energy", "stored", "self", "inductance"], ["L=[50,100,200,500]", "I=[1,2,3,5]"],
      r"An inductor of $@L@\ \text{mH}$ carries a steady current of $@I@\ \text{A}$. How much energy is stored in its magnetic field?", "0.5*L*1e-3*I**2",
      ["L*1e-3*I**2", "0.5*L*1e-3*I", "0.5*L*I**2", "0.5*L**2*1e-3*I"], r"$U = \tfrac12 LI^2$.", "the energy stored in an inductor", [r"$U = \tfrac12\times@L@\times10^{-3}\times@I@^2$", r"$U = @ans@\ \text{J}$"], u=r"\text{J}"),
    T("p12_lorentz_r", "Magnetic field", ["proton", "circular", "path", "radius", "magnetic"], ["v=[100,200,500,1000]", "B=[10,20,50,100]"],
      r"A proton ($m=1.67\times10^{-27}\ \text{kg}$, $q=1.6\times10^{-19}\ \text{C}$) enters a uniform magnetic field of $@B@\ \text{mT}$ perpendicular to the field with speed $@v@\ \text{km s}^{-1}$. Find the radius of its circular path.",
      "1.67e-27*v*1e3/(1.6e-19*B*1e-3)*100", ["1.67e-27*v*1e3/(1.6e-19*B*1e-3)*100*2", "1.67e-27*v*1e3/(1.6e-19*B*1e-3)*100/2", "1.67e-27*v*1e3/(1.6e-19*B*1e-3)", "1.67e-27*v*1e3/(1.6e-19*B*1e-3)*100*pi"],
      r"The magnetic force provides the centripetal force: $qvB = \dfrac{mv^2}{r}$, so $r = \dfrac{mv}{qB}$.", "the radius of a charged particle's circular path",
      [r"$r = \dfrac{mv}{qB} = \dfrac{1.67\times10^{-27}\times@v@\times10^{3}}{1.6\times10^{-19}\times@B@\times10^{-3}}$", r"$r = @ans@\ \text{cm}$"], u=r"\text{cm}"),
    T("p12_binding", "Radioactivity and nuclear reaction", ["mass", "defect", "binding", "energy", "nucleus"], ["dm=[0.01,0.02,0.03,0.05,0.1]"],
      r"The mass defect of a nucleus is $@dm@\ \text{u}$. Find its binding energy in MeV ($1\ \text{u}=931.5\ \text{MeV}/c^2$).", "dm*931.5", ["dm*93.15", "dm*9315", "dm/931.5", "dm*931.5**2"],
      r"$E_b = \Delta m\times931.5\ \text{MeV}$.", "binding energy", [r"$E_b = @dm@\times931.5$", r"$E_b = @ans@\ \text{MeV}$"], u=r"\text{MeV}"),
    T("p12_nuc_radius", "Radioactivity and nuclear reaction", ["nuclear", "radius", "mass", "number", "fermi"], ["A=[8,27,64,125,216]"],
      r"Using $R = R_0A^{1/3}$ with $R_0 = 1.2\ \text{fm}$, find the radius of a nucleus of mass number $@A@$.", "1.2*A**(1/3)", ["1.2*A", "1.2*A**2", "1.2*A/3", "1.2*A**(1/2)"],
      r"Nuclear radius: $R = R_0A^{1/3}$.", "the nuclear radius", [r"$R = 1.2\times@A@^{1/3}$", r"$R = @ans@\ \text{fm}$"], u=r"\text{fm}"),
    T("p12_photon_e", "Photons", ["photon", "energy", "wavelength", "ev"], ["lam=[200,310,400,500,620,775]"],
      r"Find the energy in eV of a photon of wavelength $@lam@\ \text{nm}$ ($hc = 1240\ \text{eV nm}$).", "1240/lam", ["1240*lam", "lam/1240", "12400/lam", "1240/lam/2"],
      r"$E = \dfrac{hc}{\lambda}$.", "the photon energy", [r"$E = \dfrac{1240}{@lam@}$", r"$E = @ans@\ \text{eV}$"], u=r"\text{eV}"),
    T("p12_beta", "Semiconductor devices", ["transistor", "current", "gain", "collector", "base"], ["Ic=[1,2,3,5]", "Ib=[10,20,25,40,50]"],
      r"In a common-emitter transistor circuit the collector current is $@Ic@\ \text{mA}$ and the base current is $@Ib@\ \mu\text{A}$. Find the current gain $\beta$.", "Ic*1000/Ib",
      ["Ic/Ib", "Ib/Ic/1000", "Ic*Ib", "Ic*1000/(Ic*1000+Ib)"], r"$\beta = \dfrac{I_C}{I_B}$.", "the current gain of a transistor", [r"$\beta = \dfrac{@Ic@\times10^{-3}}{@Ib@\times10^{-6}}$", r"$\beta = @ans@$"]),
    T("p12_alpha", "Semiconductor devices", ["transistor", "alpha", "beta", "current", "gain"], ["b=[19,49,99,100,50,200]"],
      r"A transistor has a current gain $\beta = @b@$. Find $\alpha = I_C/I_E$.", "b/(1+b)", ["b/(1-b)", "1/(1+b)", "(1+b)/b", "b"], r"$\alpha = \dfrac{\beta}{1+\beta}$.", "the relation between alpha and beta",
      [r"$\alpha = \dfrac{@b@}{1+@b@}$", r"$\alpha = @ans@$"], cond="b>0 and ans>0"),
    T("p12_doppler", "Acoustic phenomena", ["doppler", "source", "approaching", "frequency", "observer"], ["f=[400,500,600,1000]", "vs=[10,20,30,40]"],
      r"A source of frequency $@f@\ \text{Hz}$ moves towards a stationary observer at $@vs@\ \text{m s}^{-1}$. If the speed of sound is $340\ \text{m s}^{-1}$, find the frequency heard.",
      "f*340/(340-vs)", ["f*340/(340+vs)", "f*(340-vs)/340", "f*(340+vs)/340", "f+vs"], r"$f' = f\dfrac{v}{v-v_s}$ for an approaching source.", "the Doppler effect",
      [r"$f' = @f@\times\dfrac{340}{340-@vs@}$", r"$f' = @ans@\ \text{Hz}$"], u=r"\text{Hz}"),
    T("p12_closed_pipe", "Wave in pipes and strings", ["closed", "pipe", "fundamental", "frequency", "length"], ["L=[20,25,40,50,85]"],
      r"A pipe closed at one end is $@L@\ \text{cm}$ long. Find its fundamental frequency (speed of sound $340\ \text{m s}^{-1}$).", "340/(4*L/100)", ["340/(2*L/100)", "340/(L/100)", "340/(8*L/100)", "4*340/(L/100)"],
      r"For a closed pipe $f_1 = \dfrac{v}{4L}$.", "the closed-pipe fundamental", [r"$f_1 = \dfrac{340}{4\times@L@\times10^{-2}}$", r"$f_1 = @ans@\ \text{Hz}$"], u=r"\text{Hz}"),
    T("p12_carnot", "Second Law of Thermodynamics", ["carnot", "engine", "efficiency", "reservoir", "temperature"], ["T1=[400,500,600,800]", "T2=[200,250,300]"],
      r"A Carnot engine works between $@T1@\ \text{K}$ and $@T2@\ \text{K}$. Find its efficiency in percent.", "(1-T2/T1)*100", ["T2/T1*100", "(T1-T2)/T2*100", "(1-T2/T1)", "(T1-T2)"],
      r"$\eta = 1-\dfrac{T_2}{T_1}$.", "the Carnot efficiency", [r"$\eta = 1-\dfrac{@T2@}{@T1@}$", r"$\eta = @ans@\%$"], u=r"\%", cond="T2<T1 and ans>0"),
    T("p12_first_law", "First Law of Thermodynamics", ["internal", "energy", "heat", "work", "gas"], ["Q=[200,300,500,800]", "W=[50,100,150,200,250]"],
      r"A gas absorbs $@Q@\ \text{J}$ of heat and does $@W@\ \text{J}$ of work on its surroundings. Find the change in its internal energy.", "Q-W", ["Q+W", "W-Q", "(Q+W)/2", "Q*W"],
      r"First law: $\Delta U = Q - W$.", "the first law of thermodynamics", [r"$\Delta U = @Q@ - @W@$", r"$\Delta U = @ans@\ \text{J}$"], u=r"\text{J}", cond="Q>W"),
    T("p12_rot_ke", "Rotational dynamics", ["rotational", "kinetic", "energy", "moment", "inertia"], ["I=[0.2,0.5,1,2]", "w=[2,4,10,20]"],
      r"A wheel of moment of inertia $@I@\ \text{kg m}^2$ rotates at $@w@\ \text{rad s}^{-1}$. Find its rotational kinetic energy.", "0.5*I*w**2", ["I*w**2", "0.5*I*w", "0.5*I**2*w", "I*w"],
      r"$K = \tfrac12 I\omega^2$.", "rotational kinetic energy", [r"$K = \tfrac12\times@I@\times@w@^2$", r"$K = @ans@\ \text{J}$"], u=r"\text{J}"),
    T("p12_torque", "Rotational dynamics", ["torque", "angular", "acceleration", "moment", "inertia"], ["I=[0.5,1,2,5]", "al=[2,4,5,10]"],
      r"A torque acts on a body of moment of inertia $@I@\ \text{kg m}^2$ and gives it an angular acceleration of $@al@\ \text{rad s}^{-2}$. Find the torque.", "I*al", ["I/al", "al/I", "I*al**2", "I**2*al"],
      r"$\tau = I\alpha$.", "the torque-angular acceleration relation", [r"$\tau = @I@\times@al@$", r"$\tau = @ans@\ \text{N m}$"], u=r"\text{N m}"),
    T("p12_shm_vmax", "Periodic motion", ["simple", "harmonic", "amplitude", "maximum", "speed"], ["A=[2,5,10,20]", "Tp=[0.5,1,2,4]"],
      r"A particle executes simple harmonic motion of amplitude $@A@\ \text{cm}$ and period $@Tp@\ \text{s}$. Find its maximum speed.", "2*pi/Tp*A", ["A/Tp", "2*pi*A*Tp", "A*Tp/(2*pi)", "(2*pi/Tp)**2*A"],
      r"$v_{max} = A\omega = \dfrac{2\pi A}{T}$.", "the maximum speed in SHM", [r"$v_{max} = \dfrac{2\pi}{@Tp@}\times@A@$", r"$v_{max} = @ans@\ \text{cm s}^{-1}$"], u=r"\text{cm s}^{-1}"),
    T("p12_beats", "Wave motion", ["beats", "frequency", "tuning", "fork", "superposition"], ["f1=[256,260,512,440]", "f2=[250,254,505,436]"],
      r"Two tuning forks of frequencies $@f1@\ \text{Hz}$ and $@f2@\ \text{Hz}$ are sounded together. How many beats are heard per second?", "f1-f2", ["f1+f2", "(f1+f2)/2", "f1/f2", "f2-f1"],
      r"Beat frequency $= |f_1 - f_2|$.", "beat frequency", [r"$f_b = @f1@ - @f2@$", r"$f_b = @ans@\ \text{Hz}$"], u=r"\text{Hz}", cond="f1>f2 and f1-f2<12"),
]


def apply(path):
    D = json.load(open(path, encoding="utf-8")); mine = {t["id"]: t for t in L}; have = {t["id"] for t in D["templates"]}
    D["templates"] = [mine.get(t["id"], t) for t in D["templates"]] + [t for t in mine.values() if t["id"] not in have]
    json.dump(D, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); return len(mine) - len(have & set(mine))


if __name__ == "__main__":
    for p in ("engine/param_templates.json", "docs/model/templates.json"): print(p, "added", apply(os.path.join(R, p)))
    sp = os.path.join(R, "packs", "pack_specs.json"); cur = json.load(open(sp))
    for t in L:
        if t["id"] not in cur["phy12"].setdefault("numeric", []): cur["phy12"]["numeric"].append(t["id"])
    json.dump(cur, open(sp, "w"), indent=1); print("phy12 numeric", len(cur["phy12"]["numeric"]))
