#!/usr/bin/env python3
"""Appends the v5 template pack (physics, chemistry, maths, CS, electrical, civil/survey, nursing, accounting/economics) to engine/param_templates.json.
Idempotent. Each template is verified by eval/param_test.py (300 instances each: key==computed answer, 4 distinct options, same unit, no placeholders)."""
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine", "param_templates.json")
L = json.load(open(P, encoding="utf-8"))
NEW = []


def T(id, dom, lv, unit, kw, vars, stem, ans, u, wrong, law, lawname, sol, sig=3, cond="ans>0", derived=""):
    NEW.append(dict(id=id, dom=dom, lv=lv, unit=unit, kw=kw, vars=vars, derived=derived, stem=stem, ans=ans, u=u, wrong=wrong, law=law, lawname=lawname, sol=sol, sig=sig, cond=cond))


# ------------------------------------------------------------------ physics
T("power_vi", "physics electrical", "SHE", "Current electricity", ["power", "electric", "current", "electrical"], ["V=[6,12,24,110,220]", "I=1:10:1"],
  r"A device connected to a $@V@\ \text{V}$ supply draws a current of $@I@\ \text{A}$. Find the power consumed.", "V*I", r"\text{W}", ["V/I", "V+I", "V*I/2", "V*I*2"],
  r"Electrical power is $P = VI$.", "the formula for electrical power", [r"$P = VI = @V@\times @I@$", r"$P = @ans@\ \text{W}$"])
T("lens_power", "physics", "HE", "Refraction through lenses", ["lens", "power", "focal", "refraction", "optical"], ["f=[10,20,25,40,50,100]"],
  r"Find the power of a convex lens of focal length $@f@\ \text{cm}$.", "100/f", r"\text{D}", ["f/100", "1/f", "f", "100*f"],
  r"Power of a lens is $P = \dfrac{1}{f}$ with $f$ in metres (dioptre).", "the power of a lens", [r"$f = @f@\ \text{cm} = \dfrac{@f@}{100}\ \text{m}$", r"$P = \dfrac{1}{f} = @ans@\ \text{D}$"])
T("refr_index", "physics", "HE", "Refraction of light", ["refractive", "refraction", "speed of light", "index"], ["v=[1.2,1.25,1.5,2,2.5]"],
  r"The speed of light in a medium is $@v@\times10^{8}\ \text{m s}^{-1}$. Taking $c = 3\times10^{8}\ \text{m s}^{-1}$, find the refractive index of the medium.", "3/v", "", ["v/3", "3*v", "3-v", "3+v"],
  r"Refractive index is $n = \dfrac{c}{v}$.", "refractive index", [r"$n = \dfrac{c}{v} = \dfrac{3\times10^{8}}{@v@\times10^{8}}$", r"$n = @ans@$"])
T("latent_q", "physics chemistry", "SHE", "Heat and latent heat", ["latent", "heat", "melting", "vaporisation", "fusion"], ["m=[0.1,0.2,0.5,1,2,3]", "L=[334,2260]"],
  r"How much heat is needed to change $@m@\ \text{kg}$ of a substance having specific latent heat $@L@\ \text{kJ kg}^{-1}$ at its transition temperature?", "m*L", r"\text{kJ}", ["L/m", "m/L", "m+L", "m*L*2"],
  r"Heat absorbed during a change of state is $Q = mL$.", "the latent heat formula", [r"$Q = mL = @m@\times @L@$", r"$Q = @ans@\ \text{kJ}$"])
T("lin_expansion", "physics", "HE", "Thermal expansion", ["expansion", "thermal", "linear", "coefficient"], ["L=[1,2,5,10]", "a=[12,17,19,23]", "dT=[20,40,50,80,100]"],
  r"A rod of length $@L@\ \text{m}$ has a coefficient of linear expansion $@a@\times10^{-6}\ \text{K}^{-1}$. By how many millimetres does it expand when heated by $@dT@\ \text{K}$?", "L*a*dT/1000", r"\text{mm}",
  ["L*a*dT/100", "L*a*dT/10000", "a*dT/1000", "L*dT/1000"], r"Linear expansion is $\Delta L = L\alpha\,\Delta T$.", "linear expansion",
  [r"$\Delta L = L\alpha\Delta T = @L@\times @a@\times10^{-6}\times @dT@\ \text{m}$", r"$\Delta L = @ans@\ \text{mm}$"])
T("emf_internal", "physics electrical", "SHE", "Current electricity", ["internal resistance", "emf", "cell", "current", "circuit"], ["E=[6,12,24]", "R=[4,8,10,11]", "r=[1,2]"],
  r"A cell of emf $@E@\ \text{V}$ and internal resistance $@r@\ \Omega$ is connected to an external resistance of $@R@\ \Omega$. Find the current in the circuit.", "E/(R+r)", r"\text{A}", ["E/R", "E/(R-r)", "E*(R+r)", "E/r"],
  r"For a cell with internal resistance $I = \dfrac{E}{R + r}$.", "the current in a cell circuit", [r"$I = \dfrac{E}{R+r} = \dfrac{@E@}{@R@+@r@}$", r"$I = @ans@\ \text{A}$"])
