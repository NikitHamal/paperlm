# Verbatim samples from the shipped specialist packs (planner seed 20)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.508)

**Q1. [Human Biology; 1 mark; computed]** A person has a heart rate of $80\ \text{beats min}^{-1}$ and a stroke volume of $65\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $5.2\ \text{L min}^{-1}$
- (b) $1.23\ \text{L min}^{-1}$
- (c) $10.4\ \text{L min}^{-1}$
- (d) $52\ \text{L min}^{-1}$

Key: (a) $5.2\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 80\times 65\ \text{mL min}^{-1}$ $CO = 5.2\ \text{L min}^{-1}$

**Q2. [Plant Physiology; 1 mark; teacher]** How much energy, in kJ, is approximately released during the complete oxidation of one glucose molecule?

- (a) 1435
- (b) 2870
- (c) 30-32
- (d) 956

Key: (b) 2870. Why: The passage directly states that the complete oxidation of one glucose molecule releases about 2870 kJ.

**Q3. [Developmental Biology; 1 mark; teacher]** If an embryo undergoes 4 cleavages, how many blastomeres will it have?

- (a) $4^2$
- (b) $2^{4}$
- (c) $2 + 4$
- (d) $8$

Key: (b) $2^{4}$. Why: The number of blastomeres after n cleavages is given by $2^n$.

**Q4. [Animal Tissues; 1 mark; gold]** Which cells of connective tissue produce histamine and heparin?

- (a) fibroblasts
- (b) macrophages
- (c) mast cells
- (d) plasma cells

Key: (c) mast cells. Why: mast cell granules hold histamine and heparin. Plasma cells make antibodies.

**Q5. [Genetics; 3 marks; teacher]** Analyse the similarities and differences between DNA and RNA and evaluate their significance.

Marking scheme:

- Similarities: Both DNA and RNA are nucleic acids, store genetic information, and consist of nitrogenous bases, sugar, and phosphate.  **[1]**
- Differences: DNA is double-stranded with deoxyribose sugar, while RNA is single-stranded with ribose.  **[1]**
- Significance: Double-stranded DNA provides stability and accurate replication;  **[1]**

**Q6. [Applied Biology; 5 marks; teacher]** Explain the differences between broad-spectrum and narrow-spectrum antibiotics, providing examples of each type and their respective bacterial targets.

Marking scheme:

- Broad-spectrum antibiotics like tetracycline, chloramphenicol, and ampicillin target both Gram-positive and Gram-negative bacteria. 2.  **[1]**
- Narrow-spectrum antibiotics such as penicillin G, vancomycin, and isoniazid act on a limited range of bacteria. 3.  **[1]**
- Broad-spectrum antibiotics affect a wider variety of pathogens. 4.  **[1]**
- Narrow-spectrum antibiotics are more specific, targeting particular types of bacteria. 5.  **[1]**
- Examples of broad-spectrum include tetracycline and ampicillin; narrow-spectrum examples are penicillin G and vancomycin.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.0935)

**Q1. [DC Circuits; 1 mark; computed]** A cell of emf $12\ \text{V}$ and internal resistance $1\ \Omega$ is connected to an external resistance of $10\ \Omega$. Find the current in the circuit.

- (a) $1.09\ \text{A}$
- (b) $1.2\ \text{A}$
- (c) $1.33\ \text{A}$
- (d) $12\ \text{A}$

Key: (a) $1.09\ \text{A}$. Why: For a cell with internal resistance $I = \dfrac{E}{R + r}$. $I = \dfrac{E}{R+r} = \dfrac{12}{10+1}$ $I = 1.09\ \text{A}$

**Q2. [Physical Quantities; 1 mark; teacher]** How many significant figures are present in the measurement $0.00602$?

- (a) 6
- (b) 3
- (c) 5
- (d) 2

Key: (b) 3. Why: The significant figures in $0.00602$ are the digits 602, which amount to 3.

**Q3. [Electric field; 1 mark; gold]** The electric field at a point inside a charged hollow metal sphere is

