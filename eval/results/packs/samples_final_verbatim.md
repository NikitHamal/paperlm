# Verbatim samples from the shipped specialist packs (planner seed 11)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.816)

**Q1. [Animal Tissues; 1 mark; gold]** The epithelium that can stretch when the urinary bladder is filled is

- (a) transitional
- (b) simple cuboidal
- (c) simple squamous
- (d) ciliated columnar

Key: (a) transitional. Why: transitional epithelium lets the cells slide over one another.

**Q2. [Plant Physiology; 1 mark; teacher]** In a vacuolated plant cell at $T = 295$ K, if the osmotic pressure ($\Psi_s$) is calculated using the formula $-(1)(0.2)(0.00831)(T)$, what is the value of $\Psi_s$?

- (a) -0.69 MPa
- (b) -0.49 MPa
- (c) -0.89 MPa
- (d) -0.29 MPa

Key: (b) -0.49 MPa. Why: In a vacuolated cell the matric component is negligible against the large vacuolar solute effect, and gravity is negligible below about 10 m. $T = 295$ K; $\Psi_s = -(1)(0.2)(0.00831)(295) = -0.49$ MPa.

**Q3. [Genetics; 1 mark; teacher]** In a genetic cross analysis, if the calculated value of $0.470$ is compared to the critical value of $7.815$, what conclusion can be drawn regarding the fit to the 9 : 3 : 3 : 1 phenotypic ratio?

- (a) The deviation is not significant; the data agree with the 9 : 3 : 3 : 1 ratio.
- (b) The calculated value exceeds the critical value, rejecting the hypothesis.
- (c) The deviation is significant, indicating the data do not follow the expected ratio.
- (d) The data suggest a 3 : 1 ratio instead of a 9 : 3 : 3 : 1 ratio.

Key: (a) The deviation is not significant; the data agree with the 9 : 3 : 3 : 1 ratio.. Why: Since $0.470 < 7.815$, it indicates that the deviation is not significant and the data conform to the 9 : 3 : 3 : 1 ratio.

**Q4. [Human Biology; 1 mark; computed]** A person has a heart rate of $60\ \text{beats min}^{-1}$ and a stroke volume of $65\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $39\ \text{L min}^{-1}$
- (b) $3.9\ \text{L min}^{-1}$
- (c) $7.8\ \text{L min}^{-1}$
- (d) $0.923\ \text{L min}^{-1}$

Key: (b) $3.9\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 60\times 65\ \text{mL min}^{-1}$ $CO = 3.9\ \text{L min}^{-1}$

**Q5. [Human Biology; 3 marks; teacher]** Explain the correct dental formula for milk teeth and calculate the heart rate if the R-R interval is 0.75 seconds.

Marking scheme:

- Milk teeth formula is I2 C1 M2 (no premolars), written as 2 1 0 2.  **[2]**
- Heart rate calculation: $\text{heart rate} = \frac{60}{0.75} = 80 \text{ beats per minute}$.  **[1]**

**Q6. [Plant Physiology; 5 marks; teacher]** Describe the process of ATP generation in aerobic respiration and explain the role of kinetin in plant physiology, including its source and application.

Marking scheme:

- Aerobic respiration generates ATP through NADH and FADH₂: $10 \times 3 + 2 \times 2 = 34$ ATP from the electron transport chain, plus 4 direct ATP yields 38 ATP total. 2.  **[2]**
- Kinetin (N$^6$-furfuryladenine), isolated by Miller and Skoog (1955), is derived from DNA breakdown and not naturally occurring in plants. 3.  **[2]**
- It is commercially applied to Thompson Seedless grapes to increase berry size and loosen grape bunches.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.6584)

**Q1. [Reflection at curved mirror; 1 mark; gold]** A concave mirror forms an image of the same size as the object when the object is placed at

- (a) the centre of curvature
- (b) the pole
- (c) the focus
- (d) infinity

Key: (a) the centre of curvature. Why: $u = -R$ gives $v = -R$ and $m = -1$.

**Q2. [Physical Quantities; 1 mark; teacher]** What does the principle of homogeneity state about the terms in a physical equation?

- (a) The terms can be added only if they have different dimensions.
- (b) Every term of a physical equation has the same dimensions.
- (c) Every term must involve at least one fundamental quantity.
- (d) Each term can have different dimensions as long as they balance out.

Key: (b) Every term of a physical equation has the same dimensions.. Why: The principle of homogeneity states that every term of a physical equation has the same dimensions.

**Q3. [Dynamics; 1 mark; teacher]** During a collision between two bodies, if no net external force acts on them, what happens to the momentum?

- (a) Momentum is only transferred from one body to the other.
- (b) Momentum is increased due to internal forces.
- (c) Momentum is created within the system.
- (d) Momentum is lost to the surroundings.