T("max_height", "physics", "HE", "Projectile motion", ["projectile", "height", "motion"], ["u=[10,20,30,40,50]", "th=[30,45,60,90]"],
  r"A projectile is thrown with speed $@u@\ \text{m s}^{-1}$ at $@th@^{\circ}$ to the horizontal. Taking $g = 10\ \text{m s}^{-2}$, find the maximum height reached.", "u**2*sin(rad(th))**2/20", r"\text{m}",
  ["u**2*sin(rad(th))/20", "u**2/20", "u**2*sin(rad(th))**2/10", "u**2*cos(rad(th))**2/20"], r"Maximum height is $H = \dfrac{u^2\sin^2\theta}{2g}$.", "the maximum height of a projectile",
  [r"$H = \dfrac{u^2\sin^2\theta}{2g} = \dfrac{(@u@)^2\sin^2 @th@^{\circ}}{2\times10}$", r"$H = @ans@\ \text{m}$"])
T("faraday_emf", "physics electrical", "HE", "Electromagnetic induction", ["induction", "faraday", "emf", "flux"], ["N=[50,100,200,500]", "dp=[0.02,0.04,0.1,0.5]", "dt=[0.1,0.2,0.5,2]"],
  r"A coil of $@N@$ turns experiences a change of flux of $@dp@\ \text{Wb}$ in $@dt@\ \text{s}$. Find the magnitude of the induced emf.", "N*dp/dt", r"\text{V}", ["dp/dt", "N*dp*dt", "N*dt/dp", "N/(dp*dt)"],
  r"Faraday's law gives $|\varepsilon| = N\dfrac{\Delta\Phi}{\Delta t}$.", "Faraday's law of electromagnetic induction", [r"$\varepsilon = N\dfrac{\Delta\Phi}{\Delta t} = @N@\times\dfrac{@dp@}{@dt@}$", r"$\varepsilon = @ans@\ \text{V}$"])
T("rms_v", "physics electrical", "HE", "Alternating current", ["rms", "alternating", "peak", "ac"], ["V0=[100,200,310,400,500]"],
  r"The peak value of an alternating voltage is $@V0@\ \text{V}$. Find its rms value.", "V0/sqrt(2)", r"\text{V}", ["V0*sqrt(2)", "V0/2", "V0*0.637", "V0"],
  r"The rms value of an alternating voltage is $V_{rms} = \dfrac{V_0}{\sqrt{2}}$.", "the rms value of AC", [r"$V_{rms} = \dfrac{V_0}{\sqrt{2}} = \dfrac{@V0@}{1.414}$", r"$V_{rms} = @ans@\ \text{V}$"])
T("bohr_e", "physics chemistry", "HE", "Atomic physics: Bohr model", ["bohr", "hydrogen", "orbit", "energy level", "atomic"], ["n=[2,3,4,5]"],
  r"Find the energy of the electron of a hydrogen atom in the $n = @n@$ orbit.", "-13.6/n**2", r"\text{eV}", ["-13.6/n", "-13.6*n**2", "-13.6*n", "-13.6/(n+1)**2"],
  r"In the Bohr model the energy of the $n$th orbit of hydrogen is $E_n = -\dfrac{13.6}{n^2}\ \text{eV}$.", "the energy levels of hydrogen", [r"$E_n = -\dfrac{13.6}{n^2} = -\dfrac{13.6}{@n@^2}$", r"$E_n = @ans@\ \text{eV}$"], cond="ans<0")
T("decay_n", "physics chemistry", "HE", "Radioactivity", ["radioactive", "decay", "half life", "nuclei"], ["N0=[320,640,800,1600]", "T=[2,5,10]", "k=[2,3,4]"],
  r"A radioactive sample initially has $@N0@$ nuclei and a half-life of $@T@\ \text{days}$. How many nuclei remain undecayed after $@t@\ \text{days}$?", "N0/2**k", "",
  ["N0/(2*k)", "N0/k", "N0/2", "N0/2**(k+1)"], r"After $n$ half-lives, $N = \dfrac{N_0}{2^{n}}$ with $n = \dfrac{t}{T_{1/2}}$.", "the radioactive decay law",
  [r"$n = \dfrac{t}{T_{1/2}} = \dfrac{@t@}{@T@} = @k@$", r"$N = \dfrac{N_0}{2^{n}} = \dfrac{@N0@}{2^{@k@}} = @ans@$"], derived="t=k*T")
# ------------------------------------------------------------------ chemistry
T("ideal_n", "chemistry physics", "HE", "Ideal gas equation", ["ideal gas", "gas", "pv", "nrt", "moles"], ["P=[1,2,3,0.5]", "V=[5,10,20,22.4]", "T=[273,300,350,400]"],
  r"How many moles of an ideal gas occupy $@V@\ \text{L}$ at $@P@\ \text{atm}$ and $@T@\ \text{K}$? ($R = 0.0821\ \text{L atm K}^{-1}\text{mol}^{-1}$)", "P*V/(0.0821*T)", r"\text{mol}",
  ["P*V/T", "0.0821*T/(P*V)", "P*V/(8.314*T)", "P*V*0.0821/T"], r"The ideal gas equation is $PV = nRT$, so $n = \dfrac{PV}{RT}$.", "the ideal gas equation",
  [r"$n = \dfrac{PV}{RT} = \dfrac{@P@\times @V@}{0.0821\times @T@}$", r"$n = @ans@\ \text{mol}$"])