- (a) $kQ/r^{2}$
- (b) zero
- (c) $\sigma/\varepsilon_0$
- (d) infinite

Key: (b) zero. Why: the Gaussian surface inside encloses no charge.

**Q4. [Reflection at curved mirror; 1 mark; gold]** The image formed by a convex mirror is always

- (a) virtual, inverted and magnified
- (b) real, erect and diminished
- (c) virtual, erect and diminished
- (d) real, inverted and magnified

Key: (c) virtual, erect and diminished. Why: the reflected rays always diverge, so the image is caught behind the mirror; no object position changes this.

**Q5. [Dynamics; 2 marks; teacher]** A block slides on a surface with kinetic friction coefficient $\mu_k = 0.3$. If the normal force is $N = 100\ \text{N}$ and an external force $P = 40\ \text{N}$ acts on it, calculate the acceleration of the block.

Marking scheme:

- The kinetic friction force is $f_k = \mu_k N = 0.3 \times 100 = 30\ \text{N}$.  **[1]**
- The net force is $P - f_k = 40 - 30 = 10\ \text{N}$, giving $a = 1\ \text{m s}^{-2}$.  **[1]**

**Q6. [Nuclear physics; 5 marks; teacher]** Derive the equation $m^{2}c^{2} - m^{2}v^{2} = m_0^{2}c^{2}$ from the relativistic mass formula $m = m_0/\sqrt{1-v^{2}/c^{2}}$. Then, using the concept of binding energy, calculate the total energy gained if each of the 236 nucleons gains 0.9 MeV.

Marking scheme:

- Start with $m = m_0/\sqrt{1-v^2/c^2}$, square both sides to get $m^2(1-v^2/c^2) = m_0^2$. 2.  **[1]**
- Multiply through by $c^2$ to eliminate fractions: $m^2c^2 - m^2v^2 = m_0^2c^2$. 3.  **[1]**
- For the energy gain calculation, each of the 236 nucleons gains 0.9 MeV. 4.  **[1]**
- Total energy gained is $236 \times 0.9 = 212.4$ MeV. 5.  **[1]**
- Rounded off, the total energy gained is approximately 212 MeV.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.4911)

**Q1. [Faunal Diversity; 1 mark; teacher]** Why do male frogs have a rough dark nuptial pad on the first digit of each forelimb?

- (a) For gripping the female in amplexus
- (b) To increase their jumping distance
- (c) For attracting females through visual display
- (d) To absorb water more efficiently

Key: (a) For gripping the female in amplexus. Why: The nuptial pad is for gripping the female during amplexus.

**Q2. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 46$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $11.5$
- (b) $23$
- (c) $92$
- (d) $46$

Key: (b) $23$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{46}{2}$ $n = 23$

**Q3. [Evolutionary Biology; 1 mark; teacher]** Which of the following species belongs to the orangutan branch and was found in the Nepali Siwaliks?

- (a) Australopithecus
- (b) Ramapithecus
- (c) Homo erectus
- (d) Pan troglodytes

Key: (b) Ramapithecus. Why: The passage explicitly states that Ramapithecus of the Nepali Siwaliks belongs to the orangutan branch.

**Q4. [Ecology; 1 mark; gold]** Pneumatophores, the negatively geotropic breathing roots, are found in

- (a) parasites
- (b) epiphytes
- (c) mangrove plants
- (d) desert plants

Key: (c) mangrove plants. Why: mangroves such as Rhizophora and Avicennia grow in waterlogged saline mud where roots cannot get oxygen.

**Q5. [Floral Diversity; 2 marks; teacher]** What classification system did Linnaeus develop, and what plant features were used in this system?

Marking scheme:

- Linnaeus developed the sexual system.  **[1]**
- Plants were classified based on the number and union of stamens and carpels.  **[1]**

**Q6. [Biota and Environment; 5 marks; teacher]** Describe the adaptations of organisms to their environments by providing two examples each of structural, physiological, and behavioral adaptations.

Marking scheme:

- Structural adaptations include the snow leopard's fur for cold climates and fish fins for aquatic life.  **[2]**
- Physiological adaptations involve concentrated urine in desert animals and high hemoglobin levels in high-altitude species.  **[1]**
- Behavioral adaptations consist of migration in birds to avoid harsh winters, and hibernation in bears during cold seasons.  **[1]**
- These traits enhance survival specific to their habitats.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.1859)

**Q1. [Thermoelectric effects; 1 mark; teacher]** For a thermocouple with its cold junction at $0\,^{\circ}$C, which equation correctly represents the thermo-e.m.f. in microvolts as a function of temperature $\theta$?

- (a) $E = 16\theta - 0.02\theta^{2}$
- (b) $E = 8\theta - 0.04\theta^{2}$
- (c) $E = 16\theta^{2} - 0.02\theta$
- (d) $E = 16\theta + 0.02\theta^{2}$

Key: (a) $E = 16\theta - 0.02\theta^{2}$. Why: For a thermocouple with its cold junction at $0\,^{\circ}$C the thermo-e.m.f. in microvolts is $E = 16\theta - 0.02\theta^{2}$.

**Q2. [Rotational dynamics; 1 mark; teacher]** Why is the angular velocity $\omega$ calculated as $2\pi(120)/60$ in radians per second?

- (a) Because it determines the linear mass density of the rod.
- (b) Because it converts the rotational speed of 120 revolutions per minute into radians per second.
- (c) Because it represents the kinetic energy of the rotating object in joules.
- (d) Because it calculates the moment of inertia of the object about its axis.

Key: (b) Because it converts the rotational speed of 120 revolutions per minute into radians per second. Why: With $\omega = 2\pi(120)/60 = 4\pi = 12.57\ \text{rad s}^{-1}$, $$E_k = \tfrac{1}{2}I\omega^{2} = \tfrac{1}{2}(2.5)(12.57)^{2} = 197\ \text{J}$$ Take a rod of mass $M$ and length $L$, of uniform linear mass density $\lambda = M/L$.

**Q3. [Electrical circuits; 1 mark; teacher]** In proving the balance condition for a Wheatstone bridge, what is the required method involving Kirchhoff's laws?

- (a) Use Ohm's law directly on all resistors.
- (b) Apply the loop law to two loops and divide.
- (c) Sum currents at each node and equate them.
- (d) Integrate the voltage across each resistor.

Key: (b) Apply the loop law to two loops and divide. Why: The correct method for proving the balance condition involves applying the loop law to two loops and dividing them as stated in the standard procedure.

**Q4. [Magnetic field; 1 mark; computed]** A straight wire of length $50\ \text{cm}$ carrying a current of $10\ \text{A}$ is placed perpendicular to a magnetic field of $60\ \text{mT}$. Find the force on the wire.

- (a) $3\ \text{N}$
- (b) $30\ \text{N}$
- (c) $0.3\ \text{N}$
- (d) $0.03\ \text{N}$

Key: (c) $0.3\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 60\times10^{-3}\times10\times50\times10^{-2}$ $F = 0.3\ \text{N}$

**Q5. [Fluid statics; 3 marks; teacher]** Calculate the work done in blowing a soap bubble of radius $3\ \text{cm}$ and determine the excess pressure inside the bubble given the surface tension $T = 0.03\ \text{N m}^{-1}$. Use the formulae for work done $W = 8\pi r^2 T$ and excess pressure $\Delta P = 4T/r$.

Marking scheme:

- Work done: $W = 8\pi(0.03)^2(0.03) = 0.00226\ \text{J}$.  **[1]**
- Excess pressure: $\Delta P = 4(0.03)/(0.03) = 4\ \text{Pa}$.  **[1]**
- Bubble radius $r=3\ \text{cm}=0.03\ \text{m}$ used.  **[1]**

**Q6. [Magnetic field; 5 marks; teacher]** Explain why the magnetic force does not change the speed of a charged particle moving in a magnetic field and derive the expression for the magnetic field along the axis of a solenoid with $n$ turns per unit length.

Marking scheme:

- The magnetic force $\vec{F}$ is always perpendicular to the velocity $\vec{v}$ of a charged particle, leading to no component of the force in the direction of motion.  **[2]**
- Thus, the force does no work, preserving the particle's speed.  **[1]**
- For a solenoid with $n$ turns per unit length, the magnetic field $B$ on-axis is given by $B = \tfrac{1}{2}\mu_0 n I(\sin\alpha_1 + \sin\alpha_2)$, where $I$ is the current, and $\alpha_1$ and $\alpha_2$ are the semi-angles subtended by the solenoid's ends.  **[1]**
- This formula results from summing contributions from each turn over the solenoid's length.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.748)

**Q1. [Hydrocarbons; 1 mark; teacher]** In the process of ozonolysis using zinc as a reagent, what is the primary role of zinc?

- (a) It destroys hydrogen peroxide which could otherwise oxidize the products further.
- (b) It acts as a catalyst to speed up the reaction between ozone and the hydrocarbon.
- (c) It increases the stability of the five-membered ozonide.
- (d) It forms a protective layer over the hydrocarbons.

Key: (a) It destroys hydrogen peroxide which could otherwise oxidize the products further. Why: Zinc is essential because it destroys the hydrogen peroxide that would otherwise oxidize the products further.

**Q2. [Foundation and Fundamentals; 1 mark; computed]** How many molecules are present in $0.25\ \text{mol}$ of a substance? ($N_A = 6.022\times10^{23}\ \text{mol}^{-1}$)

- (a) $1.506\times10^{22}\ \text{molecules}$
- (b) $1.506\times10^{23}\ \text{molecules}$
- (c) $3.011\times10^{23}\ \text{molecules}$
- (d) $1.506\times10^{21}\ \text{molecules}$

Key: (b) $1.506\times10^{23}\ \text{molecules}$. Why: Number of particles $N = n\times N_A$ with $N_A = 6.022\times10^{23}\ \text{mol}^{-1}$. $N = nN_A = 0.25\times6.022\times10^{23}$ $N = 1.506\times10^{23}$

**Q3. [Fundamental Principles of Organic Chemistry; 1 mark; teacher]** In chromatography, what does the retention factor ($R_f$) represent?

- (a) The total distance travelled by the solvent front on the paper.
- (b) The ratio of the distance travelled by the substance to the distance travelled by the solvent front.
- (c) The difference in distances travelled by the substance and the solvent front.
- (d) The rate at which the solvent carries the substance upwards.

Key: (b) The ratio of the distance travelled by the substance to the distance travelled by the solvent front. Why: The retention factor $R_f$ is defined as the distance travelled by the substance divided by the distance travelled by the solvent front.

**Q4. [Chemistry of Non-metals; 1 mark; gold]** Sulphur dioxide is passed over a paper moistened with acidified potassium dichromate. The paper turns

- (a) pink
- (b) black
- (c) green
- (d) blue

Key: (c) green. Why: SO₂ reduces orange Cr(VI) to green Cr(III).

**Q5. [Chemical Bonding and Shapes of Molecules; 2 marks; gold]** Both BeF₂ and H₂O are triatomic, yet BeF₂ is linear and H₂O is bent. Explain.

Marking scheme:

- In BeF₂, $X = \frac{1}{2}(2+2) = 2$: beryllium has two bond pairs and no lone pair, so the pairs get as far apart as possible at 180° and the molecule is linear (sp).  **[2]**

**Q6. [Modern Chemical Manufactures; 5 marks; gold]** a) HCl, b) excess $\text{Cl}_2$, c) $\text{CuSO}_4$ solution.

Marking scheme:

- (a) $\text{NH}_3 + \text{HCl} \to \text{NH}_4\text{Cl}$ (white fumes).(b) $\text{NH}_3 + 3\text{Cl}_2 \to \text{NCl}_3 + 3\text{HCl}$ (excess chlorine); with excess ammonia, $8\text{NH}_3 + 3\text{Cl}_2 \to \text{N}_2 + 6\text{NH}_4\text{Cl}$.(c) $\text{CuSO}_4 + 4\text{NH}_3 \to [\text{Cu(NH}_3)_4]\text{SO}_4$ (deep blue; a pale blue precipitate of $\text{Cu(OH)}_2$ first).  **[5]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.991)