Key: (a) Momentum is only transferred from one body to the other.. Why: In the absence of external forces, momentum is conserved and can only be transferred between the colliding bodies.

**Q4. [Ideal gas; 1 mark; computed]** Find the pressure of $4\ \text{mol}$ of an ideal gas confined in $30\ \text{L}$ at $300\ \text{K}$. (Take $R = 8.314\ \text{J mol}^{-1}\text{K}^{-1}$.)

- (a) $666\ \text{kPa}$
- (b) $333\ \text{kPa}$
- (c) $166\ \text{kPa}$
- (d) $40\ \text{kPa}$

Key: (b) $333\ \text{kPa}$. Why: For an ideal gas $PV = nRT$. $P = \dfrac{nRT}{V} = \dfrac{4\times8.314\times300}{30}$ $P = 333\ \text{kPa}$

**Q5. [DC Circuits; 3 marks; teacher]** Describe the behavior of free electrons in a conductor without a battery and calculate the maximum current in a circuit with zero resistance, using the given values.

Marking scheme:

- Free electrons move randomly at $10^5\ \text{m s}^{-1}$, colliding with ions every $\tau \approx 10^{-14}\ \text{s}$.  **[2]**
- In a short circuit ($R=0$), the current is $I_{max} = \frac{E}{r}$, where $E$ is the electromotive force and $r$ is the internal resistance.  **[1]**

**Q6. [Reflection at curved mirror; 5 marks; teacher]** Explain how the position of an object relative to the focal point ($F$) and center of curvature ($C$) affects the type of image formed by a concave mirror, considering both real and virtual images. Use the mirror formula to support your explanation.

Marking scheme:

- The position of an object relative to $F$ and $C$ on a concave mirror determines the image type.  **[1]**
- When the object is beyond $C$, a real, inverted, and diminished image forms between $F$ and $C$.  **[1]**
- Between $C$ and $F$, the image is real, inverted, and magnified.  **[1]**
- At $F$, no image is formed as rays are parallel.  **[1]**
- Between $F$ and the pole, a virtual, upright, and magnified image is formed.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 4.1341)

**Q1. [Ecology; 1 mark; gold]** Gross primary productivity minus respiration of the producers equals

- (a) net primary productivity
- (b) standing crop
- (c) secondary productivity
- (d) biomass

Key: (a) net primary productivity. Why: NPP = GPP − R; only NPP is available to the next level.

**Q2. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 20$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $40$
- (b) $10$
- (c) $20$
- (d) $5$

Key: (b) $10$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{20}{2}$ $n = 10$

**Q3. [Floral Diversity; 1 mark; gold]** Axile placentation with an obliquely placed bicarpellary ovary is diagnostic of

- (a) Solanaceae
- (b) Brassicaceae
- (c) Fabaceae
- (d) Liliaceae

Key: (a) Solanaceae. Why: Solanaceae; the oblique ovary with a swollen axile placenta is the single best diagnostic character.

**Q4. [Biota and Environment; 1 mark; gold]** Pavlov's dog salivating at the sound of a bell is an example of

- (a) operant conditioning
- (b) classical conditioning
- (c) imprinting
- (d) instinct

Key: (b) classical conditioning. Why: classical conditioning: a neutral stimulus is paired with a natural one until it alone produces the response.

**Q5. [Faunal Diversity; 3 marks; teacher]** Describe the morphological characteristics of Paramecium and explain why it is commonly used as a study subject in educational settings.

Marking scheme:

- Paramecium is slipper-shaped, measuring 170–330 μm, with a blunt anterior and a pointed posterior end.  **[1]**
- It is widely found in ponds and hay infusions.  **[1]**
- Its large size makes it easily observable under a standard school microscope, facilitating educational studies.  **[1]**

**Q6. [Evolutionary Biology; 5 marks; teacher]** Explain how allele frequencies remain unchanged across generations in a population following Mendelian inheritance, and briefly discuss the historical development of evolutionary theory.

Marking scheme:

- In Mendelian inheritance, allele frequencies remain constant across generations due to Hardy-Weinberg equilibrium: $AA$ parents produce only $A$ gametes, while $Aa$ parents produce $A$ and $a$ gametes equally.  **[1]**
- Thus, $p' = p(p + q) = p$ and $q' = q$.  **[1]**
- Historically, Lamarck proposed inheritance of acquired characteristics, which was incorrect.  **[1]**
- Darwin introduced natural selection, which, combined with modern genetics, forms the basis of current evolutionary biology.  **[1]**
- Humans are the sole surviving species of a previously diverse hominin lineage.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.6774)

**Q1. [Polarization; 1 mark; gold]** Unpolarized light of intensity $I_0$ passes through an ideal polaroid. The transmitted intensity is

