#!/usr/bin/env python3
"""Authoring script for the PaperLM Parametric Formula & Distractor Engine template library.
Writes engine/param_templates.json (consumed identically by engine/parametric.py, engine/web/parametric.js and Android).

Every template = verified law/formula + variable ranges + answer expression + 'typical mistake' expressions (distractors) + worked solution.
Expressions use ONLY: + - * / ** ( ), numbers, variable names and sqrt sin cos tan atan ln log10 exp abs pi rad comb perm fact max min ceil floor
so the exact same string evaluates in Python and JavaScript.
Placeholders in stem/sol text are @name@ (variables, derived values, @ans@).
lv: S = school (C8-C10), H = +2 (C11/C12), E = entrance/engineering (CEE/IOE/BE/BCA/...), N = nursing, all = any.
"""
import json, os
T = []


def t(id, dom, lv, unit, kw, vars, stem, ans, u, wrong, law, lawname, sol, derived="", sig=3, cond="ans>0"):
    T.append(dict(id=id, dom=dom, lv=lv, unit=unit, kw=kw.split(), vars=vars.split(), derived=derived, stem=stem, ans=ans, u=u,
                  wrong=[w for w in wrong.split("|") if w], law=law, lawname=lawname, sol=sol, sig=sig, cond=cond))


# ---------------------------------------------------------------- PHYSICS
t("kin_v", "physics electrical", "SHE", "Motion in a straight line", "motion kinematics velocity equations", "u=0:20:2 a=1:9:1 t=2:12:1",
  r"A car moving with an initial velocity of $@u@\ \text{m s}^{-1}$ accelerates uniformly at $@a@\ \text{m s}^{-2}$ for $@t@\ \text{s}$. Find its final velocity.",
  "u+a*t", r"\text{m s}^{-1}", "u+a|a*t|(u+a*t)/2|u*t",
  r"For uniform acceleration the first equation of motion is $v = u + at$.", "the first equation of motion",
  [r"$v = u + at = @u@ + @a@\times @t@$", r"$v = @ans@\ \text{m s}^{-1}$"])
t("kin_s", "physics", "SHE", "Motion in a straight line", "motion kinematics displacement equations", "u=0:15:1 a=1:8:1 t=2:10:1",
  r"A particle starts with a velocity of $@u@\ \text{m s}^{-1}$ and accelerates uniformly at $@a@\ \text{m s}^{-2}$. Calculate the distance travelled in $@t@\ \text{s}$.",
  "u*t+0.5*a*t**2", r"\text{m}", "u*t+a*t**2|0.5*a*t**2|(u+a*t)*t|u*t+0.5*a*t",
  r"For uniform acceleration the second equation of motion is $s = ut + \tfrac{1}{2}at^{2}$.", "the second equation of motion",
  [r"$s = ut + \tfrac{1}{2}at^{2} = @u@\times@t@ + \tfrac{1}{2}\times@a@\times@t@^{2}$", r"$s = @ans@\ \text{m}$"])
t("newton2", "physics", "SHE", "Laws of motion", "newton laws motion force dynamics", "m=2:40:2 a=1:12:1",
  r"A force acts on a body of mass $@m@\ \text{kg}$ and produces an acceleration of $@a@\ \text{m s}^{-2}$. Calculate the magnitude of the force.",
  "m*a", r"\text{N}", "m/a|m+a|a/m",
  r"Newton's second law states that the net force equals mass times acceleration, $F = ma$.", "Newton's second law of motion",
  [r"$F = ma = @m@\times@a@$", r"$F = @ans@\ \text{N}$"])
t("pe_mgh", "physics", "SHE", "Work, energy and power", "energy work potential gravitational", "m=1:20:1 h=2:30:2",
  r"Find the gravitational potential energy of a body of mass $@m@\ \text{kg}$ raised to a height of $@h@\ \text{m}$ above the ground. (Take $g = 9.8\ \text{m s}^{-2}$.)",
  "m*9.8*h", r"\text{J}", "m*h|m*9.8|0.5*m*9.8*h|m*9.8/h",
  r"Gravitational potential energy near the Earth's surface is $U = mgh$.", "gravitational potential energy",
  [r"$U = mgh = @m@\times 9.8\times@h@$", r"$U = @ans@\ \text{J}$"])
t("ke", "physics", "SHE", "Work, energy and power", "energy kinetic work", "m=2:20:2 v=2:20:2",
  r"Calculate the kinetic energy of a body of mass $@m@\ \text{kg}$ moving with a speed of $@v@\ \text{m s}^{-1}$.",
  "0.5*m*v**2", r"\text{J}", "m*v**2|0.5*m*v|m*v|0.5*m**2*v",
  r"The kinetic energy of a body of mass $m$ moving with speed $v$ is $K = \tfrac{1}{2}mv^{2}$.", "kinetic energy",
  [r"$K = \tfrac{1}{2}mv^{2} = \tfrac{1}{2}\times@m@\times@v@^{2}$", r"$K = @ans@\ \text{J}$"])
t("impulse", "physics", "HE", "Momentum and impulse", "momentum impulse collision force", "m=1:10:1 u=0:10:2 v=12:30:2 t=1:5:1",
  r"A body of mass $@m@\ \text{kg}$ changes its velocity from $@u@\ \text{m s}^{-1}$ to $@v@\ \text{m s}^{-1}$ in $@t@\ \text{s}$. Find the average force acting on it.",
  "m*(v-u)/t", r"\text{N}", "m*(v+u)/t|m*(v-u)|m*v/t|(v-u)/t",
  r"Force equals the rate of change of momentum, $F = \dfrac{m(v-u)}{t}$.", "the relation between force and change of momentum",
  [r"$F = \dfrac{m(v-u)}{t} = \dfrac{@m@(@v@-@u@)}{@t@}$", r"$F = @ans@\ \text{N}$"])
t("work_cos", "physics", "HE", "Work, energy and power", "work force displacement angle", "F=10:100:10 s=2:20:2 th=30:60:30",
  r"A force of $@F@\ \text{N}$ acts on a body at an angle of $@th@^{\circ}$ to the direction of motion and displaces it by $@s@\ \text{m}$. Calculate the work done.",
  "F*s*cos(rad(th))", r"\text{J}", "F*s|F*s*sin(rad(th))|F*s*cos(th)|F*s*cos(rad(th))/2",
  r"The work done by a constant force is $W = Fs\cos\theta$, where $\theta$ is the angle between force and displacement.", "work done by a constant force",
  [r"$W = Fs\cos\theta = @F@\times@s@\times\cos @th@^{\circ}$", r"$W = @ans@\ \text{J}$"])
t("power_wt", "physics", "SHE", "Work, energy and power", "power work time", "W=600:6000:600 t=10:60:10",
  r"A machine does $@W@\ \text{J}$ of work in $@t@\ \text{s}$. What is its power output?",
  "W/t", r"\text{W}", "W*t|t/W|W/(2*t)",
  r"Power is the rate of doing work, $P = \dfrac{W}{t}$.", "power",
  [r"$P = \dfrac{W}{t} = \dfrac{@W@}{@t@}$", r"$P = @ans@\ \text{W}$"])
t("centripetal", "physics", "HE", "Circular motion", "circular motion centripetal force", "m=1:10:1 v=2:20:2 r=2:10:2",
  r"A body of mass $@m@\ \text{kg}$ moves in a circle of radius $@r@\ \text{m}$ with a uniform speed of $@v@\ \text{m s}^{-1}$. Find the centripetal force.",
  "m*v**2/r", r"\text{N}", "m*v/r|m*v**2*r|m*v**2/(2*r)|m*v/r**2",
  r"The centripetal force on a body of mass $m$ moving with speed $v$ in a circle of radius $r$ is $F = \dfrac{mv^{2}}{r}$.", "centripetal force",
  [r"$F = \dfrac{mv^{2}}{r} = \dfrac{@m@\times@v@^{2}}{@r@}$", r"$F = @ans@\ \text{N}$"])
t("range", "physics", "HE", "Projectile motion", "projectile motion range", "u=10:50:10 th=15:60:15",
  r"A projectile is launched with a speed of $@u@\ \text{m s}^{-1}$ at an angle of $@th@^{\circ}$ above the horizontal on level ground. Find its horizontal range. (Take $g = 9.8\ \text{m s}^{-2}$.)",
  "u**2*sin(rad(2*th))/9.8", r"\text{m}", "u**2*sin(rad(th))/9.8|u**2/9.8|u*sin(rad(2*th))/9.8|u**2*sin(rad(2*th))/(2*9.8)",
  r"The horizontal range of a projectile on level ground is $R = \dfrac{u^{2}\sin 2\theta}{g}$.", "the range of a projectile",
  [r"$R = \dfrac{u^{2}\sin 2\theta}{g} = \dfrac{@u@^{2}\sin(2\times@th@^{\circ})}{9.8}$", r"$R = @ans@\ \text{m}$"])