**Q1. [Alcohols; 1 mark; teacher]** Which of the following molecular formulas represents an alkyl halide among the given compounds P, Q, R, S, and T?

- (a) P = C₃H₇Br
- (b) R = CH₂O
- (c) S = C₂H₄O
- (d) Q = C₆H₁₄

Key: (a) P = C₃H₇Br. Why: C₃H₇Br is the only formula representing an alkyl halide among the given options.

**Q2. [Chemical Kinetics; 1 mark; teacher]** In a chemical reaction, if the energy of colliding molecules is exactly at the threshold energy, what additional quantity is necessary to initiate the reaction?

- (a) potential energy
- (b) activation energy
- (c) reactant energy
- (d) kinetic energy

Key: (b) activation energy. Why: The activation energy is defined as the extra energy needed beyond the threshold energy to initiate a reaction.

**Q3. [Haloalkanes; 1 mark; teacher]** Which alkene is formed as the major product when a halogen is removed from carbon C3 in a haloalkane, due to its higher stability?

- (a) But-1-ene
- (b) But-2-ene
- (c) Pent-2-ene
- (d) Prop-1-ene

Key: (b) But-2-ene. Why: But-2-ene is the more stable, more substituted alkene formed as the major product.

**Q4. [Electrochemistry; 1 mark; computed]** A cell transfers $n = 3$ moles of electrons with $E^\circ_{\text{cell}} = 0.8\ \text{V}$. Calculate $\Delta G^\circ$ in kJ ($F = 96500\ \text{C mol}^{-1}$).

- (a) $-116\ \text{kJ}$
- (b) $-464\ \text{kJ}$
- (c) $-232\ \text{kJ}$
- (d) $-77.2\ \text{kJ}$

Key: (c) $-232\ \text{kJ}$. Why: $\Delta G^\circ = -nFE^\circ_{\text{cell}}$. $\Delta G^\circ = -3\times 96500\times 0.8\ \text{J}$ $\Delta G^\circ = -232\ \text{kJ}$

**Q5. [Electrochemistry; 3 marks; gold]** a) What is a standard electrode potential? [1] b) Construct the galvanic cell notation, showing the anode and the cathode. [2]

Marking scheme:

- (a) The standard electrode potential of an electrode is its potential when it is in contact with a 1 M solution of its ions at 25 °C (and 1 atm for gases), measured against the standard hydrogen electrode whose potential is taken as zero.(b) Mg has the more negative potential, so it is the stronger reducing agent: Mg is the anode (oxidation) and Zn the cathode (reduction).  **[3]**

**Q6. [Aldehydes and Ketones; 5 marks; gold]** a) Zn–Hg/conc. HCl, b) NH₂NH₂ followed by KOH in glycol, c) LiAlH₄, d) PCl₅, e) NaHSO₃.

Marking scheme:

- (a) Clemmensen: propane, CH₃CH₂CH₃.(b) Wolff–Kishner: propane (via the hydrazone, with loss of N₂).(c) LiAlH₄: propan-2-ol, CH₃CH(OH)CH₃.(d) PCl₅: 2,2-dichloropropane, CH₃CCl₂CH₃ + POCl₃.(e) NaHSO₃: the white crystalline bisulphite addition compound, (CH₃)₂C(OH)SO₃Na.  **[5]**

## Mathematics - Class 11 (NEB)  (`math11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.8675)

**Q1. [Anti-derivatives; 1 mark; computed]** Evaluate $\displaystyle\int_{0}^{4}\left(9x^{2} + 4x\right)dx$.

- (a) $224$
- (b) $160$
- (c) $256$
- (d) $640$

