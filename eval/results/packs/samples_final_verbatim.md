# Verbatim samples from the shipped specialist packs (planner seed 16)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5528)

**Q1. [Plant Physiology; 1 mark; gold]** Who proposed the concept of totipotency of plant cells?

- (a) Haberlandt
- (b) Steward
- (c) Skoog
- (d) Murashige

Key: (a) Haberlandt. Why: Gottlieb Haberlandt (1902). Skoog and Miller found kinetin; Murashige and Skoog gave the medium.

**Q2. [Applied Biology; 1 mark; gold]** The earthworm species normally used in vermicomposting is

- (a) Lampito mauritii
- (b) Lumbricus terrestris
- (c) Eisenia fetida
- (d) Pheretima posthuma

Key: (c) Eisenia fetida. Why: Eisenia fetida is epigeic. Lumbricus terrestris is anecic and unsuitable.

**Q3. [Genetics; 1 mark; gold]** The promotion of flowering by a period of low temperature is called

- (a) photoperiodism
- (b) stratification
- (c) scarification
- (d) vernalisation

Key: (d) vernalisation. Why: vernalisation; stratification and scarification are seed-dormancy treatments.

**Q4. [Human Biology; 1 mark; computed]** A person has a heart rate of $75\ \text{beats min}^{-1}$ and a stroke volume of $70\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $5.25\ \text{L min}^{-1}$
- (b) $52.5\ \text{L min}^{-1}$
- (c) $1.07\ \text{L min}^{-1}$
- (d) $10.5\ \text{L min}^{-1}$

Key: (a) $5.25\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 75\times 70\ \text{mL min}^{-1}$ $CO = 5.25\ \text{L min}^{-1}$

**Q5. [Developmental Biology; 2 marks; teacher]** Describe the three parts of the mesoderm and their respective roles in development.

Marking scheme:

- The mesoderm splits into epimere (forms somites → muscles and vertebrae), mesomere (develops into kidney), and hypomere (contains coelom cavity).  **[2]**

**Q6. [Animal Tissues; 5 marks; teacher]** Describe the structure of a multipolar motor neuron observed in a spinal-cord smear under ×100 magnification and explain how nerve impulses are conducted and transmitted.

Marking scheme:

- A multipolar motor neuron features a large cell body containing a prominent nucleus and numerous branching dendrites.  **[1]**
- Nissl granules are present in the cytoplasm of the neuron's cell body.  **[1]**
- The neuron has one axon that conducts impulses away from the cell body.  **[1]**
- Impulse conduction is facilitated by myelin sheath interspersed with nodes of Ranvier, enabling saltatory conduction.  **[1]**
- Transmission occurs chemically at the synapse, which allows unidirectional impulse transfer.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.4801)

**Q1. [Physical Quantities; 1 mark; gold]** The value of $1/4\pi\varepsilon_0$ in SI units is

- (a) $9\times10^{9}$
- (b) $6.67\times10^{-11}$
- (c) $8.85\times10^{-12}$
- (d) $1.6\times10^{-19}$

Key: (a) $9\times10^{9}$. Why: option(b) is $\varepsilon_0$ itself, which is what the $9\times10^{9}$ is built from.

**Q2. [Nuclear physics; 1 mark; teacher]** In a nuclear reaction involving nucleons, what remains constant in terms of quantity?

- (a) The speed of nucleons
- (b) The energy of nucleons
- (c) The total number of nucleons
- (d) The mass of nucleons

Key: (c) The total number of nucleons. Why: Nucleons are neither created nor destroyed, ensuring the conservation of their total number.

**Q3. [Dynamics; 1 mark; gold]** The dimensional formula $[ML^{-1}T^{-2}]$ belongs to

- (a) surface tension
- (b) force constant
- (c) linear momentum
- (d) pressure

Key: (d) pressure. Why: pressure is force per area. Surface tension and force constant are both $[MT^{-2}]$, momentum is $[MLT^{-1}]$.