t("ohm", "physics electrical", "SHE", "Current electricity", "current electricity ohm resistance voltage", "V=6:48:6 R=2:12:2",
  r"A potential difference of $@V@\ \text{V}$ is applied across a resistor of $@R@\ \Omega$. Find the current flowing through it.",
  "V/R", r"\text{A}", "V*R|R/V|V/(2*R)",
  r"Ohm's law states that the current through a conductor is proportional to the potential difference across it, $V = IR$.", "Ohm's law",
  [r"$I = \dfrac{V}{R} = \dfrac{@V@}{@R@}$", r"$I = @ans@\ \text{A}$"])
t("res_par", "physics electrical", "SHE", "Current electricity", "resistors parallel combination circuit", "R1=2:20:2 R2=3:30:3",
  r"Two resistors of $@R1@\ \Omega$ and $@R2@\ \Omega$ are connected in parallel. Find their equivalent resistance.",
  "1/(1/R1+1/R2)", r"\Omega", "R1+R2|(R1+R2)/2|R1*R2|1/(R1+R2)",
  r"For resistors in parallel, $\dfrac{1}{R_{eq}} = \dfrac{1}{R_1} + \dfrac{1}{R_2}$.", "the equivalent resistance of resistors in parallel",
  [r"$\dfrac{1}{R_{eq}} = \dfrac{1}{@R1@} + \dfrac{1}{@R2@}$", r"$R_{eq} = @ans@\ \Omega$"])
t("res_ser", "physics electrical", "SHE", "Current electricity", "resistors series combination circuit", "R1=2:20:2 R2=3:30:3 R3=1:10:1",
  r"Three resistors of $@R1@\ \Omega$, $@R2@\ \Omega$ and $@R3@\ \Omega$ are connected in series. Calculate the equivalent resistance.",
  "R1+R2+R3", r"\Omega", "1/(1/R1+1/R2+1/R3)|R1*R2*R3|(R1+R2+R3)/3",
  r"For resistors in series the equivalent resistance is the sum, $R_{eq} = R_1 + R_2 + R_3$.", "the equivalent resistance of resistors in series",
  [r"$R_{eq} = R_1+R_2+R_3 = @R1@+@R2@+@R3@$", r"$R_{eq} = @ans@\ \Omega$"])
t("joule", "physics electrical", "SHE", "Current electricity", "heating power joule current", "I=1:10:1 R=2:20:2",
  r"A current of $@I@\ \text{A}$ flows through a resistor of $@R@\ \Omega$. Find the power dissipated as heat.",
  "I**2*R", r"\text{W}", "I*R|2*I*R|I**2/R|I*R**2",
  r"The power dissipated in a resistor is $P = I^{2}R$.", "Joule's heating law",
  [r"$P = I^{2}R = @I@^{2}\times@R@$", r"$P = @ans@\ \text{W}$"])
t("cap_energy", "physics electrical", "HE", "Capacitors", "capacitor energy capacitance electrostatics", "C=2:20:2 V=10:100:10",
  r"A capacitor of capacitance $@C@\ \mu\text{F}$ is charged to a potential difference of $@V@\ \text{V}$. Calculate the energy stored in it.",
  "0.5*C*V**2", r"\mu\text{J}", "C*V**2|0.5*C*V|C*V|0.5*C**2*V",
  r"The energy stored in a charged capacitor is $U = \tfrac{1}{2}CV^{2}$.", "the energy stored in a capacitor",
  [r"$U = \tfrac{1}{2}CV^{2} = \tfrac{1}{2}\times@C@\times@V@^{2}$", r"$U = @ans@\ \mu\text{J}$"])
t("coulomb", "physics", "HE", "Electrostatics", "coulomb electrostatics electric force charge", "q1=1:9:1 q2=1:9:1 r=1:5:1",
  r"Two point charges of $@q1@\ \mu\text{C}$ and $@q2@\ \mu\text{C}$ are placed $@r@\ \text{m}$ apart in air. Find the force between them. (Take $k = 9\times10^{9}\ \text{N m}^{2}\text{C}^{-2}$.)",
  "9*q1*q2/(1000*r**2)", r"\text{N}", "9*q1*q2/(1000*r)|9*q1*q2/(100*r**2)|9*q1*q2/(1000*r**2)*2|9*q1*q2/(10000*r**2)",
  r"Coulomb's law gives the force between two point charges, $F = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q_1q_2}{r^{2}}$.", "Coulomb's law",
  [r"$F = \dfrac{k q_1 q_2}{r^{2}} = \dfrac{9\times10^{9}\times@q1@\times10^{-6}\times@q2@\times10^{-6}}{@r@^{2}}$", r"$F = @ans@\ \text{N}$"])
t("wave_v", "physics", "SHE", "Waves", "wave speed frequency wavelength", "f=100:1000:50 lam=0.5:4:0.5",
  r"A wave has a frequency of $@f@\ \text{Hz}$ and a wavelength of $@lam@\ \text{m}$. Find its speed.",
  "f*lam", r"\text{m s}^{-1}", "f/lam|f+lam|lam/f",
  r"The speed of a wave is the product of frequency and wavelength, $v = f\lambda$.", "the wave equation",
  [r"$v = f\lambda = @f@\times@lam@$", r"$v = @ans@\ \text{m s}^{-1}$"])
t("pendulum", "physics", "HE", "Oscillations", "pendulum simple harmonic oscillation period", "L=0.5:4:0.5",
  r"Find the time period of a simple pendulum of length $@L@\ \text{m}$. (Take $g = 9.8\ \text{m s}^{-2}$.)",
  "2*pi*sqrt(L/9.8)", r"\text{s}", "sqrt(L/9.8)|2*pi*sqrt(L*9.8)|pi*sqrt(L/9.8)|2*pi*L/9.8",
  r"The time period of a simple pendulum is $T = 2\pi\sqrt{\dfrac{L}{g}}$.", "the time period of a simple pendulum",
  [r"$T = 2\pi\sqrt{\dfrac{L}{g}} = 2\pi\sqrt{\dfrac{@L@}{9.8}}$", r"$T = @ans@\ \text{s}$"])
t("snell", "physics", "HE", "Refraction of light", "refraction light snell refractive index optics", "i=30:60:15 r=15:30:5",
  r"A ray of light incident at $@i@^{\circ}$ in air is refracted at $@r@^{\circ}$ in a medium. Find the refractive index of the medium.",
  "sin(rad(i))/sin(rad(r))", "", "sin(rad(r))/sin(rad(i))|i/r|cos(rad(i))/cos(rad(r))|sin(rad(i))/sin(rad(r))*2", 
  r"Snell's law gives the refractive index as $n = \dfrac{\sin i}{\sin r}$.", "Snell's law",
  [r"$n = \dfrac{\sin i}{\sin r} = \dfrac{\sin @i@^{\circ}}{\sin @r@^{\circ}}$", r"$n = @ans@$"], cond="ans>1")
t("lens", "physics", "HE", "Lenses", "lens optics image convex formula", "f=5:30:5 d=20:60:5",
  r"An object is placed $@d@\ \text{cm}$ in front of a convex lens of focal length $@f@\ \text{cm}$. Find the distance of the real image from the lens.",
  "1/(1/f-1/d)", r"\text{cm}", "f*d/(f+d)|d-f|d+f|f*d/(d-f)/2",
  r"The lens formula (Cartesian sign convention) is $\dfrac{1}{f} = \dfrac{1}{v} - \dfrac{1}{u}$.", "the lens formula",
  [r"$\dfrac{1}{v} = \dfrac{1}{f} + \dfrac{1}{u} = \dfrac{1}{@f@} - \dfrac{1}{@d@}$", r"$v = @ans@\ \text{cm}$"], cond="d>f and ans>0")
t("young", "physics", "HE", "Interference of light", "interference young double slit fringe optics wave", "lam=400:700:100 D=1:3:1 d=1:4:1",
  r"In Young's double-slit experiment light of wavelength $@lam@\ \text{nm}$ is used, the slits are $@d@\ \text{mm}$ apart and the screen is $@D@\ \text{m}$ away. Find the fringe width.",
  "lam*D/(d*1000)", r"\text{mm}", "lam*d/(D*1000)|lam*D*d/1000|lam*D/d|lam*D/(2*d*1000)",
  r"In Young's double-slit experiment the fringe width is $\beta = \dfrac{\lambda D}{d}$.", "the fringe width in Young's double-slit experiment",
  [r"$\beta = \dfrac{\lambda D}{d} = \dfrac{@lam@\times10^{-9}\times@D@}{@d@\times10^{-3}}$", r"$\beta = @ans@\ \text{mm}$"])