T("avogadro", "chemistry science", "SHE", "Mole concept", ["avogadro", "mole", "molecules", "particles"], ["n=[0.25,0.5,2,3,5]"],
  r"How many molecules are present in $@n@\ \text{mol}$ of a substance? ($N_A = 6.022\times10^{23}\ \text{mol}^{-1}$)", "n*6.022e23", r"\text{molecules}", ["n*6.022e22", "n*6.022e24", "n*6.022e23*2", "n*6.022e21"],
  r"Number of particles $N = n\times N_A$ with $N_A = 6.022\times10^{23}\ \text{mol}^{-1}$.", "Avogadro's number", [r"$N = nN_A = @n@\times6.022\times10^{23}$", r"$N = @ans@$"], sig=4)
T("molality", "chemistry", "HE", "Solutions: concentration terms", ["molality", "solution", "concentration", "solute"], ["w=[20,40,60,80]", "M=[40,58.5,60,98]", "kg=[0.5,1,2]"],
  r"Calculate the molality of a solution containing $@w@\ \text{g}$ of a solute of molar mass $@M@\ \text{g mol}^{-1}$ in $@kg@\ \text{kg}$ of solvent.", "(w/M)/kg", r"\text{mol kg}^{-1}",
  ["w/M*kg", "w/kg", "(w/M)/(kg+1)", "(w/M)/(2*kg)"], r"Molality is $m = \dfrac{\text{moles of solute}}{\text{mass of solvent in kg}}$.", "molality",
  [r"$n = \dfrac{w}{M} = \dfrac{@w@}{@M@}$", r"$m = \dfrac{n}{@kg@} = @ans@\ \text{mol kg}^{-1}$"])
T("kc_equil", "chemistry", "HE", "Chemical equilibrium", ["equilibrium", "kc", "constant", "reversible"], ["A=[0.1,0.2,0.5]", "B=[0.1,0.4,0.5]", "C=[0.2,0.4,0.6]"],
  r"For the reaction $A + B \rightleftharpoons 2C$ the equilibrium concentrations are $[A] = @A@\ \text{M}$, $[B] = @B@\ \text{M}$ and $[C] = @C@\ \text{M}$. Calculate $K_c$.", "C**2/(A*B)", "",
  ["C/(A*B)", "C**2/(A+B)", "(A*B)/C**2", "2*C/(A*B)"], r"For $A + B \rightleftharpoons 2C$, $K_c = \dfrac{[C]^2}{[A][B]}$.", "the equilibrium constant",
  [r"$K_c = \dfrac{[C]^2}{[A][B]} = \dfrac{(@C@)^2}{@A@\times @B@}$", r"$K_c = @ans@$"])
T("gibbs", "chemistry physics", "HE", "Chemical thermodynamics", ["gibbs", "spontaneity", "entropy", "enthalpy", "thermodynamics"], ["H=[-92,-50,-40,40,100]", "S=[-200,150,100,-100,250]", "T=[298,300,500]"],
  r"For a reaction $\Delta H = @H@\ \text{kJ}$ and $\Delta S = @S@\ \text{J K}^{-1}$ at $@T@\ \text{K}$. Calculate $\Delta G$.", "H-T*S/1000", r"\text{kJ}", ["H+T*S/1000", "H-T*S", "(H-T*S)/1000", "H-S/1000"],
  r"The Gibbs energy change is $\Delta G = \Delta H - T\Delta S$ (convert $\Delta S$ to kJ).", "the Gibbs energy equation", [r"$\Delta G = \Delta H - T\Delta S = @H@ - @T@\times\dfrac{@S@}{1000}$", r"$\Delta G = @ans@\ \text{kJ}$"], cond="ans!=0")
T("pct_yield", "chemistry", "HE", "Stoichiometry", ["yield", "stoichiometry", "reaction", "theoretical"], ["act=[8,12,15,18,20,24]", "theo=[25,30,40,50]"],
  r"A reaction has a theoretical yield of $@theo@\ \text{g}$ but only $@act@\ \text{g}$ of product is obtained. Calculate the percentage yield.", "act/theo*100", r"\%", ["theo/act*100", "act/theo", "(theo-act)/theo*100", "act*theo/100"],
  r"Percentage yield $= \dfrac{\text{actual yield}}{\text{theoretical yield}}\times100$.", "percentage yield", [r"$\text{yield} = \dfrac{@act@}{@theo@}\times100$", r"$\text{yield} = @ans@\%$"], cond="ans>0 and ans<100")
# ------------------------------------------------------------------ mathematics
T("circle_area", "maths", "SHE", "Mensuration", ["circle", "area", "mensuration", "radius"], ["r=[3,5,7,10,14,21]"],
  r"Find the area of a circle of radius $@r@\ \text{cm}$.", "pi*r**2", r"\text{cm}^2", ["2*pi*r", "pi*r", "pi*r**2/2", "r**2"], r"The area of a circle is $A = \pi r^2$.", "the area of a circle", [r"$A = \pi r^2 = \pi\times @r@^2$", r"$A = @ans@\ \text{cm}^2$"])
T("sphere_vol", "maths physics", "SHE", "Mensuration", ["sphere", "volume", "mensuration", "radius"], ["r=[3,6,9,12]"],
  r"Find the volume of a sphere of radius $@r@\ \text{cm}$.", "4/3*pi*r**3", r"\text{cm}^3", ["4*pi*r**2", "pi*r**3", "4/3*pi*r**2", "2/3*pi*r**3"], r"The volume of a sphere is $V = \dfrac{4}{3}\pi r^3$.", "the volume of a sphere", [r"$V = \dfrac{4}{3}\pi r^3 = \dfrac{4}{3}\pi\times @r@^3$", r"$V = @ans@\ \text{cm}^3$"])