Key: (a) $224$. Why: By the power rule of integration $\displaystyle\int x^{n}dx = \dfrac{x^{n+1}}{n+1}$. $\displaystyle\int_0^{4}(9x^{2}+4x)dx = \left[\dfrac{9x^{3}}{3} + \dfrac{4x^{2}}{2}\right]_0^{4}$ $= 224$

**Q2. [Curve Sketching; 1 mark; teacher]** A function $f$ is said to be periodic with period $T>0$ if which of the following conditions holds true?

- (a) $f(x+T)=2f(x)$ for all $x$
- (b) $f(x+T)=f(x)$ for all $x$
- (c) $f(x+T)>f(x)$ for all $x$
- (d) $f(x+T)<f(x)$ for all $x$

Key: (b) $f(x+T)=f(x)$ for all $x$. Why: The definition of a periodic function directly states that $f(x+T)=f(x)$ for all $x$.

**Q3. [Vectors; 1 mark; gold]** Three vectors are coplanar if

- (a) they are all unit vectors
- (b) one of them is a linear combination of the other two
- (c) they are mutually perpendicular
- (d) they have equal magnitudes

Key: (b) one of them is a linear combination of the other two. Why: that is the condition for coplanarity.

**Q4. [Trigonometric Equations and General Values; 1 mark; teacher]** What trigonometric identity is used to express $\cos\theta + \cos 3\theta$ as $2\cos 2\theta\cos\theta$?

- (a) Half-angle identity
- (b) Double angle formula
- (c) Sum-to-product identity
- (d) Product-to-sum identity

Key: (c) Sum-to-product identity. Why: The sum-to-product identity allows converting sums of cosines into products, as shown in the expression.

**Q5. [Inverse Circular Functions; 3 marks; teacher]** Prove that $2\tan^{-1}\frac{1}{3}+\tan^{-1}\frac{1}{7}=\frac{\pi}{4}$.

Marking scheme:

- Let $x=\tan^{-1}\frac{1}{3}$, then $\tan x=\frac{1}{3}$.  **[1]**
- Using double angle formula, $\tan 2x=\frac{2\tan x}{1-\tan^2 x}=\frac{2\cdot\frac{1}{3}}{1-(\frac{1}{3})^2}=\frac{3}{4}$.  **[1]**
- Let $y=\tan^{-1}\frac{1}{7}$, so $\tan y=\frac{1}{7}$.  **[1]**

**Q6. [Anti-derivatives; 5 marks; teacher]** Evaluate the integral $\int\frac{2x+1}{(x-1)(x^{2}+1)}\,dx$ using partial fractions, clearly stating the form of the decomposition and justifying it.

Marking scheme:

- To evaluate $\int\frac{2x+1}{(x-1)(x^{2}+1)}\,dx$, decompose into partial fractions as $\frac{A}{x-1} + \frac{Bx+C}{x^2+1}$.  **[1]**
- This form is chosen because $(x-1)$ and $(x^2+1)$ are distinct irreducible factors of the denominator.  **[1]**
- Multiplying both sides by $(x-1)(x^2+1)$ gives $2x+1 = A(x^2+1) + (Bx+C)(x-1)$.  **[1]**
- Solving for coefficients $A$, $B$, and $C$ yields $A=1$, $B=-1$, and $C=2$.  **[1]**
- Thus, the integral becomes $\int\left(\frac{1}{x-1} + \frac{-x+2}{x^2+1}\right)dx$.  **[1]**

## Mathematics - Class 12 (NEB)  (`math12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.9087)

**Q1. [Derivatives; 1 mark; teacher]** What is the derivative of $\sinh x$?

- (a) $\frac{d}{dx}\sinh x = \cosh x$
- (b) $\frac{d}{dx}\sinh x = \sinh x$
- (c) $\frac{d}{dx}\sinh x = \frac{e^x - e^{-x}}{2}$
- (d) $\frac{d}{dx}\sinh x = -\cosh x$

Key: (a) $\frac{d}{dx}\sinh x = \cosh x$. Why: The derivative of $\sinh x$ is defined as $\cosh x$ according to the hyperbolic function derivatives.