t("photo", "physics", "HE", "Photoelectric effect", "photoelectric photon quantum modern physics", "lam=200:400:50 phi=2:4:0.5",
  r"Light of wavelength $@lam@\ \text{nm}$ falls on a metal of work function $@phi@\ \text{eV}$. Find the maximum kinetic energy of the emitted electrons. (Use $hc = 1240\ \text{eV nm}$.)",
  "1240/lam-phi", r"\text{eV}", "1240/lam+phi|1240/lam|lam/1240-phi|phi-1240/lam",
  r"Einstein's photoelectric equation is $K_{max} = h f - \phi = \dfrac{hc}{\lambda} - \phi$.", "Einstein's photoelectric equation",
  [r"$K_{max} = \dfrac{hc}{\lambda} - \phi = \dfrac{1240}{@lam@} - @phi@$", r"$K_{max} = @ans@\ \text{eV}$"])
t("debroglie", "physics", "HE", "Modern physics", "de broglie wave electron matter modern physics", "V=100:900:100",
  r"Find the de Broglie wavelength of an electron accelerated from rest through a potential difference of $@V@\ \text{V}$. (Use $\lambda = 1.227/\sqrt{V}\ \text{nm}$ with $V$ in volts.)",
  "1.227/sqrt(V)", r"\text{nm}", "1.227/V|1.227*sqrt(V)|12.27/sqrt(V)|1.227/sqrt(V)/2",
  r"The de Broglie wavelength of an electron accelerated through $V$ volts is $\lambda = \dfrac{h}{\sqrt{2meV}} \approx \dfrac{1.227}{\sqrt{V}}\ \text{nm}$.", "the de Broglie wavelength of an electron",
  [r"$\lambda = \dfrac{1.227}{\sqrt{V}} = \dfrac{1.227}{\sqrt{@V@}}$", r"$\lambda = @ans@\ \text{nm}$"])
t("halflife", "physics", "HE", "Radioactivity", "radioactivity decay half life nuclear", "N0=800:6400:800 T=2:10:2 k=1:4:1", 
  r"A radioactive sample initially has $@N0@$ nuclei and its half-life is $@T@$ days. How many nuclei remain after $@t@$ days?",
  "N0/2**k", "", "N0/(2*k)|N0/k|N0*k/2|N0/2**(k+1)",
  r"The number of undecayed nuclei after $n$ half-lives is $N = N_0\left(\tfrac{1}{2}\right)^{n}$.", "the law of radioactive decay",
  [r"$n = \dfrac{t}{T_{1/2}} = \dfrac{@t@}{@T@} = @k@$", r"$N = N_0\left(\tfrac{1}{2}\right)^{n} = @N0@\times\tfrac{1}{2^{@k@}} = @ans@$"], derived="t=k*T")
t("transformer", "physics electrical", "HE", "Electromagnetic induction", "transformer induction alternating current", "Vp=100:240:20 Np=100:500:100 Ns=200:1000:200",
  r"A transformer has $@Np@$ turns in the primary and $@Ns@$ turns in the secondary. If the primary voltage is $@Vp@\ \text{V}$, find the secondary voltage.",
  "Vp*Ns/Np", r"\text{V}", "Vp*Np/Ns|Vp+Ns-Np|Vp*Ns*Np|Vp/Ns*Np",
  r"For an ideal transformer $\dfrac{V_s}{V_p} = \dfrac{N_s}{N_p}$.", "the transformer equation",
  [r"$V_s = V_p\dfrac{N_s}{N_p} = @Vp@\times\dfrac{@Ns@}{@Np@}$", r"$V_s = @ans@\ \text{V}$"])
t("bil", "physics electrical", "HE", "Magnetic effects of current", "magnetic force wire current field", "B=10:90:10 I=1:10:1 L=10:50:10",
  r"A straight wire of length $@L@\ \text{cm}$ carrying a current of $@I@\ \text{A}$ is placed perpendicular to a magnetic field of $@B@\ \text{mT}$. Find the force on the wire.",
  "B*I*L/100000", r"\text{N}", "B*I*L/1000|B*I*L/10000|B*I*L/100|B*I*L/1000000",
  r"The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$.", "the force on a current-carrying conductor in a magnetic field",
  [r"$F = BIL\sin 90^{\circ} = @B@\times10^{-3}\times@I@\times@L@\times10^{-2}$", r"$F = @ans@\ \text{N}$"])
t("gas_p", "physics chemistry", "HE", "Ideal gas", "gas ideal kinetic theory thermal", "n=1:5:1 T=250:400:50 V=10:50:10",
  r"Find the pressure of $@n@\ \text{mol}$ of an ideal gas confined in $@V@\ \text{L}$ at $@T@\ \text{K}$. (Take $R = 8.314\ \text{J mol}^{-1}\text{K}^{-1}$.)",
  "n*8.314*T/V", r"\text{kPa}", "n*8.314*T*V|n*T/V|n*8.314/(T*V)|n*8.314*T/(2*V)",
  r"For an ideal gas $PV = nRT$.", "the ideal gas equation",
  [r"$P = \dfrac{nRT}{V} = \dfrac{@n@\times8.314\times@T@}{@V@}$", r"$P = @ans@\ \text{kPa}$"])
t("heat_q", "physics chemistry", "SHE", "Heat", "heat specific capacity temperature calorimetry thermal", "m=100:500:100 dT=10:50:10",
  r"How much heat is required to raise the temperature of $@m@\ \text{g}$ of water by $@dT@\ ^{\circ}\text{C}$? (Specific heat capacity of water $= 4.2\ \text{J g}^{-1}\,^{\circ}\text{C}^{-1}$.)",
  "m*4.2*dT", r"\text{J}", "m*dT|4.2*dT|m*4.2*dT/1000|m*4.2/dT",
  r"The heat absorbed is $Q = mc\Delta T$.", "the heat absorbed by a substance",
  [r"$Q = mc\Delta T = @m@\times4.2\times@dT@$", r"$Q = @ans@\ \text{J}$"])
t("stress", "physics", "HE", "Elasticity", "stress elasticity force area wire", "F=1000:10000:1000 A=2:20:2",
  r"A force of $@F@\ \text{N}$ is applied normally to a cross-section of area $@A@\ \text{cm}^{2}$. Calculate the stress in MPa.",
  "F/A/100", r"\text{MPa}", "F/A|F*A/100|F/(A*100)|F/A/1000",
  r"Stress is the restoring force per unit area, $\sigma = \dfrac{F}{A}$.", "stress",
  [r"$\sigma = \dfrac{F}{A} = \dfrac{@F@}{@A@\times10^{-4}}\ \text{Pa}$", r"$\sigma = @ans@\ \text{MPa}$"])
t("pressure_h", "physics", "SHE", "Fluid pressure", "fluid pressure liquid depth density", "rho=800:1200:200 h=2:20:2",
  r"Find the gauge pressure at a depth of $@h@\ \text{m}$ in a liquid of density $@rho@\ \text{kg m}^{-3}$. (Take $g = 9.8\ \text{m s}^{-2}$.)",
  "rho*9.8*h/1000", r"\text{kPa}", "rho*9.8*h|rho*9.8/h/1000|rho*h/1000|rho*9.8*h/2000",
  r"The pressure at depth $h$ in a liquid of density $\rho$ is $P = \rho g h$.", "the pressure due to a liquid column",
  [r"$P = \rho g h = @rho@\times9.8\times@h@\ \text{Pa}$", r"$P = @ans@\ \text{kPa}$"])
t("continuity", "physics", "HE", "Fluid flow", "fluid flow continuity pipe bernoulli", "A1=10:40:10 v1=1:5:1 A2=2:5:1",
  r"Water flows at $@v1@\ \text{m s}^{-1}$ through a pipe of cross-section $@A1@\ \text{cm}^{2}$ which narrows to $@A2@\ \text{cm}^{2}$. Find the speed in the narrow part.",
  "A1*v1/A2", r"\text{m s}^{-1}", "A2*v1/A1|v1*(A1+A2)|A1*v1*A2|v1*A1/(2*A2)",
  r"The equation of continuity for an incompressible fluid is $A_1v_1 = A_2v_2$.", "the equation of continuity",
  [r"$v_2 = \dfrac{A_1v_1}{A_2} = \dfrac{@A1@\times@v1@}{@A2@}$", r"$v_2 = @ans@\ \text{m s}^{-1}$"])
t("lc_res", "physics electrical", "HE", "Alternating current", "resonance lc circuit alternating current frequency", "L=1:10:1 C=1:10:1",
  r"Find the resonant frequency of an LC circuit with $L = @L@\ \text{mH}$ and $C = @C@\ \mu\text{F}$.",
  "1/(2*pi*sqrt(L*C*1e-9))/1000", r"\text{kHz}", "1/(sqrt(L*C*1e-9))/1000|1/(2*pi*sqrt(L*C))/1000|1/(2*pi*L*C*1e-9)/1000|1/(2*pi*sqrt(L*C*1e-9))",
  r"The resonant frequency of an LC circuit is $f_0 = \dfrac{1}{2\pi\sqrt{LC}}$.", "the resonant frequency of an LC circuit",
  [r"$f_0 = \dfrac{1}{2\pi\sqrt{LC}} = \dfrac{1}{2\pi\sqrt{@L@\times10^{-3}\times@C@\times10^{-6}}}$", r"$f_0 = @ans@\ \text{kHz}$"])