**Q4. [DC Circuits; 1 mark; computed]** A cell of emf $12\ \text{V}$ and internal resistance $1\ \Omega$ is connected to an external resistance of $4\ \Omega$. Find the current in the circuit.

- (a) $2.4\ \text{A}$
- (b) $4\ \text{A}$
- (c) $12\ \text{A}$
- (d) $60\ \text{A}$

Key: (a) $2.4\ \text{A}$. Why: For a cell with internal resistance $I = \dfrac{E}{R + r}$. $I = \dfrac{E}{R+r} = \dfrac{12}{4+1}$ $I = 2.4\ \text{A}$

**Q5. [Electric field; 3 marks; teacher]** Explain the significance of using a limit $q_0 \to 0$ in determining the electric field and describe the units of measurement for the electric field.

Marking scheme:

- The limit $q_0 \to 0$ ensures the test charge does not affect the field.  **[2]**
- Electric field units are N C⁻¹ or V m⁻¹, indicating force per unit charge or potential difference per distance.  **[1]**

**Q6. [Reflection at curved mirror; 5 marks; teacher]** A concave mirror has a focal length of $f=-20\ \text{cm}$. An object is placed at a distance of $u=-30\ \text{cm}$ from the mirror. Calculate the image distance $v$ and verify the magnification formula using the values obtained.

Marking scheme:

- Given $f=-20\ \text{cm}$ and $u=-30\ \text{cm}$, use the mirror formula: $\dfrac{1}{v}=\dfrac{1}{f}-\dfrac{1}{u}=-\dfrac{1}{20}+\dfrac{1}{30}=-\dfrac{1}{60}$, thus $v=-60\ \text{cm}$.  **[1]**
- Verify magnification: $\dfrac{1}{f}-\dfrac{1}{v}=\dfrac{1}{u}$.  **[1]**
- Substitute $v=-60\ \text{cm}$: $\dfrac{1}{-20}-\dfrac{1}{-60}=\dfrac{1}{-30}$.  **[1]**
- Simplify: $-\dfrac{3}{60}+\dfrac{1}{60}=-\dfrac{2}{60}=-\dfrac{1}{30}$.  **[1]**
- This confirms the magnification formula holds true.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5011)

**Q1. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 24$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $12$
- (b) $48$
- (c) $6$
- (d) $24$

Key: (a) $12$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{24}{2}$ $n = 12$

**Q2. [Biota and Environment; 1 mark; teacher]** What is the carrying capacity $K$ of a fish population in Phewa Tal?

- (a) $K = 9000$
- (b) $K = 7500$
- (c) $K = 8000$
- (d) $K = 8500$

Key: (c) $K = 8000$. Why: The carrying capacity $K$ of a fish population in Phewa Tal is explicitly stated as $K = 8000$.

**Q3. [Floral Diversity; 1 mark; gold]** The three-domain system of classification was proposed by

- (a) R. H. Whittaker
- (b) Carolus Linnaeus
- (c) Ernst Haeckel
- (d) Carl Woese

Key: (d) Carl Woese. Why: Woese (1977, 1990), on the basis of 16S/18S rRNA sequences.

**Q4. [Faunal Diversity; 1 mark; gold]** The scientific name of the Indian bullfrog studied in the CDC course is

- (a) Rana tigrina
- (b) Bufo melanostictus
- (c) Hyla arborea
- (d) Xenopus laevis

Key: (a) Rana tigrina. Why: Rana tigrina (now often Hoplobatrachus tigerinus), the Indian bullfrog.

**Q5. [Evolutionary Biology; 3 marks; teacher]** Describe the concept of speciation using the example of the peppered moth (Biston betularia) in Manchester pre-1850.

Marking scheme:

- Speciation involves gradual variation accumulation over generations, forming a new species.  **[1]**
- Pre-1850 in Manchester, the peppered moth was predominantly light-colored.  **[1]**
- Environmental changes later favored darker variants, illustrating how species can evolve due to natural selection.  **[1]**

