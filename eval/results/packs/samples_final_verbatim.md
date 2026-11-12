# Verbatim samples from the shipped specialist packs (planner seed 18)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5528)

**Q1. [Animal Tissues; 1 mark; gold]** Which enzymes are likely to act in order on soyabean sprouts eaten by a man as they move down the alimentary canal?

- (a) trypsin, peptidases, pepsin
- (b) peptidases, pepsin, trypsin
- (c) pepsin, peptidases, trypsin
- (d) pepsin, trypsin, peptidases

Key: (d) pepsin, trypsin, peptidases. Why: pepsin (stomach) → trypsin (duodenum) → peptidases (intestinal brush border). Reversing the stomach and the intestine gives(b) –(d).

**Q2. [Human Biology; 1 mark; computed]** A person has a heart rate of $60\ \text{beats min}^{-1}$ and a stroke volume of $65\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $3.9\ \text{L min}^{-1}$
- (b) $7.8\ \text{L min}^{-1}$
- (c) $0.923\ \text{L min}^{-1}$
- (d) $39\ \text{L min}^{-1}$

Key: (a) $3.9\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 60\times 65\ \text{mL min}^{-1}$ $CO = 3.9\ \text{L min}^{-1}$

**Q3. [Applied Biology; 1 mark; teacher]** Which of the following statements correctly identifies the largest bee species?

- (a) Apis mellifera
- (b) Megachile pluto
- (c) Bombus terrestris
- (d) Apis laboriosa

Key: (b) Megachile pluto. Why: Megachile pluto is the largest bee species.

**Q4. [Developmental Biology; 1 mark; teacher]** What hormone, when fed to a young tadpole, causes it to metamorphose prematurely into a small frog?

- (a) testosterone
- (b) insulin
- (c) thyroxine
- (d) estrogen

Key: (c) thyroxine. Why: Feeding thyroxine to a young tadpole results in premature transformation into a frog.

**Q5. [Plant Physiology; 2 marks; teacher]** Calculate the Respiratory Quotient (RQ) of tripalmitin ($\text{C}_{51}\text{H}_{98}\text{O}_6$) using its chemical formula and show that it is approximately 0.7.

Marking scheme:

- The balanced equation for tripalmitin respiration is $\text{C}_{51}\text{H}_{98}\text{O}_6 + 74\text{O}_2 \rightarrow 51\text{CO}_2 + 49\text{H}_2\text{O}$.  **[1]**
- Thus, RQ = $\frac{51}{74} \approx 0.7$.  **[1]**

**Q6. [Genetics; 5 marks; teacher]** Explain Mendel's law of independent assortment using a dihybrid cross (RrYy x RrYy) in pea plants. Predict the phenotypic ratio of the offspring and list all possible gametes formed by a double heterozygote RrYy.

Marking scheme:

- Mendel's law of independent assortment states that genes for different traits separate independently during gamete formation.  **[2]**
- In a dihybrid cross (RrYy x RrYy), a double heterozygote RrYy forms 4 types of gametes: RY, Ry, rY, and ry in equal proportions ($2^2 = 4$).  **[2]**
- The expected phenotypic ratio in the F2 generation is 9:3:3:1, representing 9 round yellow, 3 round green, 3 wrinkled yellow, and 1 wrinkled green peas.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.4801)

**Q1. [Reflection at curved mirror; 1 mark; gold]** Which of the following is dimensionless?

- (a) stress
- (b) force constant
- (c) surface tension
- (d) strain

Key: (d) strain. Why: strain is a ratio of two lengths.

**Q2. [DC Circuits; 1 mark; computed]** A cell of emf $24\ \text{V}$ and internal resistance $2\ \Omega$ is connected to an external resistance of $4\ \Omega$. Find the current in the circuit.

- (a) $4\ \text{A}$
- (b) $144\ \text{A}$
- (c) $12\ \text{A}$
- (d) $6\ \text{A}$