t("xc", "physics electrical", "HE", "Alternating current", "capacitive reactance alternating current capacitor", "f=50:500:50 C=10:100:10",
  r"Calculate the capacitive reactance of a $@C@\ \mu\text{F}$ capacitor at a frequency of $@f@\ \text{Hz}$.",
  "1/(2*pi*f*C*1e-6)", r"\Omega", "1/(f*C*1e-6)|2*pi*f*C*1e-6|1/(2*pi*f*C)|1/(2*pi*f*C*1e-6)/2",
  r"Capacitive reactance is $X_C = \dfrac{1}{2\pi f C}$.", "capacitive reactance",
  [r"$X_C = \dfrac{1}{2\pi f C} = \dfrac{1}{2\pi\times@f@\times@C@\times10^{-6}}$", r"$X_C = @ans@\ \Omega$"])
t("z_rl", "physics electrical", "HE", "Alternating current", "impedance series rl circuit alternating current", "R=30:90:30 X=40:120:40",
  r"A resistor of $@R@\ \Omega$ is connected in series with an inductor of reactance $@X@\ \Omega$ across an AC source. Find the impedance of the circuit.",
  "sqrt(R**2+X**2)", r"\Omega", "R+X|R**2+X**2|sqrt(abs(R**2-X**2))|(R+X)/2",
  r"The impedance of a series RL circuit is $Z = \sqrt{R^{2} + X_L^{2}}$.", "the impedance of a series RL circuit",
  [r"$Z = \sqrt{R^{2}+X_L^{2}} = \sqrt{@R@^{2}+@X@^{2}}$", r"$Z = @ans@\ \Omega$"])
t("mirror", "physics", "HE", "Reflection of light", "mirror concave reflection image optics", "f=5:15:5 u=20:60:10",
  r"An object is placed $@u@\ \text{cm}$ from a concave mirror of focal length $@f@\ \text{cm}$. Find the distance of the real image from the mirror.",
  "1/(1/f-1/u)", r"\text{cm}", "f*u/(f+u)|u-f|u+f|f*u/(u-f)/2",
  r"The mirror formula (real-is-positive convention) is $\dfrac{1}{f} = \dfrac{1}{u} + \dfrac{1}{v}$.", "the mirror formula",
  [r"$\dfrac{1}{v} = \dfrac{1}{f} - \dfrac{1}{u} = \dfrac{1}{@f@} - \dfrac{1}{@u@}$", r"$v = @ans@\ \text{cm}$"], cond="u>f and ans>0")
# school science
t("speed_s", "physics science", "S", "Motion", "speed distance time motion", "d=100:900:100 t=10:60:10",
  r"A cyclist covers $@d@\ \text{m}$ in $@t@\ \text{s}$. Calculate the average speed.",
  "d/t", r"\text{m s}^{-1}", "d*t|t/d|d/(2*t)",
  r"Average speed is the total distance travelled divided by the total time taken, $v = \dfrac{d}{t}$.", "average speed",
  [r"$v = \dfrac{d}{t} = \dfrac{@d@}{@t@}$", r"$v = @ans@\ \text{m s}^{-1}$"])
t("density_s", "physics science", "S", "Matter", "density mass volume matter", "m=100:900:100 V=20:100:20",
  r"A block has a mass of $@m@\ \text{g}$ and a volume of $@V@\ \text{cm}^{3}$. Find its density.",
  "m/V", r"\text{g cm}^{-3}", "m*V|V/m|m/(2*V)",
  r"Density is mass per unit volume, $\rho = \dfrac{m}{V}$.", "density",
  [r"$\rho = \dfrac{m}{V} = \dfrac{@m@}{@V@}$", r"$\rho = @ans@\ \text{g cm}^{-3}$"])
t("pressure_s", "physics science", "S", "Pressure", "pressure force area", "F=100:900:100 A=2:10:2",
  r"A force of $@F@\ \text{N}$ acts uniformly on an area of $@A@\ \text{m}^{2}$. Calculate the pressure exerted.",
  "F/A", r"\text{Pa}", "F*A|A/F|F/(2*A)",
  r"Pressure is the force acting normally per unit area, $P = \dfrac{F}{A}$.", "pressure",
  [r"$P = \dfrac{F}{A} = \dfrac{@F@}{@A@}$", r"$P = @ans@\ \text{Pa}$"])

# ---------------------------------------------------------------- CHEMISTRY
t("moles_m", "chemistry science", "SHE", "Mole concept", "mole concept stoichiometry amount", "m=10:100:10 M=[18,44,58,98,180]",
  r"Calculate the number of moles in $@m@\ \text{g}$ of a substance whose molar mass is $@M@\ \text{g mol}^{-1}$.",
  "m/M", r"\text{mol}", "M/m|m*M|m/(2*M)",
  r"The amount of substance is $n = \dfrac{\text{mass}}{\text{molar mass}}$.", "the mole",
  [r"$n = \dfrac{m}{M} = \dfrac{@m@}{@M@}$", r"$n = @ans@\ \text{mol}$"])
t("molarity", "chemistry science", "HE", "Solutions", "molarity solution concentration", "m=4:40:4 V=100:500:100",
  r"$@m@\ \text{g}$ of NaOH (molar mass $40\ \text{g mol}^{-1}$) is dissolved in water to make $@V@\ \text{mL}$ of solution. Find its molarity.",
  "m/40/(V/1000)", r"\text{mol L}^{-1}", "m/40/V|m*40/(V/1000)|m/40*(V/1000)|m/(V/1000)",
  r"Molarity is the number of moles of solute per litre of solution, $M = \dfrac{n}{V(\text{L})}$.", "molarity",
  [r"$n = \dfrac{@m@}{40}\ \text{mol}$, $V = \dfrac{@V@}{1000}\ \text{L}$", r"$M = \dfrac{n}{V} = @ans@\ \text{mol L}^{-1}$"])
t("dilution", "chemistry science", "HE", "Solutions", "dilution molarity solution", "M1=2:12:2 V1=10:50:10 V2=100:500:100",
  r"$@V1@\ \text{mL}$ of a $@M1@\ \text{M}$ solution is diluted with water to $@V2@\ \text{mL}$. Find the new molarity.",
  "M1*V1/V2", r"\text{M}", "M1*V2/V1|M1*V1*V2|M1*(V2-V1)/V2|M1+V1/V2",
  r"On dilution the number of moles of solute is unchanged, so $M_1V_1 = M_2V_2$.", "the dilution law",
  [r"$M_2 = \dfrac{M_1V_1}{V_2} = \dfrac{@M1@\times@V1@}{@V2@}$", r"$M_2 = @ans@\ \text{M}$"])
t("ph_acid", "chemistry science", "HE", "Ionic equilibrium", "pH acid hydrogen ion ionic equilibrium", "c=[1,2,5] k=2:6:1",
  r"The hydrogen-ion concentration of a solution is $@c@\times10^{-@k@}\ \text{mol L}^{-1}$. Calculate its pH.",
  "-log10(c*10**(-k))", "", "k|-ln(c*10**(-k))|k+log10(c)|14-k",
  r"$\text{pH} = -\log_{10}[\text{H}^{+}]$.", "pH",
  [r"$\text{pH} = -\log_{10}[\text{H}^{+}] = -\log_{10}(@c@\times10^{-@k@})$", r"$\text{pH} = @ans@$"])
t("ph_base", "chemistry science", "HE", "Ionic equilibrium", "pH base hydroxide ionic equilibrium", "c=[1,2,5] k=2:6:1",
  r"The hydroxide-ion concentration of a solution at $25\,^{\circ}\text{C}$ is $@c@\times10^{-@k@}\ \text{mol L}^{-1}$. Calculate its pH.",
  "14+log10(c*10**(-k))", "", "-log10(c*10**(-k))|14-k|k|14+ln(c*10**(-k))",
  r"At $25\,^{\circ}\text{C}$, $\text{pH} + \text{pOH} = 14$ and $\text{pOH} = -\log_{10}[\text{OH}^{-}]$.", "the relation between pH and pOH",
  [r"$\text{pOH} = -\log_{10}(@c@\times10^{-@k@})$", r"$\text{pH} = 14 - \text{pOH} = @ans@$"])