**Q6. [Ecology; 5 marks; teacher]** Explain the role of respiration and decomposition in the carbon cycle and how global warming is related to greenhouse gases. Also, state why the pyramid of energy cannot be inverted unlike pyramids of number and biomass.

Marking scheme:

- Respiration in plants, animals, and microbes releases CO₂ into the atmosphere.  **[1]**
- Decomposition breaks down dead matter, also releasing CO₂.  **[1]**
- Greenhouse gases trap heat in the troposphere, leading to global warming.  **[1]**
- The pyramid of energy cannot invert because energy transfer follows the second law of thermodynamics, losing energy as heat at each trophic level ($E_{n+1} = E_n \times 0.1$, where $E$ is energy at trophic levels $n$ and $n+1$).  **[1]**
- In contrast, pyramids of number and biomass may invert due to variations in organism sizes and population densities.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.6191)

**Q1. [Rotational dynamics; 1 mark; teacher]** The formula for the moment of inertia of a body about an axis is given by $I = \sum m r^{2}$. What does this quantity measure in relation to rotational motion?

- (a) Resistance to a change in rotational motion
- (b) Speed of rotation
- (c) Rate of rotational motion
- (d) Torque applied to the body

Key: (a) Resistance to a change in rotational motion. Why: The moment of inertia measures the resistance to a change in rotational motion, analogous to how mass measures resistance in linear motion.

**Q2. [Magnetic field; 1 mark; computed]** A straight wire of length $20\ \text{cm}$ carrying a current of $4\ \text{A}$ is placed perpendicular to a magnetic field of $50\ \text{mT}$. Find the force on the wire.

- (a) $0.004\ \text{N}$
- (b) $0.4\ \text{N}$
- (c) $0.04\ \text{N}$
- (d) $4\ \text{N}$

Key: (c) $0.04\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 50\times10^{-3}\times4\times20\times10^{-2}$ $F = 0.04\ \text{N}$

**Q3. [Fluid statics; 1 mark; gold]** Two capillary tubes of radii $4\ \text{mm}$ and $2\ \text{mm}$ are dipped in the same liquid. The ratio of the heights of rise in them is

- (a) $2:1$
- (b) $1:4$
- (c) $4:1$
- (d) $1:2$

Key: (d) $1:2$. Why: $h\propto 1/r$, so the wider tube gives the smaller rise: $\dfrac{h_{4}}{h_{2}} = \dfrac{r_{2}}{r_{4}} = \dfrac{2}{4} = 1:2$. Option(b) inverts the ratio.

**Q4. [Thermoelectric effects; 1 mark; gold]** Antimony and bismuth are chosen for a thermopile because

- (a) they lie at opposite ends of the thermoelectric series
- (b) they are cheap
- (c) they melt at a high temperature
- (d) they are black

Key: (a) they lie at opposite ends of the thermoelectric series. Why: the widest separation in the series gives the largest thermo-e.m.f.

**Q5. [Electrical circuits; 2 marks; gold]** State and derive Joule's law of heating, and explain why the element of a heater glows red while its copper connecting leads stay cool.

Marking scheme:

- $W = qV = VIt = I^2Rt$, all of which appears as heat since the drift velocity is unchanged.  **[2]**

**Q6. [Polarization; 5 marks; teacher]** Given the refractive index of glass as $1.5$, calculate the polarizing angle ($\theta_p$) and the corresponding angle of refraction. Also, explain how to determine the degree of polarization using the intensities $I_{\max}$ and $I_{\min}$.

Marking scheme:

- Use the formula $\theta_p = \tan^{-1}(n)$ where $n=1.5$.  **[1]**
- Thus, $\theta_p = \tan^{-1}(1.5) = 56.31^\circ$. 2.  **[1]**
- The corresponding angle of refraction can be found using Snell's law, $n_1\sin(\theta_i) = n_2\sin(\theta_r)$.  **[1]**
- For air ($n_1 = 1$) to glass ($n_2 = 1.5$), $\sin(\theta_r) = \frac{\sin(56.31^\circ)}{1.5}$.  **[1]**
- Hence, $\theta_r = 33.69^\circ$. 3.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.8785)

**Q1. [Foundation and Fundamentals; 1 mark; computed]** How many molecules are present in $2\ \text{mol}$ of a substance? ($N_A = 6.022\times10^{23}\ \text{mol}^{-1}$)

- (a) $1.204\times10^{24}\ \text{molecules}$
- (b) $1.204\times10^{22}\ \text{molecules}$
- (c) $2.409\times10^{24}\ \text{molecules}$
- (d) $1.204\times10^{23}\ \text{molecules}$

Key: (a) $1.204\times10^{24}\ \text{molecules}$. Why: Number of particles $N = n\times N_A$ with $N_A = 6.022\times10^{23}\ \text{mol}^{-1}$. $N = nN_A = 2\times6.022\times10^{23}$ $N = 1.204\times10^{24}$

**Q2. [Modern Chemical Manufactures; 1 mark; gold]** In the diaphragm cell the product formed at the cathode is

- (a) oxygen
- (b) sodium metal
- (c) hydrogen
- (d) chlorine

Key: (c) hydrogen. Why: water is reduced in preference to Na⁺, so hydrogen is evolved; sodium metal needs molten NaCl.

**Q3. [Chemical Bonding and Shapes of Molecules; 1 mark; gold]** The shape of the ammonia molecule is

- (a) tetrahedral
- (b) planar
- (c) linear
- (d) trigonal pyramidal

Key: (d) trigonal pyramidal. Why: three bond pairs and one lone pair; (a) ignores the lone pair.

**Q4. [Hydrocarbons; 1 mark; gold]** Which one does not undergo sulphonation with oleum?

- (a) methane
- (b) hexane
- (c) heptane
- (d) 2-methylpropane

Key: (a) methane. Why: the first three members, methane, ethane and propane, do not sulphonate.

**Q5. [Fundamental Principles of Organic Chemistry; 2 marks; teacher]** Why does a C=C double bond not rotate freely? Provide the energy cost associated with breaking the π bond.

Marking scheme:

- The C=C double bond does not rotate freely because rotation would break the π bond.  **[1]**
- The energy required to break this π bond is about 250 $kJ\ mol^{-1}$.  **[1]**

**Q6. [Chemistry of Non-metals; 5 marks; teacher]** Given the reaction between zinc and dilute sulfuric acid, calculate the volume of hydrogen gas liberated at STP when 65 grams of zinc reacts completely. Also, write the balanced chemical equation for the preparation of ammonia using ammonium chloride and slaked lime.

Marking scheme:

- The reaction between zinc and sulfuric acid is $\text{Zn} + \text{H}_2\text{SO}_4 \rightarrow \text{ZnSO}_4 + \text{H}_2$.  **[1]**
- For 65 grams of Zn (1 mole), 1 mole of $\text{H}_2$ is produced.  **[1]**
- At STP, 1 mole of $\text{H}_2$ occupies 22.4 L.  **[1]**
- Thus, 22.4 L of $\text{H}_2$ is liberated.  **[1]**
- The balanced equation for ammonia preparation is $\ce{2NH4Cl + Ca(OH)2 ->[\Delta] CaCl2 + 2NH3^ + 2H2O}$.  **[1]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.3057)

**Q1. [Chemical Kinetics; 1 mark; gold]** The hydrolysis of ethyl acetate in a large excess of water is

- (a) pseudo-first order
- (b) second order
- (c) zero order
- (d) third order

Key: (a) pseudo-first order. Why: truly bimolecular, but $[\text{H}_2\text{O}]$ is constant, so it behaves as first order.

**Q2. [Aldehydes and Ketones; 1 mark; gold]** Bakelite is obtained from methanal and

