# Verbatim samples from the shipped specialist packs (planner seed 15)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5528)

**Q1. [Applied Biology; 1 mark; gold]** Which enzyme is needed for the digestion of milk protein in human beings?

- (a) rennin
- (b) sucrase
- (c) lactase
- (d) pepsin

Key: (a) rennin. Why: rennin curdles casein in infants; lactase(b) digests the milk sugar, which is the trap. Pepsin also acts on protein but the classic milk-protein answer is rennin.

**Q2. [Animal Tissues; 1 mark; gold]** Which cells of connective tissue produce histamine and heparin?

- (a) fibroblasts
- (b) mast cells
- (c) plasma cells
- (d) macrophages

Key: (b) mast cells. Why: mast cell granules hold histamine and heparin. Plasma cells make antibodies.

**Q3. [Developmental Biology; 1 mark; gold]** Metamorphosis of a frog tadpole into an adult is controlled by

- (a) oestrogen
- (b) insulin
- (c) thyroxine
- (d) adrenaline

Key: (c) thyroxine. Why: thyroxine from the thyroid; if the gland is removed, tadpoles remain tadpoles.

**Q4. [Human Biology; 1 mark; computed]** A person has a heart rate of $72\ \text{beats min}^{-1}$ and a stroke volume of $60\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $8.64\ \text{L min}^{-1}$
- (b) $1.2\ \text{L min}^{-1}$
- (c) $4.32\ \text{L min}^{-1}$
- (d) $43.2\ \text{L min}^{-1}$

Key: (c) $4.32\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 72\times 60\ \text{mL min}^{-1}$ $CO = 4.32\ \text{L min}^{-1}$

**Q5. [Plant Physiology; 3 marks; teacher]** Why does PEP carboxylase play a crucial role in plant photosynthesis?

Marking scheme:

- PEP carboxylase facilitates CO2 transport to the bundle sheath cells.  **[1]**
- This ensures RuBisCO operates in a CO2-rich environment.  **[1]**
- Thus, enhancing the efficiency of the Calvin cycle by minimizing photorespiration.  **[1]**

**Q6. [Genetics; 5 marks; teacher]** In a dihybrid cross between heterozygous parents (RrYy x RrYy), calculate the expected phenotypic ratio and numbers for 1600 offspring. Additionally, explain Chargaff's rule regarding the base composition in DNA.

Marking scheme:

- For 1600 offspring: round yellow (900), round green (300), wrinkled yellow (300), wrinkled green (100).  **[2]**
- Each gene follows Rr × Rr and Yy × Yy, each giving 1/2 chance of heterozygote.  **[1]**
- In DNA, Chargaff's rule states $A = T$ and $G = C$, thus purines equal pyrimidines, $\frac{A+G}{T+C} = 1$.  **[1]**
- Expected (E) and observed (O) totals match.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.4801)

**Q1. [Nuclear physics; 1 mark; gold]** The radius of a nucleus of mass number $A$ is proportional to

- (a) $A^{1/3}$
- (b) $A^{2}$
- (c) $A$
- (d) $A^{2/3}$

Key: (a) $A^{1/3}$. Why: volume is proportional to $A$, so radius goes as the cube root.

**Q2. [Reflection at curved mirror; 1 mark; gold]** The linear magnification produced by a mirror is

- (a) $m = -u/v$
- (b) $m = -v/u$
- (c) $m = v/u$
- (d) $m = u/v$

Key: (b) $m = -v/u$. Why: the minus sign is what tells you a real image is inverted. Option (a) is the lens magnification.

**Q3. [Electric field; 1 mark; teacher]** Consider a cylindrical region with a wire running along its central axis. If the radius of this cylinder is denoted by $r$ and its length by $l$, which statement correctly describes their orientation?

- (a) The wire is tangent to the surface of the cylinder.
- (b) The wire is perpendicular to the axis of the cylinder.
- (c) The wire is along the axis of the cylinder.
- (d) The wire crosses the cylinder at an angle of 45 degrees.