**Q2. [Complex Numbers; 1 mark; teacher]** A projectile is launched with an initial velocity $u$ at an angle $\theta$ to the horizontal. If the time of flight is $10$ seconds, the maximum height reached is $125$ meters, and the range is $866$ meters, what is the value of the time of flight $T$?

- (a) $5$ s
- (b) $10$ s
- (c) $125$ m
- (d) $866$ m

Key: (b) $10$ s. Why: The time of flight $T$ is directly given as $10$ seconds in the problem statement.

**Q3. [Product of Vectors; 1 mark; computed]** Find the scalar product of $\vec{a} = 2\hat{i} + 1\hat{j} + 6\hat{k}$ and $\vec{b} = 3\hat{i} + 1\hat{j} + 4\hat{k}$.

- (a) $144$
- (b) $31$
- (c) $17$
- (d) $24$

Key: (b) $31$. Why: The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$. $\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = 2\times3+1\times1+6\times4$ $\vec{a}\cdot\vec{b} = 31$

**Q4. [Conic Sections; 1 mark; teacher]** What condition determines that a line touches a circle at exactly one point?

- (a) Circumference equals area
- (b) Radius equals diameter
- (c) Discriminant is zero
- (d) Slope is undefined

Key: (c) Discriminant is zero. Why: The line touches the circle when the discriminant is zero.

**Q5. [Matrix Based System of Linear Equations; 3 marks; teacher]** Solve the system of linear equations using the Gauss method: $x + 2y + z = 8$, $2x + 3y - z = 5$, $3x - y + 2z = 7$. Express the system in terms of the coefficient matrix $A$, the column of unknowns $X$, and the column of constants $B$. Provide the solution.

Marking scheme:

- The system is expressed as $AX = B$, where $A = \begin{pmatrix}1 & 2 & 1 \\ 2 & 3 & -1 \\ 3 & -1 & 2\end{pmatrix}$, $X = \begin{pmatrix}x \\ y \\ z\end{pmatrix}$, and $B = \begin{pmatrix}8 \\ 5 \\ 7\end{pmatrix}$.  **[2]**
- Using the Gauss method, the solution is $x=2$, $y=1$, $z=3$.  **[1]**

**Q6. [Anti-derivatives; 5 marks; gold]** a) Define a proper rational fraction with an example. [1] b) Integrate $\displaystyle\int\frac{2x^{2}+3}{x^{3}+3x^{2}+2x}\,dx$ using partial fractions. [4] (NEB 2079)

Marking scheme:

- (a) A rational fraction $\dfrac{f(x)}{g(x)}$ is proper if the degree of the numerator is less than the degree of the denominator, for example $\dfrac{x+1}{x^{2}+3x+2}$.(b) The denominator factorises: $x^{3}+3x^{2}+2x=x(x+1)(x+2)$.  **[3]**
- The fraction is proper, so  **[2]**

## Computer Science - Class 11 (NEB)  (`cs11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5669)

**Q1. [Web Technology I; 1 mark; teacher]** Which protocol is used by browsers to send requests to servers?

- (a) HTTP
- (b) SMTP
- (c) TCP
- (d) FTP

Key: (a) HTTP. Why: The passage explicitly mentions that the browser sends an HTTP request to the server.

**Q2. [Computer System; 1 mark; teacher]** Which of the following is an application of computers in telemedicine as described?

- (a) Coordinating public transportation schedules
- (b) A health worker in a remote area consulting a specialist via video call
- (c) Managing financial transactions in rural banks
- (d) Monitoring weather patterns using satellite data

Key: (b) A health worker in a remote area consulting a specialist via video call. Why: The passage explicitly mentions telemedicine for remote consultations with specialists over video calls.

**Q3. [Programming Concepts and Logics; 1 mark; computed]** Convert the binary number $11111_{2}$ to decimal.

- (a) $5$
- (b) $31$
- (c) $32$
- (d) $62$

Key: (b) $31$. Why: A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two). $1\times16+1\times8+1\times4+1\times2+1\times1$ $= 31$