Key: (a) $4\ \text{A}$. Why: For a cell with internal resistance $I = \dfrac{E}{R + r}$. $I = \dfrac{E}{R+r} = \dfrac{24}{4+2}$ $I = 4\ \text{A}$

**Q3. [Nuclear physics; 1 mark; teacher]** What is the formula for the nuclear radius $R$ as a function of the mass number $A$?

- (a) $R=A^{1/2}$
- (b) $R=R_0A^{1/3}$
- (c) $R=R_0A^2$
- (d) $R=R_0A$

Key: (b) $R=R_0A^{1/3}$. Why: The formula $R=R_0A^{1/3}$ directly states the relationship between nuclear radius and mass number as given.

**Q4. [Electric field; 1 mark; gold]** Just outside the surface of a charged conductor with surface charge density $\sigma$, the field is

- (a) $\sigma\varepsilon_0$
- (b) $\sigma/2\varepsilon_0$
- (c) $\sigma/\varepsilon_0$
- (d) zero

Key: (c) $\sigma/\varepsilon_0$. Why: the factor of two that appears for a thin non-conducting sheet is absent here, because all the charge lies on one face and there is no field inside the metal.

**Q5. [Physical Quantities; 3 marks; teacher]** Derive and check the dimensional correctness of the formula $T = 2\pi\sqrt{l/g}$ for the time period of a simple pendulum. Explain why this method cannot determine the constant $2\pi$.

Marking scheme:

- Dimensions: $T = [T]$, $l = [L]$, $g = [L T^{-2}]$. 2.  **[1]**
- Check: $[T] = \sqrt{[L]/[L T^{-2}]} = [T]$. 3.  **[1]**
- Method of dimensions verifies units but not numerical constants like $2\pi$.  **[1]**

**Q6. [Nuclear physics; 5 marks; teacher]** Explain the concept of pair production in nuclear physics and justify why it requires a minimum energy of $1.02\ \text{MeV}$ and must occur in the vicinity of a nucleus.

Marking scheme:

- Pair production involves the creation of an electron-positron pair from a photon.  **[2]**
- It needs at least $1.02\ \text{MeV}$ because this is the total rest mass energy of both particles ($2 \times 0.511\ \text{MeV}$).  **[1]**
- This process must happen near a nucleus due to the need to conserve both energy and momentum; the nucleus provides a rest frame to balance the momentum.  **[1]**
- Additionally, the high electric field near a nucleus facilitates the conversion of photon energy into particle mass.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5011)

**Q1. [Ecology; 1 mark; gold]** The pyramid of numbers in a single big tree with birds and their parasites is

- (a) upright
- (b) rectangular
- (c) inverted
- (d) spindle-shaped

Key: (d) spindle-shaped. Why: one tree carries many birds, and each bird carries very many parasites, so the pyramid is narrow, wide, wider still at the top.

**Q2. [Faunal Diversity; 1 mark; gold]** The hormone controlling metamorphosis in the frog is

- (a) thyroxine
- (b) adrenaline
- (c) auxin
- (d) insulin

Key: (a) thyroxine. Why: thyroxine from the thyroid gland; a tadpole deprived of iodine never becomes a frog.

**Q3. [Biota and Environment; 1 mark; teacher]** Which of the following statements accurately describes an adaptation of the Ganges river dolphin (Platanista gangetica) living in the Karnali and Koshi rivers?

- (a) It relies on strong vision to navigate murky waters.
- (b) It uses echolocation due to being nearly blind.
- (c) It breathes air through specialized gills.
- (d) It has developed large fins to aid in swimming against currents.

Key: (b) It uses echolocation due to being nearly blind.. Why: The Ganges dolphin is nearly blind and uses echolocation in murky water.

**Q4. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 20$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $20$
- (b) $5$
- (c) $10$
- (d) $40$

Key: (c) $10$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{20}{2}$ $n = 10$

**Q5. [Biomolecules and Cell Biology; 2 marks; teacher]** Define mitosis and state what it results in terms of chromosome number and genetic constitution in the daughter cells.