Key: (c) The wire is along the axis of the cylinder.. Why: The wire's position along the cylinder's axis is explicitly stated in the description.

**Q4. [DC Circuits; 1 mark; computed]** A cell of emf $24\ \text{V}$ and internal resistance $1\ \Omega$ is connected to an external resistance of $10\ \Omega$. Find the current in the circuit.

- (a) $24\ \text{A}$
- (b) $2.4\ \text{A}$
- (c) $2.18\ \text{A}$
- (d) $2.67\ \text{A}$

Key: (c) $2.18\ \text{A}$. Why: For a cell with internal resistance $I = \dfrac{E}{R + r}$. $I = \dfrac{E}{R+r} = \dfrac{24}{10+1}$ $I = 2.18\ \text{A}$

**Q5. [Physical Quantities; 3 marks; teacher]** Define absolute error, mean absolute error, relative error, and percentage error. Given the mass of a body as $20.00 \pm 0.05\ \text{g}$ and its volume as $5.00 \pm 0.02\ \text{cm}^3$, calculate the relative error in mass.

Marking scheme:

- Absolute error: difference between true value and measured value.  **[1]**
- Mean absolute error: average of absolute errors.  **[1]**
- Relative error: absolute error divided by true value.  **[1]**

**Q6. [Nuclear physics; 5 marks; teacher]** Explain the concept of pair production in nuclear physics and justify why it requires a minimum energy of $1.02\ \text{MeV}$ and must occur in the vicinity of a nucleus.

Marking scheme:

- Pair production involves the creation of an electron-positron pair from a photon.  **[2]**
- It needs at least $1.02\ \text{MeV}$ because this is the total rest mass energy of both particles ($2 \times 0.511\ \text{MeV}$).  **[1]**
- This process must happen near a nucleus due to the need to conserve both energy and momentum; the nucleus provides a rest frame to balance the momentum.  **[1]**
- Additionally, the high electric field near a nucleus facilitates the conversion of photon energy into particle mass.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5011)

**Q1. [Biota and Environment; 1 mark; gold]** The technique used to amplify a small sample of DNA many million times is

- (a) PCR
- (b) chromatography
- (c) ELISA
- (d) electrophoresis

Key: (a) PCR. Why: the polymerase chain reaction, invented by Kary Mullis.

**Q2. [Ecology; 1 mark; gold]** The term ecosystem was coined in 1935 by

- (a) R. L. Lindeman
- (b) A. G. Tansley
- (c) E. P. Odum
- (d) Charles Elton

Key: (b) A. G. Tansley. Why: Tansley, 1935; Lindeman later quantified the energy flow.

**Q3. [Evolutionary Biology; 1 mark; gold]** The ship on which Darwin made his five-year voyage was the

- (a) Endeavour
- (b) Challenger
- (c) Beagle
- (d) Discovery

Key: (c) Beagle. Why: HMS Beagle, 1831–36.

**Q4. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 24$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $6$
- (b) $24$
- (c) $12$
- (d) $48$

Key: (c) $12$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{24}{2}$ $n = 12$

**Q5. [Biomolecules and Cell Biology; 3 marks; teacher]** Describe the roles of the Golgi body in plant cells during cytokinesis.

Marking scheme:

- Forms lysosomes. 2.  **[1]**
- Secretes polysaccharides for cell wall synthesis. 3.  **[1]**
- Supplies vesicles for cell plate formation during cytokinesis.  **[1]**

**Q6. [Floral Diversity; 5 marks; teacher]** Explain the significance of heterospory in plant evolution and describe the characteristics of angiosperms, including their diversity.

Marking scheme:

- Heterospory is significant as it marks an evolutionary step towards seed formation in plants like Selaginella, Marsilea, and Salvinia.  **[2]**
- Angiosperms are characterized by flowers and seeds enclosed within fruits.  **[1]**
- They represent the largest and most successful plant group with about $2{,}50{,}000$ species.  **[1]**
- These features enhance reproductive success and adaptability, contributing to their widespread distribution and diversity.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.6191)