T("cyl_vol", "maths physics", "SHE", "Mensuration", ["cylinder", "volume", "mensuration"], ["r=[2,3,5,7]", "h=[5,10,14]"],
  r"Find the volume of a cylinder of radius $@r@\ \text{cm}$ and height $@h@\ \text{cm}$.", "pi*r**2*h", r"\text{cm}^3", ["2*pi*r*h", "pi*r*h", "pi*r**2*h/3", "2*pi*r*(r+h)"], r"The volume of a cylinder is $V = \pi r^2 h$.", "the volume of a cylinder", [r"$V = \pi r^2 h = \pi\times @r@^2\times @h@$", r"$V = @ans@\ \text{cm}^3$"])
T("pythag", "maths", "SHE", "Pythagoras theorem", ["pythagoras", "right", "triangle", "hypotenuse"], ["k=1:12:1"],
  r"The two perpendicular sides of a right-angled triangle are $@a@\ \text{cm}$ and $@b@\ \text{cm}$. Find the length of the hypotenuse.", "sqrt(a*a+b*b)", r"\text{cm}", ["a+b", "sqrt(b*b-a*a)", "(a+b)/2", "a*b/2"],
  r"By Pythagoras theorem $c^2 = a^2 + b^2$.", "Pythagoras theorem", [r"$c = \sqrt{a^2+b^2} = \sqrt{@a@^2+@b@^2}$", r"$c = @ans@\ \text{cm}$"], derived="a=3*k;b=4*k")
T("mean5", "maths", "SHE", "Statistics: mean", ["mean", "average", "statistics", "central tendency"], ["n1=2:20:2", "n2=3:21:3", "n3=4:20:4", "n4=5:25:5", "n5=6:24:6"],
  r"Find the arithmetic mean of $@n1@, @n2@, @n3@, @n4@$ and $@n5@$.", "(n1+n2+n3+n4+n5)/5", "", ["(n1+n2+n3+n4+n5)/6", "(n1+n2+n3+n4)/4", "(n1+n2+n3+n4+n5)", "n3"],
  r"The arithmetic mean is $\bar{x} = \dfrac{\sum x}{n}$.", "the arithmetic mean", [r"$\bar{x} = \dfrac{@n1@+@n2@+@n3@+@n4@+@n5@}{5}$", r"$\bar{x} = @ans@$"])
T("roots_sum", "maths", "SHE", "Quadratic equations", ["quadratic", "roots", "sum of roots", "equation"], ["a=[1,2,3,4,5]", "b=[5,6,7,9,11]", "c=[2,3,4,6]"],
  r"Find the sum of the roots of $@a@x^2 + @b@x + @c@ = 0$.", "-b/a", "", ["-c/a", "-b/(2*a)", "-2*b/a", "-b/(a+1)"], r"For $ax^2+bx+c=0$ the sum of the roots is $\alpha+\beta = -\dfrac{b}{a}$.", "the sum of the roots of a quadratic equation",
  [r"$\alpha+\beta = -\dfrac{b}{a} = -\dfrac{@b@}{@a@}$", r"$\alpha+\beta = @ans@$"], cond="ans<0")
T("roots_prod", "maths", "SHE", "Quadratic equations", ["quadratic", "roots", "product of roots", "equation"], ["a=[1,2,3,4,5]", "b=[5,6,7,9,11]", "c=[2,3,4,6]"],
  r"Find the product of the roots of $@a@x^2 + @b@x + @c@ = 0$.", "c/a", "", ["-c/a", "b/a", "c/b", "a/c"], r"For $ax^2+bx+c=0$ the product of the roots is $\alpha\beta = \dfrac{c}{a}$.", "the product of the roots of a quadratic equation",
  [r"$\alpha\beta = \dfrac{c}{a} = \dfrac{@c@}{@a@}$", r"$\alpha\beta = @ans@$"])
T("section_x", "maths", "HE", "Coordinate geometry: straight line", ["section formula", "coordinate", "divides", "ratio"], ["x1=[1,2,3,4]", "x2=[9,10,12,14]", "m=[1,2,3]", "n=[1,2,3]"],
  r"Find the $x$-coordinate of the point that divides the line joining points with $x$-coordinates $@x1@$ and $@x2@$ internally in the ratio $@m@:@n@$.", "(m*x2+n*x1)/(m+n)", "", ["(m*x1+n*x2)/(m+n)", "(x1+x2)/2", "(m*x2+n*x1)", "(m*x2-n*x1)/(m+n)"],
  r"By the section formula $x = \dfrac{mx_2+nx_1}{m+n}$.", "the section formula", [r"$x = \dfrac{mx_2+nx_1}{m+n} = \dfrac{@m@\times @x2@+@n@\times @x1@}{@m@+@n@}$", r"$x = @ans@$"])
T("perm_npr", "maths", "HE", "Permutation and combination", ["permutation", "arrangement", "npr"], ["n=[5,6,7,8,9]", "r=[2,3]"],
  r"In how many ways can $@r@$ different objects be arranged from $@n@$ different objects?", "perm(n,r)", "", ["comb(n,r)", "n**r", "fact(n)", "n*r"],
  r"The number of permutations is ${}^nP_r = \dfrac{n!}{(n-r)!}$.", "the permutation formula", [r"${}^{@n@}P_{@r@} = \dfrac{@n@!}{(@n@-@r@)!}$", r"${}^{@n@}P_{@r@} = @ans@$"])