- (a) urea
- (b) benzene
- (c) phenol
- (d) aniline

Key: (c) phenol. Why: phenol and methanal condense to a cross-linked, three-dimensional thermosetting network.

**Q3. [Electrochemistry; 1 mark; computed]** Calculate the mass of copper deposited when a current of $2\ \text{A}$ is passed through $\text{CuSO}_4$ solution for $40$ minutes. (Cu $= 63.5$, $F = 96500\ \text{C mol}^{-1}$.)

- (a) $3.16\ \text{g}$
- (b) $6.32\ \text{g}$
- (c) $0.0263\ \text{g}$
- (d) $1.58\ \text{g}$

Key: (d) $1.58\ \text{g}$. Why: Faraday's first law gives $m = \dfrac{M I t}{nF}$. $m = \dfrac{MIt}{nF} = \dfrac{63.5\times2\times40\times60}{2\times96500}$ $m = 1.58\ \text{g}$

**Q4. [Alcohols; 1 mark; gold]** Ethanol heated with concentrated H₂SO₄ at 140 °C gives mainly

- (a) ethoxyethane
- (b) ethene
- (c) ethanal
- (d) ethyl hydrogen sulphate

Key: (a) ethoxyethane. Why: 140 °C favours intermolecular dehydration to the ether; 170 °C gives ethene.

**Q5. [Haloalkanes; 3 marks; teacher]** Explain the rate law for the reaction of haloalkanes and what happens if the carbon attached to the halogen is chiral.

Marking scheme:

- The rate law for the reaction of haloalkanes is $\text{rate} = k[\text{R-X}]$, indicating first-order kinetics.  **[2]**
- If the carbon attached to the halogen is chiral, nucleophilic attack can occur from both faces, leading to a racemic mixture due to racemization.  **[1]**

**Q6. [Studies of Heavy Metals; 5 marks; teacher]** Explain how to calculate the percentage of copper in chalcopyrite (CuFeS$_2$) and determine the copper content if the ore is 20% pure chalcopyrite.

Marking scheme:

- Calculate molar mass of CuFeS$_2$: $M(CuFeS_2) = 63.5 + 56 + 2(32) = 183.5$ g/mol. 2.  **[1]**
- Determine %Cu in CuFeS$_2$: $\%Cu = \frac{63.5}{183.5} \times 100 = 34.60\%$. 3.  **[1]**
- Given ore purity as 20%, calculate effective copper content: $0.200 \times 34.60\% = 6.92\%$. 4.  **[1]**
- Thus, copper constitutes 6.92% of the ore by weight. 5.  **[1]**
- This calculation helps assess copper concentration in ores for extraction processes.  **[1]**

## Mathematics - Class 11 (NEB)  (`math11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.9558)

**Q1. [Curve Sketching; 1 mark; gold]** The period of $y = 5\cos 4x$ is

- (a) $\frac{\pi}{2}$
- (b) $2\pi$
- (c) $\frac{\pi}{4}$
- (d) $8\pi$

Key: (a) $\frac{\pi}{2}$. Why: period $= \frac{2\pi}{|b|} = \frac{2\pi}{4} = \frac{\pi}{2}$; the amplitude $5$ is irrelevant.

**Q2. [Computational Methods; 1 mark; teacher]** Which of the following methods involves dividing an interval into $n$ sub-intervals to approximate the definite integral?

- (a) Euler's method
- (b) bisection method
- (c) trapezoidal rule
- (d) Newton's method

Key: (c) trapezoidal rule. Why: The trapezoidal rule is specifically derived for approximating integrals by dividing the area under the curve into trapezoids.

**Q3. [Inverse Circular Functions; 1 mark; gold]** $\sin^{-1}\left(\frac12\right)$ is

- (a) $\frac{\pi}{3}$
- (b) $\frac{\pi}{4}$
- (c) $\frac{5\pi}{6}$
- (d) $\frac{\pi}{6}$