**Q1. [Magnetic field; 1 mark; computed]** A straight wire of length $40\ \text{cm}$ carrying a current of $1\ \text{A}$ is placed perpendicular to a magnetic field of $80\ \text{mT}$. Find the force on the wire.

- (a) $0.032\ \text{N}$
- (b) $0.0032\ \text{N}$
- (c) $3.2\ \text{N}$
- (d) $0.32\ \text{N}$

Key: (a) $0.032\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 80\times10^{-3}\times1\times40\times10^{-2}$ $F = 0.032\ \text{N}$

**Q2. [Polarization; 1 mark; gold]** Unpolarized light of intensity $I_0$ passes through an ideal polaroid. The transmitted intensity is

- (a) zero
- (b) $I_0/2$
- (c) $I_0$
- (d) $I_0/4$

Key: (b) $I_0/2$. Why: the polaroid passes one of the two equal components of the random polarization.

**Q3. [Electrical circuits; 1 mark; teacher]** What is the specific heat capacity of water used in the calculation?

- (a) $8400\ \text{J kg}^{-1}\text{K}^{-1}$
- (b) $2100\ \text{J kg}^{-1}\text{K}^{-1}$
- (c) $4200\ \text{J kg}^{-1}\text{K}^{-1}$
- (d) $1050\ \text{J kg}^{-1}\text{K}^{-1}$

Key: (c) $4200\ \text{J kg}^{-1}\text{K}^{-1}$. Why: If 80 % of the electrical energy reaches the water, how long does it take? Take the specific heat capacity of water as $4200\ \text{J kg}^{-1}\text{K}^{-1}$.

**Q4. [Thermoelectric effects; 1 mark; teacher]** Given the relationship between the thermoelectric potential $E = \alpha\theta + \frac{1}{2}\beta\theta^{2}$, what expression correctly represents the thermoelectric power (Seebeck coefficient)?

- (a) $S = \alpha\theta + \beta\theta^2$
- (b) $S = \alpha\theta + \beta$
- (c) $S = \alpha + \beta\theta$
- (d) $S = \frac{\alpha}{\theta} + \frac{1}{2}\beta\theta$

Key: (c) $S = \alpha + \beta\theta$. Why: The derivative of $E$ with respect to $\theta$ yields the thermoelectric power as $S = \alpha + \beta\theta$.

**Q5. [Rotational dynamics; 3 marks; teacher]** Derive the moment of inertia of a uniform thin rod of mass M and length L about an axis through its center perpendicular to its length. Show the integral setup and the final expression.

Marking scheme:

- Consider a small element $dx$ at distance $x$ from center C.  **[1]**
- Mass element $dm = \frac{M}{L} dx$.  **[1]**
- Moment of inertia $dI = x^2 dm = \frac{M}{L} x^2 dx$.  **[1]**

**Q6. [Fluid statics; 5 marks; teacher]** Calculate the work done in blowing a soap bubble of radius $3\ \text{cm}$ and determine the excess pressure inside it, given that the surface tension $T = 0.03\ \text{N m}^{-1}$. Additionally, explain how surface tension changes with temperature and the effect of detergents on it.

Marking scheme:

- The work done to blow a soap bubble of radius $3\ \text{cm}$ is $W = 8\pi R^2 T = 8\pi (0.03)^2 (0.03) = 2.26\times10^{-4}\ \text{J}$.  **[2]**
- The excess pressure inside the bubble is $4T/R = 4(0.03)/(0.03) = 4\ \text{Pa}$.  **[2]**
- Surface tension decreases with increasing temperature and is reduced by detergents.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.8785)

**Q1. [Modern Chemical Manufactures; 1 mark; gold]** An efflorescent substance is