T("tan_height", "maths physics", "SHE", "Trigonometry: heights and distances", ["height", "distance", "angle of elevation", "trigonometry", "tower"], ["d=[10,20,30,50]", "th=[30,45,60]"],
  r"The angle of elevation of the top of a tower from a point $@d@\ \text{m}$ from its foot is $@th@^{\circ}$. Find the height of the tower.", "d*tan(rad(th))", r"\text{m}", ["d/tan(rad(th))", "d*sin(rad(th))", "d*cos(rad(th))", "d*tan(rad(th))/2"],
  r"In the right triangle $\tan\theta = \dfrac{\text{height}}{\text{distance}}$.", "the tangent ratio", [r"$h = d\tan\theta = @d@\tan @th@^{\circ}$", r"$h = @ans@\ \text{m}$"])
T("pct_change", "maths accounting economics", "SHE", "Percentage", ["percentage", "increase", "change", "growth"], ["v0=[40,50,80,120,200,250]", "v1=[45,64,100,150,260,300]"],
  r"A quantity increases from $@v0@$ to $@v1@$. Find the percentage increase.", "(v1-v0)/v0*100", r"\%", ["(v1-v0)/v1*100", "v1-v0", "v1/v0*100", "v0/v1*100"],
  r"Percentage increase $= \dfrac{\text{new}-\text{old}}{\text{old}}\times100$.", "percentage change", [r"$\dfrac{@v1@-@v0@}{@v0@}\times100$", r"$@ans@\%$"], cond="ans>0")
T("avg_speed", "physics maths science", "SHE", "Motion", ["average speed", "speed", "motion", "journey"], ["v1=[20,30,40,60]", "v2=[30,60,80,90]"],
  r"A vehicle covers a distance at $@v1@\ \text{km h}^{-1}$ and returns the same distance at $@v2@\ \text{km h}^{-1}$. Find the average speed for the whole journey.", "2*v1*v2/(v1+v2)", r"\text{km h}^{-1}",
  ["(v1+v2)/2", "v1*v2/(v1+v2)", "sqrt(v1*v2)", "v1+v2"], r"For equal distances the average speed is $\dfrac{2v_1v_2}{v_1+v_2}$ (total distance over total time).", "average speed", [r"$v_{av} = \dfrac{2v_1v_2}{v_1+v_2} = \dfrac{2\times @v1@\times @v2@}{@v1@+@v2@}$", r"$v_{av} = @ans@\ \text{km h}^{-1}$"], cond="ans>0 and v1!=v2")
# ------------------------------------------------------------------ computer science
T("bits_needed", "cs", "all", "Number systems and data representation", ["bits", "binary", "representation", "number system"], ["n=[10,50,100,200,500,1000]"],
  r"What is the minimum number of bits needed to represent $@n@$ different values?", "ceil(ln(n)/ln(2))", r"\text{bits}", ["floor(ln(n)/ln(2))", "ceil(n/8)", "ceil(ln(n)/ln(10))", "n"],
  r"$k$ bits can represent $2^k$ values, so $k = \lceil\log_2 n\rceil$.", "the number of bits for $n$ values", [r"$k = \lceil\log_2 @n@\rceil$", r"$k = @ans@\ \text{bits}$"])
T("mem_kb", "cs", "all", "Computer memory", ["memory", "ram", "address", "capacity", "storage"], ["k=[10,12,16]", "w=[8,16,32]"],
  r"A memory has $2^{@k@}$ locations and each location stores $@w@$ bits. Find its capacity in kilobytes (1 KB = 1024 bytes).", "2**k*w/8192", r"\text{KB}", ["2**k*w/1024", "2**k*w", "2**k/1024", "2**k*w/8000"],
  r"Capacity $= \text{locations}\times\text{word size}$; bits $\div 8$ gives bytes and bytes $\div 1024$ gives KB.", "memory capacity", [r"$\text{bits} = 2^{@k@}\times @w@$", r"$\text{KB} = \dfrac{2^{@k@}\times @w@}{8\times1024} = @ans@\ \text{KB}$"])
T("cpu_time", "cs", "HE", "Computer architecture", ["cpu", "cpi", "clock", "performance", "instruction"], ["IC=[100,200,500]", "CPI=[1.5,2,3]", "f=[100,200,500,1000]"],
  r"A program has $@IC@$ million instructions with an average $\text{CPI}$ of $@CPI@$ on a processor of clock rate $@f@\ \text{MHz}$. Find the CPU time.", "IC*CPI/f", r"\text{s}", ["IC*f/CPI", "IC/(CPI*f)", "CPI*f/IC", "IC*CPI*f"],
  r"CPU time $= \dfrac{\text{instruction count}\times\text{CPI}}{\text{clock rate}}$.", "the CPU performance equation", [r"$T = \dfrac{IC\times CPI}{f} = \dfrac{@IC@\times10^{6}\times @CPI@}{@f@\times10^{6}}$", r"$T = @ans@\ \text{s}$"])
T("hex2dec", "cs", "all", "Number systems and data representation", ["hexadecimal", "binary", "conversion", "number system"], ["d1=1:9:1", "d0=1:9:1"],
  r"Convert the hexadecimal number $(@d1@@d0@)_{16}$ to decimal.", "16*d1+d0", "", ["10*d1+d0", "8*d1+d0", "16*d0+d1", "d1*d0"],
  r"A two-digit hexadecimal number $(d_1d_0)_{16}$ equals $16d_1 + d_0$.", "hexadecimal to decimal conversion", [r"$(@d1@@d0@)_{16} = @d1@\times16^{1}+@d0@\times16^{0}$", r"$= @ans@$"], cond="ans>0 and d1!=d0")