Marking scheme:

- Mitosis is the equational division of a somatic cell resulting in two daughter cells.  **[1]**
- Each daughter cell has the same chromosome number and genetic constitution as the parent cell.  **[1]**

**Q6. [Floral Diversity; 5 marks; teacher]** Describe the structure of fungal mycelium, its growth pattern, and explain how mycorrhizal fungi contribute to nutrient absorption in plants like pine and oak.

Marking scheme:

- The fungal body, except in unicellular yeasts, is a mycelium, which is a network of hyphae.  **[1]**
- Each hypha is a tubular structure containing cytoplasm enclosed within a chitinous cell wall, extending only at its tip.  **[1]**
- Mycorrhizal fungi form symbiotic associations with plant roots, specifically those of pine and oak trees.  **[1]**
- These fungi significantly enhance the host plant's ability to absorb phosphates, an essential nutrient, thereby improving plant nutrition and growth.  **[1]**
- This mutualistic relationship aids in the efficient recycling of nutrients back into the soil.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.6191)

**Q1. [Polarization; 1 mark; gold]** Light reflected from water at the polarizing angle is polarized with its electric vector

- (a) in the plane of incidence
- (b) at random
- (c) along the direction of travel
- (d) perpendicular to the plane of incidence

Key: (d) perpendicular to the plane of incidence. Why: the component in the plane of incidence is not reflected at $\theta_p$, leaving only the perpendicular one.

**Q2. [Thermoelectric effects; 1 mark; teacher]** For a thermocouple with its cold junction at $0\,^{\circ}\text{C}$, which formula represents the thermo-e.m.f. $E$ in microvolts as a function of temperature $\theta$?

- (a) $E = 25\theta - 0.05\theta^{2}$
- (b) $E = 50\theta - 0.01\theta^{2}$
- (c) $E = 10\theta + 0.1\theta^{2}$
- (d) $E = 25 + 0.05\theta$

Key: (a) $E = 25\theta - 0.05\theta^{2}$. Why: For a thermocouple with its cold junction at $0\,^{\circ}\text{C}$, the thermo-e.m.f. in microvolts is $E = 25\theta - 0.05\theta^{2}$.

**Q3. [Magnetic field; 1 mark; computed]** A straight wire of length $10\ \text{cm}$ carrying a current of $2\ \text{A}$ is placed perpendicular to a magnetic field of $40\ \text{mT}$. Find the force on the wire.

- (a) $0.0008\ \text{N}$
- (b) $0.008\ \text{N}$
- (c) $0.08\ \text{N}$
- (d) $0.8\ \text{N}$

Key: (b) $0.008\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 40\times10^{-3}\times2\times10\times10^{-2}$ $F = 0.008\ \text{N}$

**Q4. [Electrical circuits; 1 mark; gold]** A potentiometer is called a voltmeter of infinite resistance because

- (a) it reads the terminal voltage of the driver
- (b) its wire has infinite resistance
- (c) at balance it draws no current from the cell being measured
- (d) it has a high-resistance galvanometer

Key: (c) at balance it draws no current from the cell being measured. Why: at the null point no current flows through the cell under test, so its terminal p.d. equals its e.m.f.

**Q5. [Rotational dynamics; 2 marks; teacher]** Calculate the power output of an electric motor delivering a constant torque of $25\ \text{N m}$ at $1500$ rev min⁻¹.

Marking scheme:

- First, convert $1500$ rev min⁻¹ to rad s⁻¹: $1500 \times \frac{2\pi}{60} = 157.08$ rad s⁻¹.  **[1]**
- Power $P = \tau \omega = 25 \times 157.08 = 3927$ W or $3.93$ kW.  **[1]**

**Q6. [Fluid statics; 5 marks; teacher]** Calculate the work done in blowing a soap bubble of radius $3\ \text{cm}$ and determine the excess pressure inside it, given that the surface tension $T = 0.03\ \text{N m}^{-1}$. Additionally, explain how surface tension changes with temperature and the effect of detergents on it.