Key: (d) $\frac{\pi}{6}$. Why: principal value in $[-\pi/2,\pi/2]$; $5\pi/6$ also has sine $\frac12$ but is outside the range.

**Q4. [Anti-derivatives; 1 mark; computed]** Evaluate $\displaystyle\int_{0}^{1}\left(3x^{2} + 2x\right)dx$.

- (a) $2$
- (b) $4$
- (c) $5$
- (d) $3$

Key: (a) $2$. Why: By the power rule of integration $\displaystyle\int x^{n}dx = \dfrac{x^{n+1}}{n+1}$. $\displaystyle\int_0^{1}(3x^{2}+2x)dx = \left[\dfrac{3x^{3}}{3} + \dfrac{2x^{2}}{2}\right]_0^{1}$ $= 2$

**Q5. [Vectors; 2 marks; gold]** Prove by vector methods that the diagonals of a parallelogram bisect each other.

Marking scheme:

- Let $OACB$ be a parallelogram with $\vec{OA} = \vec{a}$, $\vec{OB} = \vec{b}$, so $\vec{OC} = \vec{a}+\vec{b}$.  **[1]**
- The midpoint of the diagonal $OC$ has position vector $\dfrac{\vec{a}+\vec{b}}{2}$.  **[1]**

**Q6. [Trigonometric Equations and General Values; 5 marks; teacher]** Given that $\cos\theta = -\frac{1}{\sqrt{2}}$, find the general solution for $\theta$. Use the facts that $\cos(\pi - \alpha) = -\cos(\alpha)$ and $\cos\theta=\cos\alpha \Rightarrow \theta = 2n\pi\pm\alpha$. Show your work.

Marking scheme:

- Given $\cos\theta = -\frac{1}{\sqrt{2}}$, identify $\alpha$ as $\frac{\pi}{4}$ since $\cos(\frac{\pi}{4}) = \frac{1}{\sqrt{2}}$.  **[1]**
- Since cosine is negative, we consider $\pi - \frac{\pi}{4} = \frac{3\pi}{4}$.  **[1]**
- Using $\cos\theta=\cos\alpha \Rightarrow \theta = 2n\pi\pm\alpha$, substitute $\alpha = \frac{3\pi}{4}$ to get $\theta = 2n\pi \pm \frac{3\pi}{4}$.  **[1]**
- Thus, the general solutions are $\theta = 2n\pi + \frac{3\pi}{4}$ and $\theta = 2n\pi - \frac{3\pi}{4}$ where $n \in \mathbb{Z}$.  **[1]**
- This covers all possible values of $\theta$ satisfying the given equation.  **[1]**

## Mathematics - Class 12 (NEB)  (`math12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.1646)

**Q1. [Complex Numbers; 1 mark; gold]** The number of distinct fifth roots of unity is

- (a) $5$
- (b) $2$
- (c) $1$
- (d) infinitely many

Key: (a) $5$. Why: the equation $z^{5}=1$ has exactly $5$ distinct roots.

**Q2. [Anti-derivatives; 1 mark; teacher]** What happens when integrating a single logarithmic or inverse trigonometric function?

- (a) It cannot be integrated directly without additional functions.
- (b) It requires an external factor for integration.
- (c) It is integrated against the invisible factor $1$.
- (d) It is always integrated using substitution methods.

Key: (c) It is integrated against the invisible factor $1$.. Why: A lone logarithm or inverse-trig function is integrated against the invisible factor $1$, as stated in the mathematics text.

**Q3. [Matrix Based System of Linear Equations; 1 mark; gold]** If the system of equations is $p_1x+q_1y=r_1$ and $p_2x+q_2y=r_2$, what is the value of $y$?

- (a) $\frac{r_1q_2-r_2q_1}{p_1q_2-p_2q_1}$
- (b) $\frac{p_1q_2-p_2q_1}{p_1r_2-p_2r_1}$
- (c) $\frac{p_2r_1-p_1r_2}{p_1q_2-p_2q_1}$
- (d) $\frac{p_1r_2-p_2r_1}{p_1q_2-p_2q_1}$