# ------------------------------------------------------------------ electrical
T("pf_power", "electrical physics", "HE", "AC circuits", ["power factor", "ac", "real power", "alternating"], ["V=[110,220,230,240]", "I=[2,5,10]", "pf=[0.6,0.8,0.9]"],
  r"A single-phase load draws $@I@\ \text{A}$ from a $@V@\ \text{V}$ supply at a power factor of $@pf@$. Find the real power.", "V*I*pf", r"\text{W}", ["V*I", "V*I/pf", "V*I*pf**2", "V*I*sqrt(1-pf**2)"],
  r"Real power is $P = VI\cos\phi$.", "real power in an AC circuit", [r"$P = VI\cos\phi = @V@\times @I@\times @pf@$", r"$P = @ans@\ \text{W}$"])
T("xl", "electrical physics", "HE", "AC circuits", ["inductive reactance", "inductor", "reactance", "ac"], ["f=[50,60,100,400]", "L=[0.1,0.2,0.5,1]"],
  r"Find the inductive reactance of a $@L@\ \text{H}$ inductor at $@f@\ \text{Hz}$.", "2*pi*f*L", r"\Omega", ["pi*f*L", "2*pi*L/f", "f*L", "2*pi*f*L**2"], r"Inductive reactance is $X_L = 2\pi f L$.", "inductive reactance",
  [r"$X_L = 2\pi f L = 2\pi\times @f@\times @L@$", r"$X_L = @ans@\ \Omega$"])
T("motor_slip", "electrical", "HE", "Induction motors", ["slip", "induction motor", "synchronous speed", "motor"], ["f=[50]", "P=[2,4,6,8]", "d=[20,30,40,50,60]"],
  r"A $@P@$-pole induction motor is supplied at $@f@\ \text{Hz}$ and runs at $@N@\ \text{rpm}$. Find the percentage slip.", "d/Ns*100", r"\%", ["d/N*100", "N/Ns*100", "d/Ns", "(Ns+N)/Ns*100"],
  r"Synchronous speed $N_s = \dfrac{120f}{P}$ and slip $s = \dfrac{N_s - N}{N_s}\times100$.", "the slip of an induction motor", [r"$N_s = \dfrac{120\times @f@}{@P@} = @Ns@\ \text{rpm}$", r"$s = \dfrac{N_s-N}{N_s}\times100 = @ans@\%$"], cond="ans>0 and ans<20", derived="Ns=120*f/P;N=Ns-d")
T("back_emf", "electrical", "HE", "DC machines", ["back emf", "dc motor", "armature", "motor"], ["V=[220,230,240]", "Ia=[10,20,25]", "Ra=[0.2,0.5,1]"],
  r"A DC motor on a $@V@\ \text{V}$ supply draws an armature current of $@Ia@\ \text{A}$ and has an armature resistance of $@Ra@\ \Omega$. Find the back emf.", "V-Ia*Ra", r"\text{V}", ["V+Ia*Ra", "V-Ia/Ra", "V-2*Ia*Ra", "V*Ia*Ra/100"],
  r"For a DC motor $E_b = V - I_aR_a$.", "the back emf of a DC motor", [r"$E_b = V - I_aR_a = @V@ - @Ia@\times @Ra@$", r"$E_b = @ans@\ \text{V}$"])
T("cap_series", "physics electrical", "HE", "Capacitors", ["capacitor", "series", "capacitance", "combination"], ["C1=[2,3,4,6,10]", "C2=[2,6,12,15]"],
  r"Two capacitors of $@C1@\ \mu\text{F}$ and $@C2@\ \mu\text{F}$ are connected in series. Find the equivalent capacitance.", "C1*C2/(C1+C2)", r"\mu\text{F}", ["C1+C2", "(C1+C2)/(C1*C2)", "C1*C2", "(C1+C2)/2"],
  r"For capacitors in series $\dfrac{1}{C} = \dfrac{1}{C_1} + \dfrac{1}{C_2}$, so $C = \dfrac{C_1C_2}{C_1+C_2}$.", "capacitors in series", [r"$C = \dfrac{C_1C_2}{C_1+C_2} = \dfrac{@C1@\times @C2@}{@C1@+@C2@}$", r"$C = @ans@\ \mu\text{F}$"])
T("rc_tau", "electrical physics", "HE", "Transient circuits", ["time constant", "rc circuit", "transient", "capacitor"], ["R=[1,2,5,10,20]", "C=[10,20,50,100]"],
  r"An RC circuit has $R = @R@\ \text{k}\Omega$ and $C = @C@\ \mu\text{F}$. Find the time constant.", "R*C", r"\text{ms}", ["R/C", "R+C", "R*C/1000", "R*C/10"], r"The time constant of an RC circuit is $\tau = RC$ (k$\Omega\times\mu$F = ms).", "the time constant of an RC circuit",
  [r"$\tau = RC = @R@\times10^{3}\times @C@\times10^{-6}\ \text{s}$", r"$\tau = @ans@\ \text{ms}$"])
# ------------------------------------------------------------------ civil / survey
T("discharge", "civil physics", "HE", "Fluid flow and hydraulics", ["discharge", "flow", "hydraulics", "pipe", "water"], ["A=[0.5,1,2,3]", "V=[1,1.5,2,3]"],
  r"Water flows through a channel of cross-sectional area $@A@\ \text{m}^2$ with a mean velocity of $@V@\ \text{m s}^{-1}$. Find the discharge.", "A*V", r"\text{m}^3\text{s}^{-1}", ["A/V", "A+V", "V/A", "A*V/2"],
  r"The discharge is $Q = AV$.", "the discharge equation", [r"$Q = AV = @A@\times @V@$", r"$Q = @ans@\ \text{m}^3\text{s}^{-1}$"])