t("gas_stp", "chemistry", "HE", "Mole concept", "gas volume stp mole concept gaseous", "m=11:88:11 M=[44,28,32,16,2]",
  r"Find the volume at STP occupied by $@m@\ \text{g}$ of a gas whose molar mass is $@M@\ \text{g mol}^{-1}$. (Molar volume at STP $= 22.4\ \text{L mol}^{-1}$.)",
  "m/M*22.4", r"\text{L}", "m*M*22.4|M/m*22.4|m/M*24.5|m/M/22.4",
  r"One mole of any ideal gas occupies $22.4\ \text{L}$ at STP.", "the molar volume of a gas at STP",
  [r"$n = \dfrac{@m@}{@M@}\ \text{mol}$", r"$V = n\times22.4 = @ans@\ \text{L}$"])
t("percent_comp", "chemistry science", "HE", "Mole concept", "percentage composition mass element compound", "n=1:4:1 A=[12,16,14,23] M=[44,60,80,100,120,180]",
  r"A compound has molar mass $@M@\ \text{g mol}^{-1}$ and each molecule contains $@n@$ atom(s) of an element of atomic mass $@A@$. Calculate the percentage by mass of that element.",
  "n*A/M*100", r"\%", "A/M*100|n*A*M/100|M/(n*A)*100|n*A/(M*100)",
  r"Percentage composition is $\dfrac{\text{mass of element in one mole}}{\text{molar mass}}\times100$.", "percentage composition",
  [r"$\% = \dfrac{nA}{M}\times100 = \dfrac{@n@\times@A@}{@M@}\times100$", r"$\% = @ans@\ \%$"], cond="ans<100 and ans>0")
t("boyle", "chemistry physics", "SHE", "Gaseous state", "boyle gas pressure volume gaseous state", "P1=1:5:1 V1=2:10:2 P2=2:8:2",
  r"A gas occupies $@V1@\ \text{L}$ at $@P1@\ \text{atm}$. What volume will it occupy at $@P2@\ \text{atm}$ if the temperature is constant?",
  "P1*V1/P2", r"\text{L}", "P2*V1/P1|P1*V1*P2|V1*(P1+P2)|P1*V1/(2*P2)",
  r"Boyle's law states that at constant temperature $P_1V_1 = P_2V_2$.", "Boyle's law",
  [r"$V_2 = \dfrac{P_1V_1}{P_2} = \dfrac{@P1@\times@V1@}{@P2@}$", r"$V_2 = @ans@\ \text{L}$"])
t("charles", "chemistry physics", "SHE", "Gaseous state", "charles gas temperature volume gaseous state", "V1=2:10:2 T1=250:350:50 T2=300:500:50",
  r"A gas occupies $@V1@\ \text{L}$ at $@T1@\ \text{K}$. Find its volume at $@T2@\ \text{K}$ at constant pressure.",
  "V1*T2/T1", r"\text{L}", "V1*T1/T2|V1*(T2-T1)|V1+T2-T1|V1*T2/(2*T1)",
  r"Charles' law states that at constant pressure $\dfrac{V_1}{T_1} = \dfrac{V_2}{T_2}$ (T in kelvin).", "Charles' law",
  [r"$V_2 = V_1\dfrac{T_2}{T_1} = @V1@\times\dfrac{@T2@}{@T1@}$", r"$V_2 = @ans@\ \text{L}$"], cond="ans>0 and T1!=T2")
t("half_first", "chemistry", "HE", "Chemical kinetics", "kinetics rate constant first order half life", "k=0.01:0.09:0.01",
  r"The rate constant of a first-order reaction is $@k@\ \text{min}^{-1}$. Calculate its half-life.",
  "0.693/k", r"\text{min}", "1/k|0.693*k|k/0.693|0.693/(2*k)",
  r"For a first-order reaction $t_{1/2} = \dfrac{0.693}{k}$.", "the half-life of a first-order reaction",
  [r"$t_{1/2} = \dfrac{0.693}{k} = \dfrac{0.693}{@k@}$", r"$t_{1/2} = @ans@\ \text{min}$"])
t("faraday", "chemistry", "HE", "Electrochemistry", "faraday electrolysis electrochemistry deposition copper", "I=1:5:1 tm=10:60:10",
  r"Calculate the mass of copper deposited when a current of $@I@\ \text{A}$ is passed through $\text{CuSO}_4$ solution for $@tm@$ minutes. (Cu $= 63.5$, $F = 96500\ \text{C mol}^{-1}$.)",
  "63.5*I*tm*60/(2*96500)", r"\text{g}", "63.5*I*tm/(2*96500)|63.5*I*tm*60/96500|63.5*I*tm*60/(3*96500)|63.5*I*tm*60*2/96500",
  r"Faraday's first law gives $m = \dfrac{M I t}{nF}$.", "Faraday's first law of electrolysis",
  [r"$m = \dfrac{MIt}{nF} = \dfrac{63.5\times@I@\times@tm@\times60}{2\times96500}$", r"$m = @ans@\ \text{g}$"])

# ---------------------------------------------------------------- MATHEMATICS
t("quad_root", "maths", "SHE", "Quadratic equations", "quadratic equation roots algebra", "a=1:9:1 b=1:9:1",
  r"Find the larger root of the equation $x^{2} - @s@x + @p@ = 0$.",
  "max(a,b)", "", "min(a,b)|a+b|a*b|max(a,b)+1",
  r"A quadratic $x^{2} - (\alpha+\beta)x + \alpha\beta = 0$ has roots $\alpha$ and $\beta$.", "the relation between the roots and coefficients of a quadratic equation",
  [r"The equation factorises as $(x-@a@)(x-@b@) = 0$.", r"The larger root is $x = @ans@$."], derived="s=a+b;p=a*b", cond="a!=b")
t("disc", "maths", "HE", "Quadratic equations", "discriminant quadratic nature roots", "a=1:5:1 b=2:12:1 c=1:6:1",
  r"Find the discriminant of the equation $@a@x^{2} + @b@x + @c@ = 0$.",
  "b**2-4*a*c", "", "b**2+4*a*c|b**2-2*a*c|4*a*c-b**2|b-4*a*c",
  r"The discriminant of $ax^{2}+bx+c=0$ is $D = b^{2} - 4ac$.", "the discriminant of a quadratic equation",
  [r"$D = b^{2}-4ac = @b@^{2} - 4\times@a@\times@c@$", r"$D = @ans@$"], cond="ans!=0")
t("ap_n", "maths", "SHE", "Sequences and series", "arithmetic progression sequence series term", "a=1:10:1 d=2:7:1 n=10:25:1",
  r"Find the $@n@$th term of the arithmetic progression with first term $@a@$ and common difference $@d@$.",
  "a+(n-1)*d", "", "a+n*d|a*(n-1)*d|a+(n+1)*d|a+(n-1)*d+d",
  r"The $n$th term of an arithmetic progression is $a_n = a + (n-1)d$.", "the general term of an arithmetic progression",
  [r"$a_n = a + (n-1)d = @a@ + (@n@-1)\times@d@$", r"$a_{@n@} = @ans@$"])
t("ap_sum", "maths", "SHE", "Sequences and series", "arithmetic progression sum series", "a=1:10:1 d=1:6:1 n=8:20:1",
  r"Find the sum of the first $@n@$ terms of the arithmetic progression with first term $@a@$ and common difference $@d@$.",
  "n/2*(2*a+(n-1)*d)", "", "n*(2*a+(n-1)*d)|n/2*(a+(n-1)*d)|n/2*(2*a+n*d)|n/2*(2*a-(n-1)*d)",
  r"The sum of the first $n$ terms of an arithmetic progression is $S_n = \dfrac{n}{2}\left[2a + (n-1)d\right]$.", "the sum of an arithmetic progression",
  [r"$S_n = \dfrac{n}{2}[2a+(n-1)d] = \dfrac{@n@}{2}[2\times@a@+(@n@-1)\times@d@]$", r"$S_{@n@} = @ans@$"])
t("gp_n", "maths", "SHE", "Sequences and series", "geometric progression sequence term ratio", "a=2:5:1 r=2:3:1 n=4:8:1",
  r"Find the $@n@$th term of the geometric progression with first term $@a@$ and common ratio $@r@$.",
  "a*r**(n-1)", "", "a*r**n|a*r*(n-1)|(a*r)**(n-1)|a*r**(n-2)",
  r"The $n$th term of a geometric progression is $a_n = ar^{n-1}$.", "the general term of a geometric progression",
  [r"$a_n = ar^{n-1} = @a@\times@r@^{@n@-1}$", r"$a_{@n@} = @ans@$"])
t("gp_inf", "maths", "HE", "Sequences and series", "geometric series infinite sum convergent", "a=1:10:1 q=2:6:1",
  r"Find the sum to infinity of the geometric series with first term $@a@$ and common ratio $\dfrac{1}{@q@}$.",
  "a/(1-1/q)", "", "a/(1+1/q)|a*q|a/(1/q)|a*(1-1/q)",
  r"The sum to infinity of a geometric series with $|r|<1$ is $S_\infty = \dfrac{a}{1-r}$.", "the sum to infinity of a geometric series",
  [r"$S_\infty = \dfrac{a}{1-r} = \dfrac{@a@}{1-\frac{1}{@q@}}$", r"$S_\infty = @ans@$"])