- (a) $\text{Na}_2\text{CO}_3\cdot10\text{H}_2\text{O}$
- (b) conc. $\text{H}_2\text{SO}_4$
- (c) anhydrous $\text{CaCl}_2$
- (d) NaCl

Key: (a) $\text{Na}_2\text{CO}_3\cdot10\text{H}_2\text{O}$. Why: washing soda loses water on standing.

**Q2. [Chemistry of Non-metals; 1 mark; gold]** The gas prepared in a Kipp's apparatus from $\text{FeS}$ is

- (a) $\text{SO}_2$
- (b) $\text{H}_2\text{S}$
- (c) $\text{H}_2$
- (d) $\text{CO}_2$

Key: (b) $\text{H}_2\text{S}$. Why: $\text{FeS}$ with dilute acid gives hydrogen sulphide; (b) comes from marble.

**Q3. [Fundamental Principles of Organic Chemistry; 1 mark; teacher]** According to Dalton's law of partial pressures, if the total pressure in a vessel is $P$, what expression represents the partial pressure ($p_i$) of a component gas with mole fraction $x_i$?

- (a) $p_i = P - x_i$
- (b) $p_i = \frac{x_i}{P}$
- (c) $p_i = x_iP$
- (d) $p_i = x_i + P$

Key: (c) $p_i = x_iP$. Why: The correct expression according to Dalton's law is $p_i = x_iP$.

**Q4. [Foundation and Fundamentals; 1 mark; computed]** How many molecules are present in $3\ \text{mol}$ of a substance? ($N_A = 6.022\times10^{23}\ \text{mol}^{-1}$)

- (a) $3.613\times10^{24}\ \text{molecules}$
- (b) $1.807\times10^{23}\ \text{molecules}$
- (c) $1.807\times10^{24}\ \text{molecules}$
- (d) $1.807\times10^{22}\ \text{molecules}$

Key: (c) $1.807\times10^{24}\ \text{molecules}$. Why: Number of particles $N = n\times N_A$ with $N_A = 6.022\times10^{23}\ \text{mol}^{-1}$. $N = nN_A = 3\times6.022\times10^{23}$ $N = 1.807\times10^{24}$

**Q5. [Foundation and Fundamentals; 3 marks; teacher]** Calculate the mass of NaOH required to neutralize 0.5 mol of H_2SO_4, given the molar mass of NaOH is 40 g/mol.

Marking scheme:

- Reaction: H_2SO_4 + 2NaOH -> Na_2SO_4 + 2H_2O. 2.  **[1]**
- Moles of NaOH = 0.5 mol * 2 = 1 mol. 3.  **[1]**
- Mass of NaOH = 1 mol * 40 g/mol = 40 g.  **[1]**

**Q6. [Chemical Bonding and Shapes of Molecules; 5 marks; teacher]** Using VSEPR theory, predict and explain the shape of $\text{H}_2\text{O}$ molecule. Account for its bond angle based on the presence of lone pairs. Include the number of lone pairs present on each atom.

Marking scheme:

- The $\text{H}_2\text{O}$ molecule has a bent shape due to the presence of two lone pairs on the oxygen atom.  **[2]**
- Oxygen has six valence electrons; forming two bonds with hydrogen leaves four electrons as two lone pairs.  **[1]**
- These lone pairs repel the bonding pairs, reducing the bond angle from ideal tetrahedral (109.5°) to approximately 104.5°.  **[1]**
- The molecule has 2 lone pairs on the oxygen atom and no lone pairs on the hydrogen atoms.  **[1]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.3057)

**Q1. [Aldehydes and Ketones; 1 mark; gold]** Tollens' reagent is obtained when AgNO₃ solution is treated with

- (a) excess ammonia solution
- (b) KI solution
- (c) dilute HCl
- (d) NaCl solution

Key: (a) excess ammonia solution. Why: ammonia dissolves the brown Ag₂O first formed, giving the diamminesilver(I) ion that is reduced by aldehydes to a silver mirror.