**Q4. [Computer Software and Operating System; 1 mark; gold]** Which of the following is NOT a function of an operating system?

- (a) device management
- (b) file management
- (c) designing web pages
- (d) memory management

Key: (c) designing web pages. Why: designing pages is the job of application tools, not of the OS.

**Q5. [Number System and Boolean Logic; 2 marks; teacher]** Describe the outputs of a half adder when it adds two single bits.

Marking scheme:

- A half adder outputs two values: the sum, which is the XOR of the inputs ($A \oplus B$), and the carry, which is the AND of the inputs ($A \cdot B$).  **[2]**

**Q6. [Multimedia; 5 marks; teacher]** Explain the concept of path animation and provide an example. Additionally, list any two software tools used for video editing and briefly describe the difference between 2D and 3D animation.

Marking scheme:

- Path animation involves an object following a predefined path, such as a bus moving along a road in a presentation.  **[2]**
- Video editing software includes Adobe Premiere Pro and Kdenlive.  **[2]**
- In 2D animation, flat drawings are used to create movement, whereas 3D animation utilizes models that are rendered with lighting and depth, as seen in modern films and games.  **[1]**

## Computer Science - Class 12 (NEB)  (`cs12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.8339)

**Q1. [Software Process Model; 1 mark; teacher]** What economic principle supports the use of reviews, writing a good SRS, and iterative models in software development?

- (a) The earlier a defect is found, the cheaper it is to remove.
- (b) Iterative models reduce the need for thorough reviews.
- (c) Defects increase the availability and efficiency of the software.
- (d) The more defects found, the higher the cost of the project.

Key: (a) The earlier a defect is found, the cheaper it is to remove. Why: This statement directly reflects the economic argument mentioned in support of specific practices in software development.

**Q2. [Database Management System; 1 mark; teacher]** Which rule ensures that data remains correct and accurate by enforcing uniqueness?

- (a) Constraints
- (b) Primary keys
- (c) Foreign keys
- (d) Data types

Key: (b) Primary keys. Why: Primary keys uniquely identify each record in a database table.

**Q3. [Object-Oriented Programming; 1 mark; teacher]** Which type of program is best suited for a procedural approach?

- (a) A banking transaction system
- (b) A Celsius-to-Fahrenheit converter
- (c) A school management system
- (d) A hospital patient record system

Key: (b) A Celsius-to-Fahrenheit converter. Why: The passage explicitly states that a Celsius-to-Fahrenheit converter needs only one function and is best written procedurally.

**Q4. [Data Communication and Networking; 1 mark; computed]** What is the minimum number of bits needed to represent $1000$ different values?

- (a) $125\ \text{bits}$
- (b) $1000\ \text{bits}$
- (c) $10\ \text{bits}$
- (d) $3\ \text{bits}$

Key: (c) $10\ \text{bits}$. Why: $k$ bits can represent $2^k$ values, so $k = \lceil\log_2 n\rceil$. $k = \lceil\log_2 1000\rceil$ $k = 10\ \text{bits}$

**Q5. [Data Communication and Networking; 3 marks; teacher]** Explain the purpose of the OSI model and the process of data transmission through its layers.

Marking scheme:

- The OSI model, published by ISO in 1984, ensures interoperability between different systems by dividing network communication into seven layers.  **[2]**
- Data travels down these layers at the sender, each layer adding a header (encapsulation), then across the medium, and up the layers at the receiver.  **[1]**

**Q6. [Recent Trends in Technology; 5 marks; teacher]** Explain how virtualization enables cloud services like SaaS and provide an example of IoT application in home automation. Include benefits of this technology in your answer.

Marking scheme:

- Virtualization splits one physical server into multiple virtual machines or containers, underpinning cloud services such as SaaS where providers manage all infrastructure, allowing customers to manage only their data.  **[2]**
- An IoT application in home automation involves connecting devices like lights, locks, fans, and cameras to a smartphone for remote control, saving electricity and enhancing security.  **[2]**
- Benefits include efficient resource utilization, cost reduction, and improved accessibility and safety.  **[1]**