Marking scheme:

- The work done to blow a soap bubble of radius $3\ \text{cm}$ is $W = 8\pi R^2 T = 8\pi (0.03)^2 (0.03) = 2.26\times10^{-4}\ \text{J}$.  **[2]**
- The excess pressure inside the bubble is $4T/R = 4(0.03)/(0.03) = 4\ \text{Pa}$.  **[2]**
- Surface tension decreases with increasing temperature and is reduced by detergents.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.8785)

**Q1. [Chemistry of Non-metals; 1 mark; gold]** The percentage of nitrogen in ammonium nitrate, NH₄NO₃, is

- (a) 17.5 %
- (b) 46.7 %
- (c) 21.2 %
- (d) 35.0 %

Key: (d) 35.0 %. Why: M = 80 and 2 N atoms give 28, so 28/80 × 100 = 35.0 %.

**Q2. [Hydrocarbons; 1 mark; teacher]** What is the molar mass of ethene?

- (a) $28\ \text{g}\ \text{mol}^{-1}$
- (b) $30\ \text{g}\ \text{mol}^{-1}$
- (c) $56\ \text{g}\ \text{mol}^{-1}$
- (d) $26\ \text{g}\ \text{mol}^{-1}$

Key: (a) $28\ \text{g}\ \text{mol}^{-1}$. Why: The molar mass of ethene is calculated as 2(12) + 4(1) = 28 g mol⁻¹.

**Q3. [Modern Chemical Manufactures; 1 mark; teacher]** Which chemical reaction correctly represents the process of recovering ammonia using $\text{Ca(OH)}_2$?

- (a) $\text{NH}_4\text{Cl} + \text{Ca(OH)}_2 \rightarrow \text{NH}_3 + \text{CaCl}_2 + \text{H}_2\text{O}$
- (b) $2\text{NH}_4\text{Cl} + \text{Ca(OH)}_2 \rightarrow 2\text{NH}_3 + \text{CaCl}_2 + 2\text{H}_2\text{O}$
- (c) $\text{NH}_4\text{Cl} + \text{Ca(OH)}_2 \rightarrow 2\text{NH}_3 + \text{CaCl}_2 + \text{H}_2\text{O}$
- (d) $2\text{NH}_4\text{Cl} + \text{Ca(OH)}_2 \rightarrow 2\text{NH}_4 + \text{CaCl}_2 + 2\text{H}_2\text{O}$

Key: (b) $2\text{NH}_4\text{Cl} + \text{Ca(OH)}_2 \rightarrow 2\text{NH}_3 + \text{CaCl}_2 + 2\text{H}_2\text{O}$. Why: The given reaction precisely matches the formula provided for the recovery of ammonia using $\text{Ca(OH)}_2$.

**Q4. [Foundation and Fundamentals; 1 mark; computed]** How many molecules are present in $0.5\ \text{mol}$ of a substance? ($N_A = 6.022\times10^{23}\ \text{mol}^{-1}$)

- (a) $6.022\times10^{23}\ \text{molecules}$
- (b) $3.011\times10^{22}\ \text{molecules}$
- (c) $3.011\times10^{23}\ \text{molecules}$
- (d) $3.011\times10^{21}\ \text{molecules}$

Key: (c) $3.011\times10^{23}\ \text{molecules}$. Why: Number of particles $N = n\times N_A$ with $N_A = 6.022\times10^{23}\ \text{mol}^{-1}$. $N = nN_A = 0.5\times6.022\times10^{23}$ $N = 3.011\times10^{23}$

**Q5. [Foundation and Fundamentals; 3 marks; teacher]** Calculate the mass of one molecule of water and explain how industrial chemists use mole ratios in reactions. Include the formula to calculate the percentage composition of an element.

Marking scheme:

- Mass of one water molecule: $\dfrac{18}{6.022\times10^{23}}=2.99\times10^{-23}\ \text{g}$.  **[1]**
- Chemists use mole ratios from balanced equations to plan reaction quantities.  **[1]**
- Formula for element's % composition: $\%\text{ of element}=\dfrac{\text{mass of the element in one mole}}{\text{molar mass}}\times100$.  **[1]**

**Q6. [Chemical Bonding and Shapes of Molecules; 5 marks; teacher]** Using VSEPR theory, predict and explain the shape of $\text{H}_2\text{O}$ molecule. Account for its bond angle based on the presence of lone pairs. Include the number of lone pairs present on each atom.

Marking scheme:

- The $\text{H}_2\text{O}$ molecule has a bent shape due to the presence of two lone pairs on the oxygen atom.  **[2]**
- Oxygen has six valence electrons; forming two bonds with hydrogen leaves four electrons as two lone pairs.  **[1]**
- These lone pairs repel the bonding pairs, reducing the bond angle from ideal tetrahedral (109.5°) to approximately 104.5°.  **[1]**
- The molecule has 2 lone pairs on the oxygen atom and no lone pairs on the hydrogen atoms.  **[1]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.3057)

**Q1. [Studies of Heavy Metals; 1 mark; gold]** The formula of zinc blende is

- (a) ZnCO₃
- (b) ZnSO₄·7H₂O
- (c) ZnO
- (d) ZnS

Key: (d) ZnS. Why: zinc blende is the sulphide; ZnCO₃ is calamine and ZnO is zincite.

**Q2. [Alcohols; 1 mark; gold]** Phenol is more acidic than ethanol mainly because

- (a) the phenoxide ion is resonance stabilised
- (b) it contains a benzene ring
- (c) it has a higher molar mass
- (d) it is a solid

Key: (a) the phenoxide ion is resonance stabilised. Why: the negative charge is delocalised over C-2, C-4 and C-6, which is impossible in an alkoxide ion.

**Q3. [Aldehydes and Ketones; 1 mark; gold]** Ethylmagnesium bromide poured on solid CO₂ and then hydrolysed gives

- (a) ethanoic acid
- (b) propanoic acid
- (c) propan-1-ol
- (d) ethanol

Key: (b) propanoic acid. Why: carbonation adds one carbon to the ethyl group.

**Q4. [Electrochemistry; 1 mark; computed]** A cell transfers $n = 2$ moles of electrons with $E^\circ_{\text{cell}} = 0.46\ \text{V}$. Calculate $\Delta G^\circ$ in kJ ($F = 96500\ \text{C mol}^{-1}$).

- (a) $-178\ \text{kJ}$
- (b) $-44.4\ \text{kJ}$
- (c) $-88.8\ \text{kJ}$
- (d) $-888\ \text{kJ}$

Key: (c) $-88.8\ \text{kJ}$. Why: $\Delta G^\circ = -nFE^\circ_{\text{cell}}$. $\Delta G^\circ = -2\times 96500\times 0.46\ \text{J}$ $\Delta G^\circ = -88.8\ \text{kJ}$

**Q5. [Chemical Kinetics; 2 marks; gold]** Draw the potential-energy profile for an exothermic reaction with and without a catalyst. If a catalyst lowers the activation energy from 75 kJ mol⁻¹ to 50 kJ mol⁻¹, by what factor does the rate increase at 300 K?

Marking scheme:

- The diagram is the one in §3.9(d): the same reactant and product levels, the same $\Delta H$, but a lower peak for the catalysed path.  **[1]**
- The rates are in the ratio of the exponential factors:  **[1]**

**Q6. [Electrochemistry; 5 marks; gold]** a) Arrange the four metals and hydrogen in an activity series. [2] b) For E°(Zn²⁺/Zn) = −0.76 V and E°(Fe³⁺/Fe²⁺) = +0.77 V, write the cell notation, the cell reaction and the emf. [3] (NEB 2079 model; data re-set for (b))

Marking scheme:

- (a) C is displaced by none, so it is the most reactive.  **[2]**
- D and C displace hydrogen, so both are above H.  **[1]**
- B and A are below hydrogen (they do not displace it), and B displaces A but not the reverse.  **[1]**
- Series in decreasing activity: C > D > H > B > A.(b) Zn is oxidised, and Fe³⁺ is reduced to Fe²⁺ at an inert platinum electrode:  **[1]**

## Mathematics - Class 11 (NEB)  (`math11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.9558)

**Q1. [Trigonometric Equations and General Values; 1 mark; gold]** If $\tan\theta = \tan\alpha$ then $\theta$ equals

- (a) $2n\pi\pm\alpha$
- (b) $2n\pi+\alpha$
- (c) $n\pi+(-1)^{n}\alpha$
- (d) $n\pi+\alpha$

Key: (d) $n\pi+\alpha$. Why: tangent has period $\pi$.

**Q2. [Anti-derivatives; 1 mark; computed]** Evaluate $\displaystyle\int_{0}^{1}\left(6x^{2} + 4x\right)dx$.

- (a) $4$
- (b) $8$
- (c) $10$
- (d) $6$

Key: (a) $4$. Why: By the power rule of integration $\displaystyle\int x^{n}dx = \dfrac{x^{n+1}}{n+1}$. $\displaystyle\int_0^{1}(6x^{2}+4x)dx = \left[\dfrac{6x^{3}}{3} + \dfrac{4x^{2}}{2}\right]_0^{1}$ $= 4$

**Q3. [Computational Methods; 1 mark; teacher]** What is the total length obtained when the logarithmic lengths of $2.5$ and $3.2$ are placed end to end on a logarithmic scale?

- (a) 0.803
- (b) 0.90309
- (c) 1.003
- (d) 0.703

Key: (b) 0.90309. Why: The sum of the logarithmic lengths $\log 2.5 = 0.398$ and $\log 3.2 = 0.505$ equals $0.90309$.

**Q4. [Vectors; 1 mark; teacher]** Why is the scalar product $\vec{a}\cdot\vec{b}$ equal to $|\vec{a}|(|\vec{b}|\cos\theta)$?

- (a) It measures the perpendicular distance from $\vec{a}$ to $\vec{b}$.
- (b) It is the sum of the magnitudes of $\vec{a}$ and $\vec{b}$.
- (c) It represents the length of $\vec{a}$ times the length of the projection of $\vec{b}$ onto $\vec{a}$.
- (d) It calculates the angle $\theta$ between $\vec{a}$ and $\vec{b}$ directly.

Key: (c) It represents the length of $\vec{a}$ times the length of the projection of $\vec{b}$ onto $\vec{a}$.. Why: The scalar product formula given is derived from the projection of one vector onto another, which aligns with the provided explanation.

**Q5. [Curve Sketching; 2 marks; gold]** Sketch $y = \dfrac{1}{2x-6}$, showing the asymptotes, the intercept and the monotonic intervals.

Marking scheme:

- $y = \frac{1}{2x-6}$.  **[1]**
- The denominator vanishes at $2x - 6 = 0$, i.e.  **[1]**

**Q6. [Anti-derivatives; 5 marks; teacher]** Given the velocity function $v(t) = 3t^{2}-4t+2$, find the displacement function $s(t)$ if the initial condition is $s(0) = 5$. Also, evaluate the integral $\int\left(x+2+\frac{1}{x}\right)dx$.

Marking scheme:

- To find $s(t)$, integrate $v(t) = 3t^{2}-4t+2$: $$s(t) = \int (3t^{2}-4t+2) dt = t^{3}-2t^{2}+2t + C.$$ Applying the initial condition $s(0) = 5$, we get $C = 5$.  **[2]**
- Thus, $s(t) = t^{3}-2t^{2}+2t+5$.  **[2]**
- Next, evaluate $\int\left(x+2+\frac{1}{x}\right)dx$: $$\int\left(x+2+\frac{1}{x}\right)dx = \frac{x^{2}}{2} + 2x + \ln|x| + C.$$  **[1]**