**Q2. [Studies of Heavy Metals; 1 mark; gold]** The Bessemer converter is used in the extraction of copper for

- (a) electrolytic refining of copper
- (b) converting copper matte into blister copper
- (c) concentrating copper pyrite
- (d) roasting zinc blende

Key: (b) converting copper matte into blister copper. Why: hot air blown through molten matte oxidises FeS to slag and then Cu₂S to blister copper: 2Cu₂S + 3O₂ → 2Cu₂O + 2SO₂, then 2Cu₂O + Cu₂S → 6Cu + SO₂.

**Q3. [Haloalkanes; 1 mark; gold]** Trichloromethane is stored in dark bottles filled to the brim because in air and light it forms

- (a) methanol
- (b) HCl
- (c) phosgene
- (d) chloropicrin

Key: (c) phosgene. Why: slow photo-oxidation gives carbonyl chloride; the ethanol added destroys any phosgene formed and the full bottle excludes air.

**Q4. [Electrochemistry; 1 mark; computed]** Calculate the mass of copper deposited when a current of $3\ \text{A}$ is passed through $\text{CuSO}_4$ solution for $20$ minutes. (Cu $= 63.5$, $F = 96500\ \text{C mol}^{-1}$.)

- (a) $2.37\ \text{g}$
- (b) $0.79\ \text{g}$
- (c) $1.18\ \text{g}$
- (d) $4.74\ \text{g}$

Key: (c) $1.18\ \text{g}$. Why: Faraday's first law gives $m = \dfrac{M I t}{nF}$. $m = \dfrac{MIt}{nF} = \dfrac{63.5\times3\times20\times60}{2\times96500}$ $m = 1.18\ \text{g}$

**Q5. [Chemical Kinetics; 3 marks; teacher]** Explain how to determine the order of a reaction with respect to reactant A using initial rates.

Marking scheme:

- Conduct multiple experiments, altering [A] while keeping other concentrations constant. 2.  **[1]**
- Measure initial rates for each experiment. 3.  **[1]**
- If doubling [A] doubles the rate, the order with respect to A is 1, as $2^1 = 2$.  **[1]**

**Q6. [Electrochemistry; 5 marks; gold]** a) Draw the standard hydrogen electrode and label it. [2] b) Why is it called a reference electrode? [1] c) E°(Zn²⁺/Zn) = −0.76 V and E°(Pb²⁺/Pb) = −0.13 V. Write the cell notation and calculate the emf. [2] (NEB model set B)

Marking scheme:

- (a) See the figure: platinum foil coated with platinum black, dipping in 1 M HCl; pure H₂ gas at 1 atm bubbled over it; a side tube to a salt bridge.(b) Its potential is fixed at zero by convention, so every other electrode potential is measured relative to it.(c) Zn (more negative) is the anode and Pb the cathode.  **[5]**

## Mathematics - Class 11 (NEB)  (`math11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.9558)

**Q1. [Computational Methods; 1 mark; gold]** The Newton–Raphson iteration formula is