T("youngs_mod", "civil physics", "HE", "Strength of materials", ["young's modulus", "stress", "strain", "elasticity", "modulus"], ["s=[100,200,250,400]", "e=[0.0005,0.001,0.002]"],
  r"A steel bar under a stress of $@s@\ \text{MPa}$ shows a strain of $@e@$. Find Young's modulus.", "s/e/1000", r"\text{GPa}", ["s/e/100", "s/e/10000", "s*e*1000", "s/e"],
  r"Young's modulus is $E = \dfrac{\text{stress}}{\text{strain}}$.", "Young's modulus", [r"$E = \dfrac{\sigma}{\varepsilon} = \dfrac{@s@\ \text{MPa}}{@e@}$", r"$E = @ans@\ \text{GPa}$"])
T("wc_ratio", "civil", "HE", "Concrete technology", ["water cement ratio", "concrete", "cement", "mix"], ["w=[100,120,150,190,225]", "c=[300,400,450,500]"],
  r"A concrete mix uses $@w@\ \text{kg}$ of water and $@c@\ \text{kg}$ of cement. Find the water-cement ratio.", "w/c", "", ["c/w", "w+c", "w/(w+c)", "w*c/1000"],
  r"Water-cement ratio $= \dfrac{\text{mass of water}}{\text{mass of cement}}$.", "the water-cement ratio", [r"$\dfrac{w}{c} = \dfrac{@w@}{@c@}$", r"$w/c = @ans@$"], cond="ans>0 and ans<1")
T("trap_area", "civil maths", "SHE", "Area of land and mensuration", ["trapezium", "area", "land", "survey", "mensuration"], ["a=[10,12,15,20]", "b=[14,18,25,30]", "h=[4,5,6,8]"],
  r"Find the area of a trapezium whose parallel sides are $@a@\ \text{m}$ and $@b@\ \text{m}$ and whose height is $@h@\ \text{m}$.", "h*(a+b)/2", r"\text{m}^2", ["h*(a+b)", "a*b*h/2", "h*(a+b)/4", "(a+b)/2"],
  r"The area of a trapezium is $A = \dfrac{1}{2}(a+b)h$.", "the area of a trapezium", [r"$A = \dfrac{1}{2}(a+b)h = \dfrac{1}{2}(@a@+@b@)\times @h@$", r"$A = @ans@\ \text{m}^2$"])
T("rl_level", "civil", "HE", "Levelling", ["levelling", "reduced level", "backsight", "foresight", "height of instrument", "survey"], ["BM=[100,150,200,250]", "BS=[1.2,1.5,2,2.4]", "FS=[0.4,0.8,1.8,2.6]"],
  r"A level is set up with a back sight of $@BS@\ \text{m}$ on a bench mark of RL $@BM@\ \text{m}$ and a fore sight of $@FS@\ \text{m}$ on point $P$. Find the reduced level of $P$.", "BM+BS-FS", r"\text{m}", ["BM+BS+FS", "BM-BS+FS", "BM-BS-FS"],
  r"By the height of instrument method $\text{RL}_P = \text{RL}_{BM} + BS - FS$.", "the reduced level of a point", [r"$\text{HI} = @BM@ + @BS@$", r"$\text{RL}_P = \text{HI} - @FS@ = @ans@\ \text{m}$"], sig=5)
# ------------------------------------------------------------------ nursing
T("fluid_421", "nursing", "all", "Fluid and electrolyte balance", ["maintenance fluid", "fluid", "paediatric", "4-2-1", "iv fluid"], ["W=[8,12,15,20,25,30,40]"],
  r"Using the 4-2-1 rule, calculate the hourly maintenance fluid requirement of a child weighing $@W@\ \text{kg}$.", "4*min(W,10)+2*min(max(W-10,0),10)+max(W-20,0)", r"\text{mL h}^{-1}", ["W*4", "W*2", "W*3", "4*W+2*W+W"],
  r"The 4-2-1 rule: $4\ \text{mL/kg/h}$ for the first $10\ \text{kg}$, $2$ for the next $10\ \text{kg}$ and $1$ for every kg above $20\ \text{kg}$.", "the 4-2-1 maintenance fluid rule",
  [r"Rate $= 4\times\min(W,10) + 2\times\min(\max(W-10,0),10) + \max(W-20,0)$ with $W = @W@$", r"Rate $= @ans@\ \text{mL h}^{-1}$"])
T("bsa", "nursing", "all", "Body surface area and dosing", ["body surface area", "bsa", "mosteller", "chemotherapy", "dose"], ["h=[150,160,170,180]", "w=[50,60,70,80]"],
  r"Using the Mosteller formula, find the body surface area of a patient with height $@h@\ \text{cm}$ and weight $@w@\ \text{kg}$.", "sqrt(h*w/3600)", r"\text{m}^2", ["sqrt(h*w/360)", "h*w/3600", "sqrt(h*w)/3600", "sqrt(h*w/3000)"],
  r"Mosteller formula: $\text{BSA} = \sqrt{\dfrac{h\,(\text{cm})\times w\,(\text{kg})}{3600}}$.", "the Mosteller formula", [r"$\text{BSA} = \sqrt{\dfrac{@h@\times @w@}{3600}}$", r"$\text{BSA} = @ans@\ \text{m}^2$"])