t("deriv_pt", "maths", "HE", "Derivatives", "derivative differentiation calculus slope tangent", "a=1:5:1 b=1:6:1 x0=1:4:1",
  r"If $f(x) = @a@x^{3} + @b@x^{2}$, find $f'(@x0@)$.",
  "3*a*x0**2+2*b*x0", "", "a*x0**3+b*x0**2|3*a*x0+2*b|3*a*x0**2+b*x0|3*a*x0**2+2*b",
  r"By the power rule $\dfrac{d}{dx}x^{n} = nx^{n-1}$.", "the power rule of differentiation",
  [r"$f'(x) = 3\times@a@x^{2} + 2\times@b@x$", r"$f'(@x0@) = @ans@$"])
t("integral", "maths", "HE", "Integration", "integral integration definite calculus area", "a=3:9:3 b=2:8:2 k=1:4:1",
  r"Evaluate $\displaystyle\int_{0}^{@k@}\left(@a@x^{2} + @b@x\right)dx$.",
  "a*k**3/3+b*k**2/2", "", "a*k**3+b*k**2|a*k**2+b*k|a*k**3/3+b*k**2|a*k**3/3-b*k**2/2",
  r"By the power rule of integration $\displaystyle\int x^{n}dx = \dfrac{x^{n+1}}{n+1}$.", "the power rule of integration",
  [r"$\displaystyle\int_0^{@k@}(@a@x^{2}+@b@x)dx = \left[\dfrac{@a@x^{3}}{3} + \dfrac{@b@x^{2}}{2}\right]_0^{@k@}$", r"$= @ans@$"])
t("dist", "maths", "SHE", "Coordinate geometry", "distance coordinate geometry points straight line", "x1=0:4:1 y1=0:4:1 x2=5:9:1 y2=5:9:1",
  r"Find the distance between the points $(@x1@, @y1@)$ and $(@x2@, @y2@)$.",
  "sqrt((x2-x1)**2+(y2-y1)**2)", "", "(x2-x1)+(y2-y1)|(x2-x1)**2+(y2-y1)**2|sqrt((x2+x1)**2+(y2+y1)**2)|sqrt((x2-x1)**2-(y2-y1)**2)",
  r"The distance between $(x_1,y_1)$ and $(x_2,y_2)$ is $d = \sqrt{(x_2-x_1)^{2} + (y_2-y_1)^{2}}$.", "the distance formula",
  [r"$d = \sqrt{(@x2@-@x1@)^{2} + (@y2@-@y1@)^{2}}$", r"$d = @ans@$"])
t("slope", "maths", "SHE", "Coordinate geometry", "slope gradient straight line coordinate", "x1=0:4:1 y1=0:6:1 x2=5:9:1 y2=7:15:1",
  r"Find the slope of the line joining the points $(@x1@, @y1@)$ and $(@x2@, @y2@)$.",
  "(y2-y1)/(x2-x1)", "", "(x2-x1)/(y2-y1)|(y2+y1)/(x2+x1)|(y2-y1)*(x2-x1)|(y1-y2)/(x2-x1)",
  r"The slope of the line through $(x_1,y_1)$ and $(x_2,y_2)$ is $m = \dfrac{y_2-y_1}{x_2-x_1}$.", "the slope formula",
  [r"$m = \dfrac{y_2-y_1}{x_2-x_1} = \dfrac{@y2@-@y1@}{@x2@-@x1@}$", r"$m = @ans@$"])
t("tri_area", "maths", "HE", "Coordinate geometry", "area triangle vertices coordinate geometry", "x1=0:5:1 y1=0:5:1 x2=3:9:1 y2=0:5:1 x3=0:9:1 y3=4:9:1",
  r"Find the area of the triangle with vertices $(@x1@, @y1@)$, $(@x2@, @y2@)$ and $(@x3@, @y3@)$.",
  "0.5*abs(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))", r"\text{sq. units}", "abs(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))|0.5*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))+1|0.5*abs(x1*y2-x2*y1)",
  r"The area of a triangle with vertices $(x_1,y_1),(x_2,y_2),(x_3,y_3)$ is $\tfrac{1}{2}\left|x_1(y_2-y_3)+x_2(y_3-y_1)+x_3(y_1-y_2)\right|$.", "the area of a triangle in coordinate geometry",
  [r"$A = \tfrac{1}{2}|x_1(y_2-y_3)+x_2(y_3-y_1)+x_3(y_1-y_2)|$", r"$A = @ans@\ \text{sq. units}$"], cond="ans>0")
t("comb", "maths", "HE", "Permutation and combination", "combination permutation counting selection", "n=6:12:1 r=2:4:1",
  r"In how many ways can $@r@$ students be selected from a group of $@n@$ students?",
  "comb(n,r)", "", "perm(n,r)|n**r|comb(n+1,r)|comb(n,r)*r",
  r"The number of ways of choosing $r$ objects from $n$ is $^{n}C_r = \dfrac{n!}{r!(n-r)!}$.", "the combination formula",
  [r"$^{@n@}C_{@r@} = \dfrac{@n@!}{@r@!\,(@n@-@r@)!}$", r"$= @ans@$"])
t("prob2", "maths", "SHE", "Probability", "probability balls selection chance", "r=3:8:1 b=2:7:1",
  r"A bag contains $@r@$ red and $@b@$ blue balls. Two balls are drawn at random without replacement. Find the probability that both are red.",
  "comb(r,2)/comb(r+b,2)", "", "(r/(r+b))**2|r/(r+b)|comb(r,2)/(r+b)**2|2*r/(r+b)/(r+b-1)",
  r"Probability $= \dfrac{\text{favourable outcomes}}{\text{total outcomes}}$.", "the classical definition of probability",
  [r"$P = \dfrac{^{@r@}C_2}{^{@n@}C_2}$ where $n = @r@+@b@$", r"$P = @ans@$"], derived="n=r+b", cond="r>1 and ans<1")
t("det2", "maths", "SHE", "Matrices and determinants", "determinant matrix matrices", "a=1:9:1 b=1:9:1 c=1:9:1 d=1:9:1",
  r"Find the value of the determinant $\begin{vmatrix} @a@ & @b@ \\ @c@ & @d@ \end{vmatrix}$.",
  "a*d-b*c", "", "a*d+b*c|a*c-b*d|a*b-c*d|b*c-a*d",
  r"For a $2\times2$ matrix, $\begin{vmatrix} a & b \\ c & d \end{vmatrix} = ad - bc$.", "the determinant of a 2 by 2 matrix",
  [r"$\Delta = ad - bc = @a@\times@d@ - @b@\times@c@$", r"$\Delta = @ans@$"], cond="ans!=0")
t("comp_int", "maths accounting economics", "SHE", "Mathematics of finance", "compound interest finance percent amount", "P=1000:10000:1000 r=5:12:1 n=2:4:1",
  r"Find the amount when Rs. $@P@$ is invested for $@n@$ years at $@r@\%$ compound interest per annum.",
  "P*(1+r/100)**n", r"\text{ rupees}", "P*(1+n*r/100)|P*(r/100)**n|P*n*r/100|P*(1+r/100)**(n-1)",
  r"The amount under compound interest is $A = P\left(1+\dfrac{r}{100}\right)^{n}$.", "the compound interest formula",
  [r"$A = P\left(1+\dfrac{r}{100}\right)^{n} = @P@\left(1+\dfrac{@r@}{100}\right)^{@n@}$", r"$A = \text{Rs. }@ans@$"])
t("simple_int", "maths accounting economics", "S", "Mathematics of finance", "simple interest finance percent", "P=1000:10000:1000 r=4:12:1 n=2:6:1",
  r"Find the simple interest on Rs. $@P@$ for $@n@$ years at $@r@\%$ per annum.",
  "P*r*n/100", r"\text{ rupees}", "P*(1+r/100)**n|P*r/100|P*r*n/1000|P*(1+n*r/100)",
  r"Simple interest is $I = \dfrac{PTR}{100}$.", "the simple interest formula",
  [r"$I = \dfrac{PTR}{100} = \dfrac{@P@\times@n@\times@r@}{100}$", r"$I = \text{Rs. }@ans@$"])
t("sine_rule", "maths", "HE", "Trigonometry", "sine rule triangle trigonometry", "a=5:20:5 A=30:60:30 B=45:90:45",
  r"In a triangle $ABC$, $a = @a@\ \text{cm}$, $A = @A@^{\circ}$ and $B = @B@^{\circ}$. Find the side $b$.",
  "a*sin(rad(B))/sin(rad(A))", r"\text{cm}", "a*sin(rad(A))/sin(rad(B))|a*cos(rad(B))/cos(rad(A))|a*B/A|a*sin(rad(B))/sin(rad(A))/2",
  r"By the sine rule $\dfrac{a}{\sin A} = \dfrac{b}{\sin B}$.", "the sine rule",
  [r"$b = \dfrac{a\sin B}{\sin A} = \dfrac{@a@\sin @B@^{\circ}}{\sin @A@^{\circ}}$", r"$b = @ans@\ \text{cm}$"], cond="A!=B and A+B<180")