- (a) $I_0/2$
- (b) $I_0/4$
- (c) $I_0$
- (d) zero

Key: (a) $I_0/2$. Why: the polaroid passes one of the two equal components of the random polarization.

**Q2. [Rotational dynamics; 1 mark; teacher]** Which equation represents the angular position $\theta$ of a rotating object as a function of time when the angular acceleration $\alpha$ is constant?

- (a) $\omega^{2} = \omega_0^{2} + 2\alpha\theta$
- (b) $\theta = \omega_0 t + \frac{1}{2}\alpha t^{2}$
- (c) $s = r\theta$
- (d) $\omega = \omega_0 + \alpha t$

Key: (b) $\theta = \omega_0 t + \frac{1}{2}\alpha t^{2}$. Why: The equation $\theta = \omega_0 t + \frac{1}{2}\alpha t^{2}$ describes the angular position with respect to initial angular velocity and constant angular acceleration over time.

**Q3. [Fluid statics; 1 mark; teacher]** A container filled with water has a depth of $h$. If the density of water is $\rho$ and acceleration due to gravity is $g$, what is the absolute pressure at the bottom of the container if the atmospheric pressure at the surface is $P_0$?

- (a) $P = P_0 + h\rho g$
- (b) $P = \frac{P_0}{h\rho g}$
- (c) $P = h\rho g$
- (d) $P = P_0 - h\rho g$

Key: (a) $P = P_0 + h\rho g$. Why: The absolute pressure at a depth in a fluid is given by the sum of the atmospheric pressure and the gauge pressure.

**Q4. [Magnetic effects of current; 1 mark; computed]** A straight wire of length $40\ \text{cm}$ carrying a current of $7\ \text{A}$ is placed perpendicular to a magnetic field of $90\ \text{mT}$. Find the force on the wire.

- (a) $0.0252\ \text{N}$
- (b) $0.252\ \text{N}$
- (c) $2.52\ \text{N}$
- (d) $25.2\ \text{N}$

Key: (b) $0.252\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 90\times10^{-3}\times7\times40\times10^{-2}$ $F = 0.252\ \text{N}$

**Q5. [Thermoelectric effects; 2 marks; gold]** Explain the Peltier effect. [2]

Marking scheme:

- The Peltier effect: when a current flows across a junction of two different metals, heat is absorbed at the junction for one direction of the current and evolved for the other; this is because the electrons carry different energy in the two metals.  **[2]**

**Q6. [Fluid statics; 5 marks; teacher]** Explain the concept of surface tension and derive the formula for capillary rise. How does the height of capillary rise vary with the radius of the tube?

Marking scheme:

- Surface tension $T$ is defined as the force acting per unit length on an imaginary line on the liquid surface, $T = \frac{F}{l}$, measured in N m$^{-1}$.  **[2]**
- The capillary rise $h$ is given by $h = \frac{2T\cos\theta}{r\rho g}$, where $T$ is surface tension, $\theta$ is contact angle, $r$ is tube radius, $\rho$ is liquid density, and $g$ is gravitational acceleration.  **[2]**
- From this formula, it's evident that $h \propto \frac{1}{r}$, indicating that the height of capillary rise decreases as the tube radius increases.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.941)

**Q1. [Chemistry of Non-metals; 1 mark; gold]** Depletion of the ozone layer is mainly caused by

- (a) chlorofluorocarbons
- (b) $\text{CH}_4$
- (c) $\text{CO}_2$
- (d) $\text{N}_2$

Key: (a) chlorofluorocarbons. Why: chlorine radicals from CFCs catalyse $\text{O}_3 \to \text{O}_2$.

**Q2. [Foundation and Fundamentals; 1 mark; gold]** The empirical formula of a compound is CH₂O and its molecular mass is 60. Its molecular formula is

- (a) C₃H₆O₃
- (b) C₂H₄O₂
- (c) C₆H₁₂O₆
- (d) CH₂O

Key: (b) C₂H₄O₂. Why: EF mass = 30, n = 60/30 = 2.

**Q3. [Chemical Bonding and Shapes of Molecules; 1 mark; gold]** The hybridization of carbon in ethyne is

- (a) $sp$
- (b) $sp^{3}d$
- (c) $sp^{3}$
- (d) $sp^{2}$

Key: (a) $sp$. Why: each carbon forms one $\sigma$ bond to H and one to C, with two $\pi$ bonds.

**Q4. [Stoichiometry; 1 mark; computed]** A reaction has a theoretical yield of $30\ \text{g}$ but only $15\ \text{g}$ of product is obtained. Calculate the percentage yield.

- (a) $4.5\ \%$
- (b) $50\ \%$
- (c) $200\ \%$
- (d) $0.5\ \%$