- (a) $x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}$
- (b) $x_{n+1}=\frac{f(x_n)}{f'(x_n)}$
- (c) $x_{n+1}=x_n+\frac{f(x_n)}{f'(x_n)}$
- (d) $x_{n+1}=x_n-\frac{f'(x_n)}{f(x_n)}$

Key: (a) $x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}$. Why: subtract the ratio; (a) has the wrong sign and (c) inverts the ratio.

**Q2. [Trigonometric Equations and General Values; 1 mark; gold]** The general solution of $\sin x=\frac12$ is

- (a) $n\pi+\frac{\pi}{6}$
- (b) $n\pi+(-1)^n\frac{\pi}{6}$
- (c) $2n\pi\pm\frac{\pi}{6}$
- (d) $n\pi\pm\frac{\pi}{6}$

Key: (b) $n\pi+(-1)^n\frac{\pi}{6}$. Why: for $\sin x=\sin\alpha$ the general value is $n\pi+(-1)^n\alpha$ with $\alpha=\pi/6$.

**Q3. [Vectors; 1 mark; teacher]** In vector algebra, if we want to express vector $\vec{c}$ as a linear combination of vectors $\vec{a}$ and $\vec{b}$, which of the following represents this expression?

- (a) $\vec{c} = \frac{x}{\vec{a}} + \frac{y}{\vec{b}}$
- (b) $\vec{c} = x\vec{a} - y\vec{b}$
- (c) $\vec{c} = x\vec{a} + y\vec{b}$
- (d) $\vec{c} = x\vec{a} \cdot y\vec{b}$

Key: (c) $\vec{c} = x\vec{a} + y\vec{b}$. Why: The expression $\vec{c} = x\vec{a} + y\vec{b}$ directly matches the statement provided.

**Q4. [Anti-derivatives; 1 mark; computed]** Evaluate $\displaystyle\int_{0}^{2}\left(3x^{2} + 8x\right)dx$.

- (a) $40$
- (b) $28$
- (c) $24$
- (d) $56$

Key: (c) $24$. Why: By the power rule of integration $\displaystyle\int x^{n}dx = \dfrac{x^{n+1}}{n+1}$. $\displaystyle\int_0^{2}(3x^{2}+8x)dx = \left[\dfrac{3x^{3}}{3} + \dfrac{8x^{2}}{2}\right]_0^{2}$ $= 24$

**Q5. [Curve Sketching; 3 marks; teacher]** Given $f(x)=x^3$ and $g(x)=e^{-x}$, determine if each function is increasing or decreasing on $\mathbb{R}$, and explain why $f(x)=x^2$ is not monotonic.

Marking scheme:

- $f(x)=x^3$ is increasing on $\mathbb{R}$ as its derivative $f'(x)=3x^2 \geq 0$. 2.  **[1]**
- $g(x)=e^{-x}$ is decreasing because $g'(x)=-e^{-x} < 0$. 3.  **[1]**
- $f(x)=x^2$ is not monotonic since it decreases on $(-\infty,0]$ and increases on $[0,\infty)$.  **[1]**

**Q6. [Anti-derivatives; 5 marks; teacher]** Evaluate the integral $\int\frac{2x+1}{(x-1)(x^{2}+1)}\,dx$ using partial fractions, clearly stating the form of the decomposition and justifying it.

Marking scheme:

- To evaluate $\int\frac{2x+1}{(x-1)(x^{2}+1)}\,dx$, decompose into partial fractions as $\frac{A}{x-1} + \frac{Bx+C}{x^2+1}$.  **[1]**
- This form is chosen because $(x-1)$ and $(x^2+1)$ are distinct irreducible factors of the denominator.  **[1]**
- Multiplying both sides by $(x-1)(x^2+1)$ gives $2x+1 = A(x^2+1) + (Bx+C)(x-1)$.  **[1]**
- Solving for coefficients $A$, $B$, and $C$ yields $A=1$, $B=-1$, and $C=2$.  **[1]**
- Thus, the integral becomes $\int\left(\frac{1}{x-1} + \frac{-x+2}{x^2+1}\right)dx$.  **[1]**

## Mathematics - Class 12 (NEB)  (`math12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.1646)

**Q1. [Anti-derivatives; 1 mark; gold]** $1^{2}+2^{2}+\cdots+n^{2}$ equals

- (a) $\frac{n(n+1)(2n+1)}{6}$
- (b) $\frac{n(n+1)(n+2)}{6}$
- (c) $\frac{n(n+1)}{2}$
- (d) $\left[\frac{n(n+1)}{2}\right]^{2}$

Key: (a) $\frac{n(n+1)(2n+1)}{6}$. Why: the standard result; (c) is the sum of cubes.

**Q2. [Conic Sections; 1 mark; gold]** The eccentricity of the ellipse $\frac{x^{2}}{25}+\frac{y^{2}}{16}=1$ is

- (a) $\frac{5}{3}$
- (b) $\frac{3}{5}$
- (c) $\frac{4}{5}$
- (d) $\frac{5}{4}$

Key: (b) $\frac{3}{5}$. Why: $e=\sqrt{1-\frac{16}{25}}=\sqrt{\frac{9}{25}}=\frac{3}{5}$.

**Q3. [Product of Vectors; 1 mark; computed]** Find the scalar product of $\vec{a} = 2\hat{i} + 1\hat{j} + 6\hat{k}$ and $\vec{b} = 3\hat{i} + 1\hat{j} + 4\hat{k}$.

- (a) $17$
- (b) $144$
- (c) $31$
- (d) $24$

Key: (c) $31$. Why: The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$. $\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = 2\times3+1\times1+6\times4$ $\vec{a}\cdot\vec{b} = 31$

**Q4. [Derivatives; 1 mark; teacher]** As $x$ becomes very large, which function does $\sinh x$ approach?

- (a) $e^x$
- (b) $\cosh x$
- (c) $\frac{1}{2} e^x$
- (d) $\frac{1}{2} e^{-x}$

Key: (c) $\frac{1}{2} e^x$. Why: Both $\sinh x$ and $\cosh x$ approach $\frac{1}{2} e^x$ for large values of $x$.

**Q5. [Complex Numbers; 3 marks; teacher]** Given $z = 1.18(\cos 32^{\circ} + i\sin 32^{\circ})$, calculate $z^4$ and express it in polar form.

Marking scheme:

- Calculate radius: $1.18^4 = 1.94$. 2.  **[1]**
- Calculate angle: $4 \times 32^{\circ} = 128^{\circ}$. 3.  **[1]**
- Express $z^4$ as $1.94(\cos 128^{\circ} + i\sin 128^{\circ})$.  **[1]**

**Q6. [Conic Sections; 5 marks; gold]** a) Find the foci and the centre of the hyperbola $9x^{2}-16y^{2}-144=0$. [2] b) A parabolic reflector is $20$ cm in diameter and $5$ cm deep. Find the position of its focus. [3] (NEB 2080 Q21a; NEB 2081 Q4)