Key: (d) $\frac{p_1r_2-p_2r_1}{p_1q_2-p_2q_1}$. Why: $y = \frac{D_y}{D}$, and $D_y$ replaces the $y$-column by the constants, giving $p_1r_2-p_2r_1$ over $p_1q_2-p_2q_1$. (The paper printed its four options as determinant ratios; they are written out here.)

**Q4. [Product of Vectors; 1 mark; computed]** Find the scalar product of $\vec{a} = 5\hat{i} + 1\hat{j} + 4\hat{k}$ and $\vec{b} = 3\hat{i} + 6\hat{j} + 3\hat{k}$.

- (a) $33$
- (b) $9$
- (c) $45$
- (d) $22$

Key: (a) $33$. Why: The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$. $\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = 5\times3+1\times6+4\times3$ $\vec{a}\cdot\vec{b} = 33$

**Q5. [Product of Vectors; 3 marks; teacher]** Define the scalar product of two vectors and using vector methods, prove that $a^{2} = b^{2}+c^{2}-2bc\cos A$ for any triangle ABC.

Marking scheme:

- Scalar product: $\vec{a} \cdot \vec{b} = |\vec{a}||\vec{b}|\cos\theta$. 2.  **[1]**
- In $\triangle ABC$, let $\vec{BC}=\vec{a}$, $\vec{CA}=\vec{b}$, $\vec{AB}=\vec{c}$. 3.  **[1]**
- Using vector identity: $(\vec{b}-\vec{c})^2 = \vec{b}^2 + \vec{c}^2 - 2\vec{b}\cdot\vec{c} = b^2 + c^2 - 2bc\cos A$, thus $a^2 = b^2 + c^2 - 2bc\cos A$.  **[1]**

**Q6. [Conic Sections; 5 marks; gold]** a) Find the foci and the centre of the hyperbola $9x^{2}-16y^{2}-144=0$. [2] b) A parabolic reflector is $20$ cm in diameter and $5$ cm deep. Find the position of its focus. [3] (NEB 2080 Q21a; NEB 2081 Q4)

Marking scheme:

- (a) Divide by $144$: $\dfrac{x^{2}}{16}-\dfrac{y^{2}}{9}=1$.  **[2]**
- So $a=4$, $b=3$, $c=\sqrt{16+9}=5$, and the centre is the origin.  **[1]**
- Foci: $(\pm5,\,0)$.(b) Place the vertex at the origin and the axis along the $y$-axis: $x^{2}=4ay$.  **[1]**
- The rim of the reflector is $10$ cm from the axis and $5$ cm from the vertex, so $(10,5)$ lies on the parabola:  **[1]**

## Computer Science - Class 11 (NEB)  (`cs11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.9843)

**Q1. [Computer System; 1 mark; gold]** The generation of computers that used integrated circuits is the

- (a) third
- (b) second
- (c) first
- (d) fifth

Key: (a) third. Why: third generation (1964 to 1971) used integrated circuits.

**Q2. [Multimedia; 1 mark; gold]** In 24-bit true colour, the number of colours available is about

- (a) 4.3 billion
- (b) 256
- (c) 16.7 million
- (d) 65,536

Key: (c) 16.7 million. Why: 2²⁴ ≈ 16.7 million.

**Q3. [Number System and Boolean Logic; 1 mark; gold]** The 2's complement of $0101$ (4 bits) is

- (a) 1010
- (b) 1001
- (c) 0110
- (d) 1011

Key: (d) 1011. Why: 1's complement 1010, add 1 gives 1011.

**Q4. [Programming Concepts and Logics; 1 mark; computed]** Convert the binary number $10111_{2}$ to decimal.

- (a) $23$
- (b) $46$
- (c) $24$
- (d) $29$