## Mathematics - Class 12 (NEB)  (`math12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.1646)

**Q1. [Conic Sections; 1 mark; gold]** $\int\frac{dx}{x^{2}+2x+2}$ equals

- (a) $\frac{1}{2}\tan^{-1}(x+1)+C$
- (b) $\tan^{-1}(x+2)+C$
- (c) $\log|x^{2}+2x+2|+C$
- (d) $\tan^{-1}(x+1)+C$

Key: (d) $\tan^{-1}(x+1)+C$. Why: complete the square: $\int\frac{dx}{(x+1)^{2}+1} = \tan^{-1}(x+1)$. Machine-checked.

**Q2. [Derivatives; 1 mark; teacher]** When evaluating the indeterminate form $1^{\infty}$, which method should you apply to transform it into a determinate form?

- (a) Take the logarithm, $\ln y = g \ln f$, and evaluate the limit of $\ln y$.
- (b) Apply L'Hopital's rule directly to the original form.
- (c) Convert the expression into a polynomial and solve.
- (d) Directly substitute the values into the function.

Key: (a) Take the logarithm, $\ln y = g \ln f$, and evaluate the limit of $\ln y$.. Why: The correct approach for transforming the indeterminate form $1^{\infty}$ into a determinate form is by taking the logarithm as described.

**Q3. [Anti-derivatives; 1 mark; teacher]** Evaluate the definite integral $\int_{0}^{\pi}x\sin x\,dx$.

- (a) $0$
- (b) $\pi$
- (c) $-\pi$
- (d) $2\pi$

Key: (b) $\pi$. Why: The calculation follows integration by parts, leading to the result $\pi$.

**Q4. [Product of Vectors; 1 mark; computed]** Find the scalar product of $\vec{a} = 6\hat{i} + 5\hat{j} + 5\hat{k}$ and $\vec{b} = 2\hat{i} + 5\hat{j} + 4\hat{k}$.

- (a) $60$
- (b) $17$
- (c) $57$
- (d) $27$

Key: (c) $57$. Why: The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$. $\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = 6\times2+5\times5+5\times4$ $\vec{a}\cdot\vec{b} = 57$

**Q5. [Complex Numbers; 2 marks; teacher]** Given two complex numbers $z_1=3\text{cis}\,\frac{\pi}{6}$ and $z_2=2\text{cis}\,\frac{\pi}{3}$, find the product $z_1z_2$ and express it in polar form.

Marking scheme:

- Using $z_1z_2=r_1r_2\,\text{cis}(\theta_1+\theta_2)$, we get $z_1z_2=3\cdot2\,\text{cis}\left(\frac{\pi}{6}+\frac{\pi}{3}\right)=6\,\text{cis}\,\frac{\pi}{2}$.  **[2]**

**Q6. [Conic Sections; 5 marks; gold]** a) Find the foci and the centre of the hyperbola $9x^{2}-16y^{2}-144=0$. [2] b) A parabolic reflector is $20$ cm in diameter and $5$ cm deep. Find the position of its focus. [3] (NEB 2080 Q21a; NEB 2081 Q4)

Marking scheme:

- (a) Divide by $144$: $\dfrac{x^{2}}{16}-\dfrac{y^{2}}{9}=1$.  **[2]**
- So $a=4$, $b=3$, $c=\sqrt{16+9}=5$, and the centre is the origin.  **[1]**
- Foci: $(\pm5,\,0)$.(b) Place the vertex at the origin and the axis along the $y$-axis: $x^{2}=4ay$.  **[1]**
- The rim of the reflector is $10$ cm from the axis and $5$ cm from the vertex, so $(10,5)$ lies on the parabola:  **[1]**

## Computer Science - Class 11 (NEB)  (`cs11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.9843)

**Q1. [Computer Software and Operating System; 1 mark; gold]** Which of the following is NOT a function of an operating system?

- (a) memory management
- (b) device management
- (c) file management
- (d) designing web pages