Marking scheme:

- (a) Divide by $144$: $\dfrac{x^{2}}{16}-\dfrac{y^{2}}{9}=1$.  **[2]**
- So $a=4$, $b=3$, $c=\sqrt{16+9}=5$, and the centre is the origin.  **[1]**
- Foci: $(\pm5,\,0)$.(b) Place the vertex at the origin and the axis along the $y$-axis: $x^{2}=4ay$.  **[1]**
- The rim of the reflector is $10$ cm from the axis and $5$ cm from the vertex, so $(10,5)$ lies on the parabola:  **[1]**

## Computer Science - Class 11 (NEB)  (`cs11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.9843)

**Q1. [Multimedia; 1 mark; gold]** Which device reads the pencil-filled bubbles on an objective answer sheet?

- (a) OMR
- (b) BCR
- (c) OCR
- (d) MICR

Key: (a) OMR. Why: Optical Mark Recognition senses marks; OCR reads printed characters.

**Q2. [Computer Software and Operating System; 1 mark; gold]** An operating system that keeps several programs in main memory and switches the CPU among them is called

- (a) real-time only
- (b) multiprogramming
- (c) single-user
- (d) batch only

Key: (b) multiprogramming. Why: multiprogramming keeps many jobs in memory so the CPU is never idle.

**Q3. [Programming Concepts and Logics; 1 mark; computed]** Convert the binary number $11100_{2}$ to decimal.

- (a) $56$
- (b) $7$
- (c) $28$
- (d) $29$

Key: (c) $28$. Why: A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two). $1\times16+1\times8+1\times4+0\times2+0\times1$ $= 28$

**Q4. [Web Technology I; 1 mark; teacher]** What is used to uniquely identify a computer on the internet?