t("log_val", "maths", "SHE", "Logarithms", "logarithm logs indices", "b=[2,3,5] k=2:5:1",
  r"Evaluate $\log_{@b@} @x@$.",
  "k", "", "x/b|k+1|b*k|x-b",
  r"By definition $\log_b b^{k} = k$, i.e. $\log_b x = k \iff x = b^{k}$.", "the definition of a logarithm",
  [r"$@x@ = @b@^{@k@}$", r"$\log_{@b@}@x@ = @ans@$"], derived="x=b**k")
t("dot", "maths", "HE", "Vectors", "vector dot product scalar product", "a1=1:6:1 a2=1:6:1 a3=1:6:1 b1=1:6:1 b2=1:6:1 b3=1:6:1",
  r"Find the scalar product of $\vec{a} = @a1@\hat{i} + @a2@\hat{j} + @a3@\hat{k}$ and $\vec{b} = @b1@\hat{i} + @b2@\hat{j} + @b3@\hat{k}$.",
  "a1*b1+a2*b2+a3*b3", "", "a1*b2+a2*b3+a3*b1|a1+b1+a2+b2+a3+b3|(a1*b1)*(a2*b2)*(a3*b3)|a1*b1+a2*b2-a3*b3",
  r"The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$.", "the scalar product of two vectors",
  [r"$\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = @a1@\times@b1@+@a2@\times@b2@+@a3@\times@b3@$", r"$\vec{a}\cdot\vec{b} = @ans@$"])
t("limit", "maths", "HE", "Limits", "limit calculus continuity", "a=1:9:1",
  r"Evaluate $\displaystyle\lim_{x\to @a@}\dfrac{x^{2}-@a2@}{x-@a@}$.",
  "2*a", "", "a|a**2|2*a**2|a+1",
  r"$\dfrac{x^{2}-a^{2}}{x-a} = x + a$ for $x \ne a$, so the limit as $x \to a$ is $2a$.", "the limit of a difference quotient",
  [r"$\dfrac{x^{2}-@a2@}{x-@a@} = x+@a@$ for $x\ne@a@$", r"$\lim = @a@+@a@ = @ans@$"], derived="a2=a**2")
t("arc", "maths", "SHE", "Mensuration", "arc length circle sector mensuration", "r=2:10:2 th=30:150:30",
  r"Find the length of an arc of a circle of radius $@r@\ \text{cm}$ that subtends an angle of $@th@^{\circ}$ at the centre.",
  "r*pi*th/180", r"\text{cm}", "r*th|r*pi*th/90|r*pi*th/360|pi*th/180",
  r"The arc length is $l = r\theta$ with $\theta$ in radians, i.e. $l = \dfrac{\pi r\theta^{\circ}}{180}$.", "the arc length formula",
  [r"$l = \dfrac{\pi r\theta}{180} = \dfrac{\pi\times@r@\times@th@}{180}$", r"$l = @ans@\ \text{cm}$"])
t("sum_sq", "maths", "HE", "Sequences and series", "sum squares natural numbers series", "n=5:20:1",
  r"Find the value of $1^{2} + 2^{2} + 3^{2} + \cdots + @n@^{2}$.",
  "n*(n+1)*(2*n+1)/6", "", "n*(n+1)/2|(n*(n+1)/2)**2|n*(n+1)*(2*n+1)/3|n*(n+1)*(2*n-1)/6",
  r"The sum of the first $n$ squares is $\sum k^{2} = \dfrac{n(n+1)(2n+1)}{6}$.", "the formula for the sum of squares of natural numbers",
  [r"$\sum k^{2} = \dfrac{n(n+1)(2n+1)}{6} = \dfrac{@n@\times(@n@+1)\times(2\times@n@+1)}{6}$", r"$= @ans@$"])

# ---------------------------------------------------------------- COMPUTER SCIENCE
t("bin2dec", "cs", "all", "Number systems", "binary decimal number system conversion", "b4=0:1:1 b3=0:1:1 b2=0:1:1 b1=0:1:1 b0=0:1:1",
  r"Convert the binary number $@b4@@b3@@b2@@b1@@b0@_{2}$ to decimal.",
  "16*b4+8*b3+4*b2+2*b1+b0", "", "b4+2*b3+4*b2+8*b1+16*b0|16*b4+8*b3+4*b2+2*b1+b0+1|b4+b3+b2+b1+b0|32*b4+16*b3+8*b2+4*b1+2*b0",
  r"A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two).", "positional values in the binary number system",
  [r"$@b4@\times16+@b3@\times8+@b2@\times4+@b1@\times2+@b0@\times1$", r"$= @ans@$"], cond="ans>=5")
t("dl_time", "cs", "all", "Computer networks", "download time bandwidth network speed file transfer", "size=10:200:10 sp=2:20:2",
  r"How many seconds does it take to download a $@size@\ \text{MB}$ file over a connection of $@sp@\ \text{Mbps}$? (1 byte $= 8$ bits.)",
  "size*8/sp", r"\text{s}", "size/sp|size*sp|size*8*sp|size/(8*sp)",
  r"Transfer time is $\dfrac{\text{file size in bits}}{\text{bandwidth in bits per second}}$ and 1 byte $= 8$ bits.", "the data transfer time",
  [r"$t = \dfrac{@size@\times8\ \text{Mb}}{@sp@\ \text{Mbps}}$", r"$t = @ans@\ \text{s}$"])
t("subnet", "cs", "all", "Computer networks", "subnet ip address network hosts", "p=24:30:1",
  r"How many usable host addresses are available in an IPv4 subnet with prefix length $/@p@$?",
  "2**(32-p)-2", "", "2**(32-p)|2**(32-p)-1|2**p-2|2**(32-p)-4",
  r"An IPv4 subnet with prefix length $/p$ has $2^{32-p}-2$ usable hosts (network and broadcast addresses excluded).", "the number of usable hosts in a subnet",
  [r"$2^{32-@p@} - 2 = 2^{@hb@} - 2$", r"Usable hosts $= @ans@$"], derived="hb=32-p")
t("image_kb", "cs", "all", "Multimedia", "image size pixel bit depth multimedia graphics", "w=100:800:100 h=100:600:100 bpp=[8,16,24]",
  r"Find the uncompressed size, in KB, of a $@w@\times@h@$ pixel image with a colour depth of $@bpp@$ bits per pixel. (1 KB $= 1024$ bytes.)",
  "w*h*bpp/8/1024", r"\text{KB}", "w*h*bpp/8|w*h*bpp/1024|w*h*bpp/8/1024/8|w*h/8/1024",
  r"Image size in bytes is $\dfrac{\text{width}\times\text{height}\times\text{bits per pixel}}{8}$ and 1 KB $= 1024$ bytes.", "the size of an uncompressed bitmap image",
  [r"$\text{bits} = @w@\times@h@\times@bpp@$", r"$\text{KB} = \dfrac{\text{bits}}{8\times1024} = @ans@\ \text{KB}$"])

# ---------------------------------------------------------------- NURSING / CLINICAL
t("oral_dose", "nursing", "all", "Drug dosage calculation", "dosage drug oral medication calculation pharmacology", "D=50:400:50 H=100:250:50",
  r"A doctor orders $@D@\ \text{mg}$ of a drug. The syrup available contains $@H@\ \text{mg}$ in every $5\ \text{mL}$. How many millilitres should the nurse give?",
  "D/H*5", r"\text{mL}", "D/H|H/D*5|D*H/5|D*5",
  r"Dose to give $= \dfrac{\text{desired dose}}{\text{dose on hand}}\times\text{quantity of the stock volume}$.", "the basic dosage calculation formula",
  [r"$\dfrac{D}{H}\times Q = \dfrac{@D@}{@H@}\times5$", r"Volume $= @ans@\ \text{mL}$"])
t("iv_drip", "nursing", "all", "Intravenous therapy", "iv infusion drip rate drops fluid", "V=500:1000:250 th=4:8:2 DF=[10,15,20]",
  r"A nurse must infuse $@V@\ \text{mL}$ of IV fluid over $@th@$ hours using a set with a drop factor of $@DF@\ \text{drops mL}^{-1}$. Calculate the flow rate in drops per minute.",
  "V*DF/(th*60)", r"\text{drops min}^{-1}", "V*DF/th|V/(th*60)|V*DF/(th*6)|V*DF*th/60",
  r"Drip rate $= \dfrac{\text{volume (mL)}\times\text{drop factor}}{\text{time (min)}}$.", "the IV drip rate formula",
  [r"Time in minutes $= @th@\times60$", r"Rate $= \dfrac{@V@\times@DF@}{@th@\times60} = @ans@\ \text{drops min}^{-1}$"])