Key: (a) $23$. Why: A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two). $1\times16+0\times8+1\times4+1\times2+1\times1$ $= 23$

**Q5. [Programming Concepts and Logics; 2 marks; teacher]** What is the output of the factorial program for inputs 7 and 0, and why does the loop not run for input 0?

Marking scheme:

- For input 7, output is $7!$.  **[1]**
- For input 0, output is $1$, as the loop runs zero times, keeping $fact=1$, matching $0!$ mathematically.  **[1]**

**Q6. [Computer Software and Operating System; 5 marks; teacher]** Explain the concept of proprietary software and define the role of an operating system in managing computer operations. Additionally, describe mobile computing and provide examples of devices used in it.

Marking scheme:

- Proprietary software, like Windows and MS Office, is closed-source and requires payment.  **[2]**
- The OS is the system software interfacing users with hardware, being the first program loaded during startup and controlling all other programs.  **[2]**
- Mobile computing involves using wireless-connected portable devices such as smartphones and tablets for work, communication, and accessing information on-the-go.  **[1]**

## Computer Science - Class 12 (NEB)  (`cs12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 4.4192)

**Q1. [Database Management System; 1 mark; gold]** Which statement removes the whole table together with its structure?

- (a) DROP TABLE student_info;
- (b) TRUNCATE TABLE student_info;
- (c) DELETE FROM student_info;
- (d) ALTER TABLE student_info;

Key: (a) DROP TABLE student_info;. Why: DROP destroys structure and data; DELETE/TRUNCATE keep the structure.

**Q2. [Recent Trends in Technology; 1 mark; teacher]** A sensor collects data every 5 seconds. How many readings will it collect in a single day?

- (a) 51840
- (b) 8640
- (c) 17280
- (d) 34560

Key: (c) 17280. Why: The calculation $\dfrac{24 \times 60 \times 60}{5}$ correctly yields 17280 readings per day.

**Q3. [Data Communication and Networking; 1 mark; computed]** What is the minimum number of bits needed to represent $200$ different values?

- (a) $3\ \text{bits}$
- (b) $25\ \text{bits}$
- (c) $7\ \text{bits}$
- (d) $8\ \text{bits}$

Key: (d) $8\ \text{bits}$. Why: $k$ bits can represent $2^k$ values, so $k = \lceil\log_2 n\rceil$. $k = \lceil\log_2 200\rceil$ $k = 8\ \text{bits}$

**Q4. [Software Process Model; 1 mark; teacher]** Why does the system analyst study the business problem?

- (a) To decide what the system must do.
- (b) To choose the programming language.
- (c) To train the end-users.
- (d) To design the user interface.

Key: (a) To decide what the system must do.. Why: The analyst studies the business problem to decide what the system must do.

**Q5. [Object-Oriented Programming; 3 marks; teacher]** Explain the types of inheritance and differentiate between compile-time and run-time polymorphism in OOP.

Marking scheme:

- Inheritance types include single, multilevel, multiple, hierarchical, and hybrid.  **[2]**
- Compile-time polymorphism uses function and operator overloading, while run-time polymorphism utilizes virtual functions and overriding.  **[1]**

**Q6. [Web Technology II; 5 marks; teacher]** Explain the function of 'onsubmit="return validateForm()"' in a web form submission process, and discuss the syntax and parameters of 'mysqli_connect()' function used for connecting to a MySQL database. Also, mention a common mistake students make while learning this topic.

Marking scheme:

- The 'onsubmit="return validateForm()"' prevents form submission if the 'validateForm()' function returns false, ensuring data validation before submission.  **[2]**
- The 'mysqli_connect()' function connects to a MySQL database using the syntax: mysqli_connect(server, username, password, database).  **[1]**
- Parameters include 'server' (e.g., "localhost"), 'username', 'password', and an optional 'database'.  **[1]**
- A frequent error is mixing syntax or habits between different programming languages.  **[1]**