- (a) Domain name
- (b) URL
- (c) IP address
- (d) MAC address

Key: (c) IP address. Why: An IP address, such as 142.250.183.4, is used to uniquely identify a computer on the internet.

**Q5. [Computer System; 3 marks; teacher]** Explain the formula for access time in a computer system and briefly describe what computer memory does.

Marking scheme:

- Access time is calculated as $Access\ time = seek\ time + rotational\ latency + transfer\ time$.  **[2]**
- Computer memory stores data and instructions temporarily or permanently, facilitating quick access during processing.  **[1]**

**Q6. [Programming Concepts and Logics; 5 marks; teacher]** Explain the difference between pre-increment (++x) and post-increment (x++) operators with an example. Also, provide the correct evaluation of the expression 2 + 3 * 4 - 6 / 2, and describe how the number 59 is represented in BCD.

Marking scheme:

- Pre-increment (++x) increments the value before it is used, e.g., if x=10, then y=++x sets y to 11.  **[2]**
- Post-increment (x++) uses the current value first, then increments, e.g., if x=10, then y=x++ sets y to 10.  **[1]**
- The expression 2 + 3 * 4 - 6 / 2 evaluates to 11, following operator precedence rules.  **[1]**
- In BCD, 59 is represented as $0101\ 1001$, where each 4-bit segment corresponds to a decimal digit.  **[1]**

## Computer Science - Class 12 (NEB)  (`cs12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 4.4192)

**Q1. [Recent Trends in Technology; 1 mark; gold]** Why is cloud computing popular nowadays?

- (a) cost-sharing and easily accessible
- (b) affordable to all (NEB model question)
- (c) modern technology and costly
- (d) accessible and freely available

Key: (a) cost-sharing and easily accessible. Why: many users share one pool of resources, so the cost per user falls and the service is reachable from anywhere.

**Q2. [Web Technology II; 1 mark; gold]** A collection of hyperlinked documents on the Internet is called

- (a) email system (NEB 2080)
- (b) www
- (c) HTML
- (d) webpage

Key: (b) www. Why: the World Wide Web is the hyperlinked document collection; HTML is only its language.

**Q3. [Object-Oriented Programming; 1 mark; gold]** A special member function that runs automatically when an object is created is a

- (a) friend function
- (b) destructor
- (c) constructor
- (d) virtual function

Key: (c) constructor. Why: the constructor initialises the object's data members.

**Q4. [Data Communication and Networking; 1 mark; computed]** What is the minimum number of bits needed to represent $100$ different values?

- (a) $13\ \text{bits}$
- (b) $2\ \text{bits}$
- (c) $7\ \text{bits}$
- (d) $6\ \text{bits}$

Key: (c) $7\ \text{bits}$. Why: $k$ bits can represent $2^k$ values, so $k = \lceil\log_2 n\rceil$. $k = \lceil\log_2 100\rceil$ $k = 7\ \text{bits}$

**Q5. [Database Management System; 3 marks; teacher]** List and briefly explain three disadvantages of using a centralized database management system.

Marking scheme:

- Higher costs for both software and hardware. 2.  **[1]**
- Increased complexity requiring skilled staff. 3.  **[1]**
- Single point of failure; if the server fails, all applications stop.  **[1]**

**Q6. [Data Communication and Networking; 5 marks; teacher]** Explain the concept of subnetting within a class C IP address block using a block size of 64. Additionally, define IP address, subnet mask, gateway, and MAC address.

Marking scheme:

- Subnetting a class C block with a size of 64 yields subnets starting at 0, 64, 128, and 192 ($4 \times 64 = 256$).  **[1]**
- An IP address uniquely identifies devices on a network.  **[1]**
- A subnet mask divides an IP address into network and host parts.  **[1]**
- A gateway routes traffic between networks.  **[1]**
- A MAC address is a unique identifier for a network interface.  **[1]**