t("bmi", "nursing", "all", "Nutrition and assessment", "bmi body mass index nutrition assessment weight height", "w=45:95:5 h=150:190:10",
  r"Calculate the body mass index of a patient who weighs $@w@\ \text{kg}$ and is $@h@\ \text{cm}$ tall.",
  "w/(h/100)**2", r"\text{kg m}^{-2}", "w/(h/100)|w/h**2|w*(h/100)**2|w/(h/100)**2/2",
  r"Body mass index is $\text{BMI} = \dfrac{\text{weight (kg)}}{\text{height (m)}^{2}}$.", "body mass index",
  [r"Height $= @h@/100$ m", r"$\text{BMI} = \dfrac{@w@}{(@h@/100)^{2}} = @ans@\ \text{kg m}^{-2}$"])
t("paed_dose", "nursing", "all", "Paediatric dosage", "paediatric child dose weight mg/kg", "w=8:30:2 rate=10:50:5 n=[2,3,4]",
  r"A child weighing $@w@\ \text{kg}$ is prescribed $@rate@\ \text{mg kg}^{-1}$ per day in $@n@$ equally divided doses. Find the dose per administration.",
  "w*rate/n", r"\text{mg}", "w*rate|rate/n|w/n|w*rate*n",
  r"Paediatric dose $= \text{weight (kg)}\times\text{dose per kg per day}$, divided by the number of doses per day.", "the weight-based paediatric dose calculation",
  [r"Daily dose $= @w@\times@rate@\ \text{mg}$", r"Per dose $= \dfrac{@w@\times@rate@}{@n@} = @ans@\ \text{mg}$"])
t("inf_rate", "nursing", "all", "Intravenous therapy", "infusion pump rate ml per hour intravenous", "V=250:1000:250 th=2:8:2",
  r"Calculate the infusion pump rate in $\text{mL h}^{-1}$ to give $@V@\ \text{mL}$ over $@th@$ hours.",
  "V/th", r"\text{mL h}^{-1}", "V*th|th/V|V/(th*60)",
  r"Infusion rate $= \dfrac{\text{total volume}}{\text{time in hours}}$.", "the infusion rate formula",
  [r"Rate $= \dfrac{V}{t} = \dfrac{@V@}{@th@}$", r"Rate $= @ans@\ \text{mL h}^{-1}$"])
t("map", "nursing", "all", "Vital signs", "blood pressure mean arterial pressure vital signs cardiovascular", "S=100:140:10 Dd=60:90:10",
  r"A patient's blood pressure is $@S@/@Dd@\ \text{mmHg}$. Calculate the mean arterial pressure.",
  "(S+2*Dd)/3", r"\text{mmHg}", "(S+Dd)/2|(2*S+Dd)/3|S-Dd|(S+2*Dd)/2",
  r"Mean arterial pressure is $\text{MAP} = \dfrac{\text{SBP} + 2\times\text{DBP}}{3}$.", "mean arterial pressure",
  [r"$\text{MAP} = \dfrac{\text{SBP}+2\,\text{DBP}}{3} = \dfrac{@S@+2\times@Dd@}{3}$", r"$\text{MAP} = @ans@\ \text{mmHg}$"])
t("pulse_p", "nursing", "all", "Vital signs", "pulse pressure blood pressure vital signs", "S=110:150:10 Dd=60:90:10",
  r"A patient's blood pressure is $@S@/@Dd@\ \text{mmHg}$. Find the pulse pressure.",
  "S-Dd", r"\text{mmHg}", "S+Dd|(S+Dd)/2|(S+2*Dd)/3|S/Dd",
  r"Pulse pressure is the difference between systolic and diastolic pressure, $PP = SBP - DBP$.", "pulse pressure",
  [r"$PP = SBP - DBP = @S@ - @Dd@$", r"$PP = @ans@\ \text{mmHg}$"])
t("co", "nursing", "all", "Cardiovascular assessment", "cardiac output heart rate stroke volume cardiovascular", "HR=60:100:10 SV=50:90:10",
  r"A patient has a heart rate of $@HR@$ beats per minute and a stroke volume of $@SV@\ \text{mL}$ per beat. Calculate the cardiac output.",
  "HR*SV/1000", r"\text{L min}^{-1}", "HR*SV|HR/SV|HR*SV/100|HR+SV",
  r"Cardiac output is $CO = HR\times SV$.", "cardiac output",
  [r"$CO = HR\times SV = @HR@\times@SV@\ \text{mL min}^{-1}$", r"$CO = @ans@\ \text{L min}^{-1}$"])
t("pct_sol", "nursing chemistry", "all", "Drug dosage calculation", "percent solution concentration drug mg", "p=1:10:1 V=5:50:5",
  r"How many milligrams of drug are present in $@V@\ \text{mL}$ of a $@p@\%$ (w/v) solution?",
  "p*10*V", r"\text{mg}", "p*V|p*V/100|p*10*V/1000|p*100*V",
  r"A $p\%$ w/v solution contains $p\ \text{g}$ in $100\ \text{mL}$, i.e. $10p\ \text{mg mL}^{-1}$.", "percentage strength of a solution",
  [r"$@p@\%\ \text{w/v} = @p@\ \text{g}/100\ \text{mL} = @p10@\ \text{mg mL}^{-1}$", r"Drug $= @p10@\times@V@ = @ans@\ \text{mg}$"], derived="p10=p*10")

# ---------------------------------------------------------------- ACCOUNTING / ECONOMICS
t("depr", "accounting", "SHE", "Depreciation", "depreciation straight line accounting asset", "cost=50000:200000:25000 salv=5000:25000:5000 life=4:10:1",
  r"A machine costing Rs. $@cost@$ has an estimated scrap value of Rs. $@salv@$ and a useful life of $@life@$ years. Find the annual depreciation by the straight-line method.",
  "(cost-salv)/life", r"\text{ rupees}", "cost/life|(cost-salv)*life|(cost+salv)/life|(cost-salv)/(life+1)",
  r"Straight-line depreciation $= \dfrac{\text{cost} - \text{scrap value}}{\text{useful life}}$.", "the straight-line method of depreciation",
  [r"$\dfrac{\text{Cost}-\text{Scrap}}{\text{Life}} = \dfrac{@cost@-@salv@}{@life@}$", r"Annual depreciation $= \text{Rs. }@ans@$"])
t("profit_pct", "accounting economics maths", "S", "Profit and loss", "profit loss percent selling price cost price", "cp=200:2000:200 pr=10:50:10",
  r"An article bought for Rs. $@cp@$ is sold at a profit of $@pr@\%$. Find the selling price.",
  "cp*(1+pr/100)", r"\text{ rupees}", "cp*(1-pr/100)|cp+pr|cp*pr/100|cp/(1+pr/100)",
  r"Selling price $= \text{cost price}\times\left(1+\dfrac{\text{profit}\%}{100}\right)$.", "the relation between cost price, profit and selling price",
  [r"$SP = CP\left(1+\dfrac{P\%}{100}\right) = @cp@\left(1+\dfrac{@pr@}{100}\right)$", r"$SP = \text{Rs. }@ans@$"])
t("elasticity", "economics", "SHE", "Elasticity of demand", "price elasticity demand percentage change", "dq=20:60:10 dp=10:20:5",
  r"The price of a good rises by $@dp@\%$ and the quantity demanded falls by $@dq@\%$. Calculate the price elasticity of demand (in magnitude).",
  "dq/dp", "", "dp/dq|dq*dp|dq+dp|dq-dp",
  r"Price elasticity of demand is $E_d = \dfrac{\%\ \text{change in quantity demanded}}{\%\ \text{change in price}}$.", "price elasticity of demand",
  [r"$E_d = \dfrac{\%\Delta Q}{\%\Delta P} = \dfrac{@dq@}{@dp@}$", r"$E_d = @ans@$"])

DOMAINS = [["^(physics|engineering-physics)$", ["physics"]], ["electric|electron|circuit|instrument|machine|signals|electromagnetics", ["electrical"]],
           ["^(chemistry|engineering-chemistry)$", ["chemistry"]], ["^science$", ["physics", "chemistry"]],
           ["math|statistics|discrete|numerical", ["maths"]], ["computer|programming|gk-and-it|microprocessor|digital|logic|theory-of-computation|organization", ["cs"]],
           ["nursing|midwifery|health|nutrition|psychiatric|social-and|integrated", ["nursing"]], ["^accountancy$", ["accounting"]], ["^economics$", ["economics"]]]
LEVELS = {"C8": "S", "C9": "S", "C10": "S", "C11": "H", "C12": "H", "CEE": "HE", "IOE": "HE", "BE": "HE", "BCA": "HE", "BSN": "HEN"}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine", "param_templates.json")
    json.dump(dict(templates=T, domains=DOMAINS, levels=LEVELS), open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(T), "templates ->", out)