T("target_hr", "nursing", "all", "Cardiovascular assessment", ["heart rate", "target", "exercise", "pulse", "cardiac"], ["age=[20,30,40,50,60,70]"],
  r"Using the formula $220 - \text{age}$ for maximum heart rate, find the $85\%$ target heart rate of a person aged $@age@$ years.", "0.85*(220-age)", r"\text{beats min}^{-1}", ["220-age", "0.85*220-age", "0.75*(220-age)", "0.85*(200-age)"],
  r"Maximum heart rate $= 220 - \text{age}$; the target is the stated percentage of it.", "the target heart rate", [r"$\text{HR}_{max} = 220 - @age@$", r"$0.85\times\text{HR}_{max} = @ans@\ \text{beats min}^{-1}$"])
T("urine_out", "nursing", "all", "Fluid balance and renal assessment", ["urine output", "renal", "fluid balance", "intake output", "oliguria"], ["V=[600,900,1200,1500]", "W=[50,60,75]", "t=[12,24]"],
  r"A patient weighing $@W@\ \text{kg}$ passes $@V@\ \text{mL}$ of urine in $@t@\ \text{h}$. Calculate the urine output in $\text{mL kg}^{-1}\text{h}^{-1}$.", "V/(W*t)", r"\text{mL kg}^{-1}\text{h}^{-1}", ["V/W", "V/t", "V*t/W", "V/(W+t)"],
  r"Urine output rate $= \dfrac{\text{volume}}{\text{weight}\times\text{time}}$.", "urine output per kg per hour", [r"$\dfrac{V}{Wt} = \dfrac{@V@}{@W@\times @t@}$", r"$= @ans@\ \text{mL kg}^{-1}\text{h}^{-1}$"])
T("kcal_macro", "nursing", "all", "Nutrition and diet therapy", ["energy", "calorie", "carbohydrate", "protein", "fat", "diet"], ["c=[50,100,150,200,250,300]", "p=[20,40,60,80]", "f=[10,30,50,70]"],
  r"A diet provides $@c@\ \text{g}$ carbohydrate, $@p@\ \text{g}$ protein and $@f@\ \text{g}$ fat. Calculate its energy value.", "4*c+4*p+9*f", r"\text{kcal}", ["4*c+4*p+4*f", "9*c+4*p+4*f", "4*c+9*p+4*f", "4*(c+p+f)"],
  r"Energy values: carbohydrate $4$, protein $4$ and fat $9\ \text{kcal g}^{-1}$.", "the Atwater energy factors", [r"$E = 4c + 4p + 9f = 4\times @c@ + 4\times @p@ + 9\times @f@$", r"$E = @ans@\ \text{kcal}$"])
T("dehyd_deficit", "nursing", "all", "Dehydration and rehydration", ["dehydration", "deficit", "fluid deficit", "rehydration"], ["pct=[5,10]", "W=[6,8,10,12,15]"],
  r"A child weighing $@W@\ \text{kg}$ has $@pct@\%$ dehydration. Calculate the fluid deficit.", "10*pct*W", r"\text{mL}", ["pct*W", "pct*W/10", "pct*W*5", "pct*W*2"],
  r"Fluid deficit $= \%\text{ dehydration}\times\text{weight (kg)}\times10\ \text{mL}$.", "the fluid deficit formula", [r"$\text{deficit} = @pct@\times @W@\times10$", r"$\text{deficit} = @ans@\ \text{mL}$"])
# ------------------------------------------------------------------ accounting / economics
T("cogs", "accounting", "SHE", "Final accounts: cost of goods sold", ["cost of goods sold", "cogs", "trading account", "gross profit", "stock"], ["o=[10000,20000,30000]", "p=[50000,60000,80000]", "c=[5000,10000,15000]"],
  r"Opening stock is Rs. $@o@$, purchases Rs. $@p@$ and closing stock Rs. $@c@$. Calculate the cost of goods sold.", "o+p-c", r"\text{rupees}", ["o+p+c", "o-p+c", "p-c-o", "o+p"],
  r"Cost of goods sold $=$ opening stock $+$ purchases $-$ closing stock.", "the cost of goods sold", [r"$\text{COGS} = @o@ + @p@ - @c@$", r"$\text{COGS} = @ans@\ \text{rupees}$"], sig=6)
T("avg_cost", "economics accounting", "SHE", "Production and cost", ["average cost", "cost", "total cost", "production", "output"], ["TC=[5000,8000,12000,15000]", "Q=[100,200,250,500]"],
  r"The total cost of producing $@Q@$ units is Rs. $@TC@$. Find the average cost per unit.", "TC/Q", r"\text{rupees}", ["Q/TC", "TC*Q", "TC/(Q+10)", "TC/(2*Q)"],
  r"Average cost $= \dfrac{\text{total cost}}{\text{output}}$.", "average cost", [r"$AC = \dfrac{TC}{Q} = \dfrac{@TC@}{@Q@}$", r"$AC = @ans@$ rupees per unit"])

have = {t["id"] for t in L["templates"]}
L["templates"] += [t for t in NEW if t["id"] not in have]
if not any("civil" in d[1] for d in L["domains"]):
    L["domains"].append(["civil|survey|water-supply|concrete|building|geology|materials|hydraulics", ["civil"]])
json.dump(L, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=None, separators=(",", ":"))
print(len(L["templates"]), "templates")