Key: (d) designing web pages. Why: designing pages is the job of application tools, not of the OS.

**Q2. [Web Technology I; 1 mark; teacher]** What is the standard markup language used to create the structure of web pages?

- (a) HTML
- (b) JavaScript
- (c) XML
- (d) CSS

Key: (a) HTML. Why: HTML (HyperText Markup Language) is explicitly stated as the standard markup language used to create the structure of web pages.

**Q3. [Multimedia; 1 mark; teacher]** Why is the World Wide Web considered unique among hypermedia systems?

- (a) It was the first hypermedia system created.
- (b) It is the largest hypermedia system ever built.
- (c) It operates independently of the internet.
- (d) It can only be accessed through specific software.

Key: (b) It is the largest hypermedia system ever built.. Why: The statement directly identifies the World Wide Web as the largest hypermedia system ever built.

**Q4. [Programming Concepts and Logics; 1 mark; computed]** Convert the binary number $11110_{2}$ to decimal.

- (a) $31$
- (b) $4$
- (c) $30$
- (d) $60$

Key: (c) $30$. Why: A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two). $1\times16+1\times8+1\times4+1\times2+0\times1$ $= 30$

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

**Q1. [Web Technology II; 1 mark; gold]** Which function is used to connect to a MySQL database?

- (a) mysqli_open()
- (b) $mysqli_con() (NEB 2080)
- (c) var mysqli_query()
- (d) mysqli_connect()

Key: (d) mysqli_connect(). Why: mysqli_connect($server, $user, $pass, $db);

**Q2. [Software Process Model; 1 mark; teacher]** Why is the SDLC represented as a cycle?

- (a) Maintenance generates new requirements that initiate another cycle.
- (b) The cycle symbolizes the constant improvement of software aesthetics.
- (c) It represents the linear progression from development to deployment.
- (d) Each phase is independent and does not influence the others.

Key: (a) Maintenance generates new requirements that initiate another cycle.. Why: Maintenance produces new requirements that start the next round, indicating a cyclical nature.

**Q3. [Recent Trends in Technology; 1 mark; teacher]** A sensor records data every 5 seconds. How many readings does it record in one day?

- (a) $8{,}640$
- (b) $17{,}280$
- (c) $5{,}184$
- (d) $34{,}560$

Key: (b) $17{,}280$. Why: The calculation $\dfrac{24 \times 60 \times 60}{5}$ correctly yields the total number of readings as $17{,}280$.

**Q4. [Data Communication and Networking; 1 mark; computed]** What is the minimum number of bits needed to represent $100$ different values?

- (a) $2\ \text{bits}$
- (b) $13\ \text{bits}$
- (c) $7\ \text{bits}$
- (d) $6\ \text{bits}$

Key: (c) $7\ \text{bits}$. Why: $k$ bits can represent $2^k$ values, so $k = \lceil\log_2 n\rceil$. $k = \lceil\log_2 100\rceil$ $k = 7\ \text{bits}$

**Q5. [Database Management System; 3 marks; teacher]** Explain how the network model differs from a hierarchical model in terms of parent-child relationships.

Marking scheme:

- In the network model (CODASYL, 1971), a record can have multiple parents, unlike in a hierarchical model where each record has only one parent.  **[2]**
- This makes the network model's structure a graph instead of a tree.  **[1]**

**Q6. [Data Communication and Networking; 5 marks; teacher]** Explain the addressing capability of IPv6, its approach to multicasting, and calculate the number of cables and ports required in a full mesh network with 8 nodes.

Marking scheme:

- IPv6 provides $3.4\times10^{38}$ addresses and utilizes multicast instead of broadcast.  **[2]**
- In a full mesh network with 8 nodes, the number of cables needed is calculated as $\frac{n(n-1)}{2} = \frac{8\times7}{2} = 28$ cables.  **[1]**
- Each node requires $n-1 = 7$ ports.  **[1]**
- This setup ensures direct links between all pairs without needing NAT.  **[1]**