Key: (b) $50\ \%$. Why: Percentage yield $= \dfrac{\text{actual yield}}{\text{theoretical yield}}\times100$. $\text{yield} = \dfrac{15}{30}\times100$ $\text{yield} = 50\%$

**Q5. [Fundamental Principles of Organic Chemistry; 2 marks; gold]** Using these effects, explain: (i) the order HCOOH > CH₃COOH > CH₃CH₂COOH in acid strength; (ii) why phenol is more acidic than ethanol; (iii) why aniline is a weaker base than ammonia.

Marking scheme:

- (i) The methyl group in CH₃COOH is +I and pushes electron density onto the carboxylate, destabilising the anion; the ethyl group in CH₃CH₂COOH is a still stronger +I group.  **[2]**

**Q6. [Modern Chemical Manufactures; 5 marks; gold]** a) HCl, b) excess $\text{Cl}_2$, c) $\text{CuSO}_4$ solution.

Marking scheme:

- (a) $\text{NH}_3 + \text{HCl} \to \text{NH}_4\text{Cl}$ (white fumes).(b) $\text{NH}_3 + 3\text{Cl}_2 \to \text{NCl}_3 + 3\text{HCl}$ (excess chlorine); with excess ammonia, $8\text{NH}_3 + 3\text{Cl}_2 \to \text{N}_2 + 6\text{NH}_4\text{Cl}$.(c) $\text{CuSO}_4 + 4\text{NH}_3 \to [\text{Cu(NH}_3)_4]\text{SO}_4$ (deep blue; a pale blue precipitate of $\text{Cu(OH)}_2$ first).  **[5]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.4853)

**Q1. [Studies of Heavy Metals; 1 mark; gold]** The red oxide of copper is

- (a) Cu₂O
- (b) CuCO₃
- (c) CuO
- (d) Cu(OH)₂

Key: (a) Cu₂O. Why: cuprous oxide is red; cupric oxide CuO is black.

**Q2. [Chemical Kinetics; 1 mark; gold]** In a plot of $\ln k$ against $1/T$ the slope is equal to

- (a) $-E_a/2.303R$
- (b) $-E_a/R$
- (c) $\ln A$
- (d) $+E_a/R$

Key: (b) $-E_a/R$. Why: from $\ln k = \ln A - E_a/RT$.

**Q3. [Electrochemistry; 1 mark; computed]** Calculate the mass of copper deposited when a current of $1\ \text{A}$ is passed through $\text{CuSO}_4$ solution for $30$ minutes. (Cu $= 63.5$, $F = 96500\ \text{C mol}^{-1}$.)

- (a) $0.592\ \text{g}$
- (b) $2.37\ \text{g}$
- (c) $1.18\ \text{g}$
- (d) $0.395\ \text{g}$

Key: (a) $0.592\ \text{g}$. Why: Faraday's first law gives $m = \dfrac{M I t}{nF}$. $m = \dfrac{MIt}{nF} = \dfrac{63.5\times1\times30\times60}{2\times96500}$ $m = 0.592\ \text{g}$

**Q4. [Aldehydes and Ketones; 1 mark; gold]** Ethylmagnesium bromide poured on solid CO₂ and then hydrolysed gives

- (a) ethanoic acid
- (b) propanoic acid
- (c) ethanol
- (d) propan-1-ol

Key: (b) propanoic acid. Why: carbonation adds one carbon to the ethyl group.

**Q5. [Studies of Heavy Metals; 2 marks; gold]** Compare the Basic Oxygen Process with the Open Hearth Process under three headings.

Marking scheme:

- Oxidant: pure O₂ blown in, versus haematite added to the charge.  **[1]**
- Time: 20–40 minutes, versus 8–10 hours.  **[1]**

**Q6. [Haloalkanes; 5 marks; gold]** a) Identify B. [1] b) Which substitution mechanism occurs, and why? [1] c) What is formed if alcoholic KOH is used instead of aqueous KOH? [2] d) How can nitropropane be obtained from the haloalkane? [1] (NEB 2082)

Marking scheme:

- (a) B = propan-1-ol, CH₃CH₂CH₂OH.(b) SN2. 1-Bromopropane is a primary halide with little steric hindrance, and OH⁻ is a strong nucleophile, so it attacks the carbon from the back in a single step with inversion and no carbocation forms (a primary carbocation is unstable).(c) Alcoholic KOH gives elimination (dehydrohalogenation): CH₃CH₂CH₂Br + KOH(alc.) → CH₃CH=CH₂ + KBr + H₂O, that is propene.(d) By heating with silver nitrite: CH₃CH₂CH₂Br + AgNO₂ → CH₃CH₂CH₂NO₂ + AgBr, giving 1-nitropropane.  **[5]**
