# Verbatim samples from the shipped specialist packs (planner seed 11)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5528)

**Q1. [Animal Tissues; 1 mark; gold]** The type of cell that makes up about 99 % of the formed elements of blood is

- (a) RBC
- (b) platelets
- (c) WBC
- (d) plasma cell

Key: (a) RBC. Why: red cells outnumber white cells by about 600 : 1.

**Q2. [Plant Physiology; 1 mark; teacher]** Which statement best describes the process of the ascent of sap in plants?

- (a) The diffusion of oxygen into the leaves from the atmosphere through stomata.
- (b) The upward movement of water and dissolved minerals from the roots to the leaves through the xylem.
- (c) The absorption of carbon dioxide by roots from the soil.
- (d) The downward transport of sugars from the leaves to the roots through the phloem.

Key: (b) The upward movement of water and dissolved minerals from the roots to the leaves through the xylem.. Why: The ascent of sap refers specifically to the upward movement of water and minerals through the xylem.

**Q3. [Genetics; 1 mark; teacher]** In a test cross involving a double heterozygote yielding 1600 offspring with 96 being recombinants, what is the recombination frequency between the two genes and the corresponding map distance?

- (a) The recombination frequency is $\frac{96}{1600} \times 100 = 6\%$, and the map distance is $6$ centimorgans.
- (b) The recombination frequency is $\frac{96}{1600} \times 100 = 6\%$, and the map distance is $12$ centimorgans.
- (c) The recombination frequency is $\frac{1504}{1600} \times 100 = 94\%$, and the map distance is $94$ centimorgans.
- (d) The recombination frequency is $\frac{96}{1600} \times 100 = 6\%$, and the map distance is $3$ centimorgans.

Key: (a) The recombination frequency is $\frac{96}{1600} \times 100 = 6\%$, and the map distance is $6$ centimorgans.. Why: The recombination frequency is calculated as the ratio of recombinant offspring to the total number of offspring multiplied by 100, and map distance in centimorgans equals the recombination frequency.

**Q4. [Human Biology; 1 mark; computed]** A person has a heart rate of $80\ \text{beats min}^{-1}$ and a stroke volume of $60\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $48\ \text{L min}^{-1}$
- (b) $4.8\ \text{L min}^{-1}$
- (c) $9.6\ \text{L min}^{-1}$
- (d) $1.33\ \text{L min}^{-1}$

Key: (b) $4.8\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 80\times 60\ \text{mL min}^{-1}$ $CO = 4.8\ \text{L min}^{-1}$

**Q5. [Human Biology; 3 marks; teacher]** Describe the process of absorption in the human digestive system, specifying the pathways for sugars, amino acids, and fats.

Marking scheme:

- Absorption involves transferring end products from the lumen into blood or lymph.  **[1]**
- Sugars and amino acids enter blood capillaries.  **[1]**
- Fats exit as chylomicrons into lacteals.  **[1]**

**Q6. [Developmental Biology; 5 marks; teacher]** Describe the initial stages of oogenesis and the fate of the primary follicle during female reproductive development, including the approximate number of primary follicles present at birth, puberty, and those that typically mature in a woman's lifetime.

Marking scheme:

- Oogenesis initiates with the formation of primary follicles containing oocytes arrested at prophase I of meiosis I.  **[1]**
- At birth, a female has approximately 2 million primary follicles.  **[1]**
- By puberty, this number reduces to about 400,000.  **[1]**
- Throughout her reproductive life, only around 400 of these primary follicles will mature into ovum.  **[1]**
- The reduction in number is due to programmed cell death and maturation processes.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.4801)

**Q1. [Reflection at curved mirror; 1 mark; gold]** The focal length of a plane mirror is

- (a) infinite
- (b) equal to the object distance
- (c) zero
- (d) $R/2$ with $R$ finite

Key: (a) infinite. Why: a plane mirror is a spherical mirror of infinite radius, so $f = R/2 \to \infty$.

**Q2. [Physical Quantities; 1 mark; teacher]** Why does the dimensional analysis on the equation $T = 2\pi\sqrt{l/g}$ not confirm the presence of the factor $2\pi$?

- (a) Because the value of $2\pi$ can vary based on the system of units used.
- (b) Because dimensional analysis only verifies the consistency of dimensions and does not account for dimensionless constants.
- (c) Because the factor $2\pi$ is determined experimentally and not theoretically.
- (d) Because $2\pi$ is always a constant and doesn't affect the physical dimensions.

Key: (b) Because dimensional analysis only verifies the consistency of dimensions and does not account for dimensionless constants.. Why: Dimensional analysis only verifies the consistency of dimensions and does not account for dimensionless constants.

**Q3. [Dynamics; 1 mark; teacher]** In a physics experiment involving a pulley system, what condition is assumed about the pulley to ensure all torque contributes to the motion of the objects?

- (a) massless
- (b) elastic
- (c) frictional
- (d) rigid

Key: (a) massless. Why: The pulley is assumed to be massless so that all torque contributes to the motion of the objects.

**Q4. [Ideal gas; 1 mark; computed]** Find the pressure of $5\ \text{mol}$ of an ideal gas confined in $30\ \text{L}$ at $250\ \text{K}$. (Take $R = 8.314\ \text{J mol}^{-1}\text{K}^{-1}$.)

- (a) $692\ \text{kPa}$
- (b) $346\ \text{kPa}$
- (c) $41.7\ \text{kPa}$
- (d) $173\ \text{kPa}$

Key: (b) $346\ \text{kPa}$. Why: For an ideal gas $PV = nRT$. $P = \dfrac{nRT}{V} = \dfrac{5\times8.314\times250}{30}$ $P = 346\ \text{kPa}$

**Q5. [DC Circuits; 3 marks; teacher]** Two light bulbs are rated at 100 W and 60 W respectively, both for 220 V operation. If connected in parallel to a 220 V source, which bulb will be brighter and why? Explain using their resistances.

Marking scheme:

- The 100 W bulb will be brighter.  **[1]**
- Both bulbs operate at 220 V.  **[1]**
- The 100 W bulb has a resistance of $484\ \Omega$, while the 60 W bulb has $807\ \Omega$.  **[1]**

**Q6. [Nuclear physics; 5 marks; teacher]** Explain the concept of pair production in nuclear physics and justify why it requires a minimum energy of $1.02\ \text{MeV}$ and must occur in the vicinity of a nucleus.

Marking scheme:

- Pair production involves the creation of an electron-positron pair from a photon.  **[2]**
- It needs at least $1.02\ \text{MeV}$ because this is the total rest mass energy of both particles ($2 \times 0.511\ \text{MeV}$).  **[1]**
- This process must happen near a nucleus due to the need to conserve both energy and momentum; the nucleus provides a rest frame to balance the momentum.  **[1]**
- Additionally, the high electric field near a nucleus facilitates the conversion of photon energy into particle mass.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5011)

**Q1. [Ecology; 1 mark; gold]** Gross primary productivity minus respiration of the producers equals

- (a) net primary productivity
- (b) standing crop
- (c) secondary productivity
- (d) biomass

Key: (a) net primary productivity. Why: NPP = GPP − R; only NPP is available to the next level.

**Q2. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 24$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $48$
- (b) $12$
- (c) $24$
- (d) $6$

Key: (b) $12$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{24}{2}$ $n = 12$

**Q3. [Floral Diversity; 1 mark; teacher]** Why does Chlamydomonas possess a red eyespot (stigma)?

- (a) for phototaxis
- (b) to aid in reproduction
- (c) for photosynthesis
- (d) to store energy

Key: (a) for phototaxis. Why: The red eyespot in Chlamydomonas is specifically mentioned to aid in phototaxis.

**Q4. [Biota and Environment; 1 mark; teacher]** Which of the following animals divides its life between land and water?

- (a) whales
- (b) frogs
- (c) seals
- (d) turtles

Key: (b) frogs. Why: Frogs are listed as tertiary (partial) aquatic animals that divide their lives between land and water.

**Q5. [Faunal Diversity; 3 marks; teacher]** Describe the diagnostic feature of Cnidaria and the basic characteristics of sponges.

Marking scheme:

- Cnidaria's diagnostic feature is the cnidoblast, a cell with a nematocyst used for prey capture, defense, and movement.  **[2]**
- Sponges, simplest animals, have a cellular organization level, are aquatic (mostly marine), sessile as adults, and exhibit asymmetry or radial symmetry.  **[1]**

**Q6. [Evolutionary Biology; 5 marks; teacher]** Explain how both fossil evidence of horses and biochemical similarities among organisms support the theory of evolution. Include a brief mention of artificial selection to illustrate the concept.

Marking scheme:

- Fossil records show horse evolution from Eohippus to Equus, demonstrating size increase from 0.3 to 1.6m, reduction in toes from 4 to 1, and dietary shift from browsing to grazing, indicating adaptation.  **[2]**
- Biochemically, all organisms share nucleic acids as genetic material, use the same genetic code, ATP, and 20 standard amino acids; similarities quantify evolutionary relationships.  **[2]**
- Artificial selection, like breeding dogs or crops, shows rapid changes in traits over centuries, suggesting nature could effect gradual changes over eons, supporting evolution.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.6191)

**Q1. [Polarization; 1 mark; gold]** Which of the following cannot be polarized?

- (a) sound waves in air
- (b) radio waves
- (c) light
- (d) X-rays

Key: (a) sound waves in air. Why: sound in air is longitudinal, and a longitudinal wave has no transverse direction to restrict.

**Q2. [Rotational dynamics; 1 mark; teacher]** Which statement is true regarding the equations $v = r\omega$, $s = r\theta$, and $\tau = I\alpha$?

- (a) They require angles to be measured in degrees.
- (b) They are valid only if angles are measured in radians.
- (c) These equations are universally applicable without any conditions.
- (d) They apply to all systems regardless of angular measurement.

Key: (b) They are valid only if angles are measured in radians.. Why: $v = r\omega$, $s = r\theta$ and $\tau = I\alpha$ are true only when angles are in radians.

**Q3. [Fluid statics; 1 mark; teacher]** What is the formula to calculate the height $h$ of capillary rise for a liquid with surface tension $T$, contact angle $\theta$, density $\rho$, and radius $r$?

- (a) $h = \frac{2T\cos\theta}{r\rho g}$
- (b) $h = \frac{2T}{r\rho g\cos\theta}$
- (c) $h = \frac{T\cos\theta}{r\rho g}$
- (d) $h = \frac{2T\sin\theta}{r\rho g}$

Key: (a) $h = \frac{2T\cos\theta}{r\rho g}$. Why: The correct formula includes the factor of 2, cosine of the contact angle, and all other variables as specified in the physics equation for capillary rise.

**Q4. [Magnetic effects of current; 1 mark; computed]** A straight wire of length $40\ \text{cm}$ carrying a current of $7\ \text{A}$ is placed perpendicular to a magnetic field of $90\ \text{mT}$. Find the force on the wire.

- (a) $0.0252\ \text{N}$
- (b) $0.252\ \text{N}$
- (c) $2.52\ \text{N}$
- (d) $25.2\ \text{N}$

Key: (b) $0.252\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 90\times10^{-3}\times7\times40\times10^{-2}$ $F = 0.252\ \text{N}$

**Q5. [Thermoelectric effects; 2 marks; gold]** Explain the Peltier effect. [2]

Marking scheme:

- The Peltier effect: when a current flows across a junction of two different metals, heat is absorbed at the junction for one direction of the current and evolved for the other; this is because the electrons carry different energy in the two metals.  **[2]**

**Q6. [Electrical circuits; 5 marks; teacher]** Given that 80% of the electrical energy is transferred to water, calculate the time required to heat 1 kg of water from $20^\circ C$ to $100^\circ C$. Assume the specific heat capacity of water is $4200\ \text{J kg}^{-1}\text{K}^{-1}$ and the power supplied by the electrical source is 1000 W.

Marking scheme:

- The energy needed to heat 1 kg of water from $20^\circ C$ to $100^\circ C$ is calculated as $Q = m c \Delta T = 1 \times 4200 \times (100 - 20) = 336000\ \text{J}$.  **[2]**
- Since 80% of the electrical energy reaches the water, the total energy supplied by the electrical source is $E = \frac{336000}{0.8} = 420000\ \text{J}$.  **[1]**
- With a power supply of 1000 W, the time taken is $t = \frac{E}{P} = \frac{420000}{1000} = 420\ \text{s}$.  **[1]**
- Therefore, it takes 420 seconds or 7 minutes to heat the water.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.8785)

**Q1. [Chemistry of Non-metals; 1 mark; gold]** For $\text{H}_2 + \text{Cl}_2 \rightleftharpoons 2\text{HCl}$, increasing the pressure

- (a) has no effect
- (b) shifts it left
- (c) shifts it right
- (d) lowers $K_c$

Key: (a) has no effect. Why: $\Delta n = 0$.

**Q2. [Foundation and Fundamentals; 1 mark; teacher]** What formula represents the percentage composition of an element in a compound?

- (a) $\%\text{ of element}=\dfrac{\text{mass of the element}}{\text{total mass of compound}}$
- (b) $\%\text{ of element}=\dfrac{\text{mass of the element in one mole}}{\text{molar mass}}\times100$
- (c) $\%\text{ of element}=\dfrac{\text{number of moles of element}}{\text{molar mass}}\times100$
- (d) $\%\text{ of element}=\dfrac{\text{atomic mass}}{\text{molecular weight}}\times100$

Key: (b) $\%\text{ of element}=\dfrac{\text{mass of the element in one mole}}{\text{molar mass}}\times100$. Why: The provided formula directly matches the definition given in the chemistry textbook for calculating the percentage composition of an element.

**Q3. [Chemical Bonding and Shapes of Molecules; 1 mark; teacher]** What is the shape of $\text{BeF}_2$ based on its molecular structure?

- (a) linear
- (b) bent
- (c) trigonal planar
- (d) tetrahedral

Key: (a) linear. Why: The shape of $\text{BeF}_2$ is linear as it has two bonding pairs and no lone pairs around the central beryllium atom.

**Q4. [Stoichiometry; 1 mark; computed]** A reaction has a theoretical yield of $30\ \text{g}$ but only $8\ \text{g}$ of product is obtained. Calculate the percentage yield.

- (a) $2.4\ \%$
- (b) $26.7\ \%$
- (c) $73.3\ \%$
- (d) $0.267\ \%$

Key: (b) $26.7\ \%$. Why: Percentage yield $= \dfrac{\text{actual yield}}{\text{theoretical yield}}\times100$. $\text{yield} = \dfrac{8}{30}\times100$ $\text{yield} = 26.7\%$

**Q5. [Hydrocarbons; 3 marks; teacher]** Explain the process of polymerisation leading to the formation of polythene and write the chemical equation for the production of acetylene in the laboratory using calcium carbide.

Marking scheme:

- Polymerisation involves joining many ethene molecules to form polythene: $n\,\text{CH}_2{=}\text{CH}_2 \rightarrow (-\text{CH}_2\text{CH}_2-)_n$.  **[2]**
- In lab, acetylene is produced by reacting calcium carbide with water: $\text{CaC}_2 + 2\text{H}_2\text{O} \rightarrow \text{Ca(OH)}_2 + \text{C}_2\text{H}_2$.  **[1]**

**Q6. [Modern Chemical Manufactures; 5 marks; gold]** a) HCl, b) excess $\text{Cl}_2$, c) $\text{CuSO}_4$ solution.

Marking scheme:

- (a) $\text{NH}_3 + \text{HCl} \to \text{NH}_4\text{Cl}$ (white fumes).(b) $\text{NH}_3 + 3\text{Cl}_2 \to \text{NCl}_3 + 3\text{HCl}$ (excess chlorine); with excess ammonia, $8\text{NH}_3 + 3\text{Cl}_2 \to \text{N}_2 + 6\text{NH}_4\text{Cl}$.(c) $\text{CuSO}_4 + 4\text{NH}_3 \to [\text{Cu(NH}_3)_4]\text{SO}_4$ (deep blue; a pale blue precipitate of $\text{Cu(OH)}_2$ first).  **[5]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.3057)

**Q1. [Studies of Heavy Metals; 1 mark; gold]** The red oxide of copper is

- (a) Cu₂O
- (b) CuCO₃
- (c) CuO
- (d) Cu(OH)₂

Key: (a) Cu₂O. Why: cuprous oxide is red; cupric oxide CuO is black.

**Q2. [Chemical Kinetics; 1 mark; teacher]** Which of the following statements correctly describes the relationship between the rate constant ($k$) and the reaction rate for reactions of the same order?

- (a) A smaller $k$ indicates a faster reaction rate at any given concentration.
- (b) The reaction with the larger $k$ proceeds faster at any given concentration.
- (c) The reaction rate decreases as $k$ increases for reactions of the same order.
- (d) The reaction rate is independent of the value of $k$ for reactions of the same order.

Key: (b) The reaction with the larger $k$ proceeds faster at any given concentration.. Why: For reactions of the same order, a larger rate constant $k$ indicates a faster reaction rate at any given concentration.

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

**Q5. [Alcohols; 2 marks; teacher]** Explain the order of ease of dehydration for primary, secondary, and tertiary alcohols and state Saytzeff's rule regarding the formation of alkenes.

Marking scheme:

- The ease of dehydration follows: 3° > 2° > 1°.  **[1]**
- According to Saytzeff's rule, the more substituted (stable) alkene predominates in formation.  **[1]**

**Q6. [Haloalkanes; 5 marks; gold]** a) Identify B. [1] b) Which substitution mechanism occurs, and why? [1] c) What is formed if alcoholic KOH is used instead of aqueous KOH? [2] d) How can nitropropane be obtained from the haloalkane? [1] (NEB 2082)

Marking scheme:

- (a) B = propan-1-ol, CH₃CH₂CH₂OH.(b) SN2. 1-Bromopropane is a primary halide with little steric hindrance, and OH⁻ is a strong nucleophile, so it attacks the carbon from the back in a single step with inversion and no carbocation forms (a primary carbocation is unstable).(c) Alcoholic KOH gives elimination (dehydrohalogenation): CH₃CH₂CH₂Br + KOH(alc.) → CH₃CH=CH₂ + KBr + H₂O, that is propene.(d) By heating with silver nitrite: CH₃CH₂CH₂Br + AgNO₂ → CH₃CH₂CH₂NO₂ + AgBr, giving 1-nitropropane.  **[5]**

## Mathematics - Class 11 (NEB)  (`math11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.9558)

**Q1. [Trigonometric Equations and General Values; 1 mark; gold]** The general solution of $\cos\theta = 0$ is

- (a) $(2n+1)\frac{\pi}{2}$
- (b) $2n\pi$
- (c) $n\pi$
- (d) $n\pi+\frac{\pi}{4}$

Key: (a) $(2n+1)\frac{\pi}{2}$. Why: the cosine vanishes at every odd multiple of $\frac{\pi}{2}$.

**Q2. [Curve Sketching; 1 mark; teacher]** What formula gives the x-coordinate of the vertex for a quadratic equation $ax^2 + bx + c$?

- (a) $x = a-b+c$
- (b) $x = -\frac{b}{2a}$
- (c) $x = b^2-4ac$
- (d) $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$

Key: (b) $x = -\frac{b}{2a}$. Why: The x-coordinate of the vertex for a quadratic equation is given by the formula $x = -\frac{b}{2a}$.

**Q3. [Inverse Circular Functions; 1 mark; teacher]** What is the range of the inverse sine function ($\sin^{-1}$)?

- (a) $-\frac{\pi}{2} \text{ to } \frac{\pi}{2}$
- (b) $-\frac{\pi}{4} \text{ to } \frac{\pi}{4}$
- (c) $0 \text{ to } \pi$
- (d) $-\pi \text{ to } \pi$

Key: (a) $-\frac{\pi}{2} \text{ to } \frac{\pi}{2}$. Why: The range of the inverse sine function is centered on $0$, from $-\pi/2$ to $\pi/2$.

**Q4. [Vectors; 1 mark; computed]** Find the scalar product of $\vec{a} = 2\hat{i} + 6\hat{j} + 2\hat{k}$ and $\vec{b} = 2\hat{i} + 2\hat{j} + 1\hat{k}$.

- (a) $14$
- (b) $18$
- (c) $96$
- (d) $15$

Key: (b) $18$. Why: The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$. $\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = 2\times2+6\times2+2\times1$ $\vec{a}\cdot\vec{b} = 18$

**Q5. [Anti-derivatives; 3 marks; teacher]** Explain why two anti-derivatives of the same function can differ by a constant and how to handle substitutions that do not eliminate all $x$ terms in an integrand.

Marking scheme:

- Two anti-derivatives of the same function differ by a constant $C$, making $F(x)+C$ the general form.  **[1]**
- For substitutions not clearing the integrand, express remaining $x$ terms in $u$.  **[1]**
- This ensures the integral remains in terms of $u$, facilitating integration.  **[1]**

**Q6. [Vectors; 5 marks; teacher]** Given vectors $\vec{a} = \hat{i}+2\hat{j}-\hat{k}$, $\vec{b} = 3\hat{i}-\hat{j}+2\hat{k}$, and $\vec{c} = 5\hat{i}+3\hat{j}$, show that they are linearly dependent and find the relation connecting them.

Marking scheme:

- To prove linear dependence, solve $x\vec{a} + y\vec{b} = \vec{c}$.  **[1]**
- Substituting given values yields equations: $x + 3y = 5$, $2x - y = 3$, $-x + 2y = 0$.  **[1]**
- Solving these, $x=2$ and $y=1$.  **[1]**
- Thus, $2\vec{a} + \vec{b} = \vec{c}$.  **[1]**
- This confirms linear dependence and the relation is $2\vec{a} + \vec{b} - \vec{c} = \vec{0}$.  **[1]**

## Mathematics - Class 12 (NEB)  (`math12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.1646)

**Q1. [Conic Sections; 1 mark; gold]** The slope of the tangent to $y=x^{2}-3x$ at $x=2$ is

- (a) $1$
- (b) $2$
- (c) $-2$
- (d) $4$

Key: (a) $1$. Why: $\frac{dy}{dx}=2x-3 = 4-3 = 1$.

**Q2. [Complex Numbers; 1 mark; teacher]** What equation represents the sum of unity and its complex cube roots equaling zero?

- (a) $1 + i + i^2 = 0$
- (b) $1 + \omega + \omega^{2} = 0$
- (c) $1 + \omega + \omega^{3} = 0$
- (d) $\omega^3 = 1$

Key: (b) $1 + \omega + \omega^{2} = 0$. Why: The equation $1 + \omega + \omega^{2} = 0$ correctly represents the sum of unity and its complex cube roots equating to zero as per the provided statement.

**Q3. [Matrix Based System of Linear Equations; 1 mark; teacher]** When performing the row operation $R_2 \to 2R_1 - R_2$ on an augmented matrix, what does this represent?

- (a) First row doubled minus second row, applied to both coefficients and constants.
- (b) First row minus twice the second row, applied to both coefficients and constants.
- (c) Second row minus twice the first row, applied only to coefficients.
- (d) Second row doubled plus the first row, applied to both coefficients and constants.

Key: (a) First row doubled minus second row, applied to both coefficients and constants.. Why: The operation $R_2 \to 2R_1 - R_2$ correctly describes first row doubled minus second row for both coefficients and constants.

**Q4. [Derivatives; 1 mark; computed]** If $f(x) = 2x^{3} + 5x^{2}$, find $f'(4)$.

- (a) $116$
- (b) $136$
- (c) $34$
- (d) $106$

Key: (b) $136$. Why: By the power rule $\dfrac{d}{dx}x^{n} = nx^{n-1}$. $f'(x) = 3\times2x^{2} + 2\times5x$ $f'(4) = 136$

**Q5. [Derivatives; 2 marks; gold]** Find the rate of change of the volume of a sphere with respect to its surface area when the radius is $7$ cm. [2]

Marking scheme:

- $V=\dfrac43\pi r^{3}$ and $S=4\pi r^{2}$, so $\dfrac{dV}{dr}=4\pi r^{2}$ and $\dfrac{dS}{dr}=8\pi r$:  **[2]**

**Q6. [Conic Sections; 5 marks; gold]** a) Find the foci and the centre of the hyperbola $9x^{2}-16y^{2}-144=0$. [2] b) A parabolic reflector is $20$ cm in diameter and $5$ cm deep. Find the position of its focus. [3] (NEB 2080 Q21a; NEB 2081 Q4)

Marking scheme:

- (a) Divide by $144$: $\dfrac{x^{2}}{16}-\dfrac{y^{2}}{9}=1$.  **[2]**
- So $a=4$, $b=3$, $c=\sqrt{16+9}=5$, and the centre is the origin.  **[1]**
- Foci: $(\pm5,\,0)$.(b) Place the vertex at the origin and the axis along the $y$-axis: $x^{2}=4ay$.  **[1]**
- The rim of the reflector is $10$ cm from the axis and $5$ cm from the vertex, so $(10,5)$ lies on the parabola:  **[1]**

## Computer Science - Class 11 (NEB)  (`cs11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.9843)

**Q1. [Computer Software and Operating System; 1 mark; gold]** Which of the following is a mobile operating system?

- (a) Android
- (b) MS-DOS
- (c) Ubuntu
- (d) Solaris

Key: (a) Android. Why: Android is a mobile OS; Ubuntu and Solaris are desktop or server systems.

**Q2. [Computer System; 1 mark; teacher]** What formula represents the relationship between time period ($T$) and frequency ($f$)?

- (a) $T = f^2$
- (b) $T = 1/f$
- (c) $T = 2f$
- (d) $T = f/2$

Key: (b) $T = 1/f$. Why: The correct relationship between time period and frequency as stated is $T = 1/f$.

**Q3. [Number System and Boolean Logic; 1 mark; teacher]** Why does the output of a NAND gate become $0$ when both inputs are $1$?

- (a) NAND is the inverse of AND; AND(1, 1) = 1, so NAND = 0.
- (b) NAND gates always produce $1$ when both inputs are identical.
- (c) NAND combines OR and NOT functions to produce $0$.
- (d) A NAND gate only outputs $0$ if one input is $0$.

Key: (a) NAND is the inverse of AND; AND(1, 1) = 1, so NAND = 0.. Why: The correct answer is based on the definition of NAND as the inverse of the AND operation where AND(1, 1) equals 1, thus NAND equals 0.

**Q4. [Multimedia; 1 mark; computed]** Find the uncompressed size, in KB, of a $400\times400$ pixel image with a colour depth of $16$ bits per pixel. (1 KB $= 1024$ bytes.)

- (a) $19.5\ \text{KB}$
- (b) $313\ \text{KB}$
- (c) $39.1\ \text{KB}$
- (d) $2500\ \text{KB}$

Key: (b) $313\ \text{KB}$. Why: Image size in bytes is $\dfrac{\text{width}\times\text{height}\times\text{bits per pixel}}{8}$ and 1 KB $= 1024$ bytes. $\text{bits} = 400\times400\times16$ $\text{KB} = \dfrac{\text{bits}}{8\times1024} = 313\ \text{KB}$

**Q5. [Web Technology I; 2 marks; teacher]** Differentiate between domain name registration and web hosting services.

Marking scheme:

- Domain name registration involves renting a name via a registrar and DNS resolution.  **[1]**
- Web hosting provides rented server space for website storage and access.  **[1]**

**Q6. [Programming Concepts and Logics; 5 marks; teacher]** Explain the difference between pre-increment (++x) and post-increment (x++) operators with an example. Also, provide the correct evaluation of the expression 2 + 3 * 4 - 6 / 2, and describe how the number 59 is represented in BCD.

Marking scheme:

- Pre-increment (++x) increments the value before it is used, e.g., if x=10, then y=++x sets y to 11.  **[2]**
- Post-increment (x++) uses the current value first, then increments, e.g., if x=10, then y=x++ sets y to 10.  **[1]**
- The expression 2 + 3 * 4 - 6 / 2 evaluates to 11, following operator precedence rules.  **[1]**
- In BCD, 59 is represented as $0101\ 1001$, where each 4-bit segment corresponds to a decimal digit.  **[1]**

## Computer Science - Class 12 (NEB)  (`cs12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 4.4192)

**Q1. [Web Technology II; 1 mark; gold]** Which of the following is the correct way of defining a variable in PHP?

- (a) $variable_name = value;
- (b) $variable_name = value
- (c) $variable name = value;
- (d) $variable name as value; (NEB 2079)

Key: (a) $variable_name = value;. Why: a PHP variable name starts with $, cannot contain a space, and the statement needs its semicolon.

**Q2. [Database Management System; 1 mark; teacher]** Why does 1NF require every column to hold a single atomic value?

- (a) To increase the storage capacity of the database.
- (b) To eliminate repeating groups within the columns.
- (c) To simplify the process of joining unrelated tables.
- (d) To ensure faster database query execution.

Key: (b) To eliminate repeating groups within the columns.. Why: The requirement ensures there are no repeating groups in the columns as per the definition of 1NF.

**Q3. [Data Communication and Networking; 1 mark; teacher]** What is the network address when using the subnet mask $255.255.255.0$ with the IP address $192.168.10.x$?

- (a) 192.168.10.0
- (b) 192.0.0.0
- (c) 192.168.0.0
- (d) 192.168.10.255

Key: (a) 192.168.10.0. Why: The network address is derived by setting the host octet to 0 with the given subnet mask.

**Q4. [Number systems; 1 mark; computed]** Convert the binary number $11001_{2}$ to decimal.

- (a) $3$
- (b) $25$
- (c) $19$
- (d) $26$

Key: (b) $25$. Why: A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two). $1\times16+1\times8+0\times4+0\times2+1\times1$ $= 25$

**Q5. [Software Process Model; 3 marks; teacher]** Given 260 story points and a sprint capacity of 40 points per sprint, calculate the total number of sprints required. What adjustments would be necessary if the customer added 60 more story points after the second sprint?

Marking scheme:

- Total sprints needed: $\dfrac{260}{40} = 6.5 \rightarrow 7$ sprints.  **[2]**
- If 60 more story points are added after the second sprint, re-evaluation and likely extension to 8 sprints would be required.  **[1]**

**Q6. [Object-Oriented Programming; 5 marks; teacher]** Explain the concept of encapsulation in OOP using the class 'Book' and its objects 'b1' and 'b2'. How does this differ from procedural programming as demonstrated by the example of setting the length of a rectangle to a negative value?

Marking scheme:

- Encapsulation in OOP bundles data and methods within a class.  **[1]**
- In 'Book', 'set()' and 'display()' protect 'title' and 'price' from direct access.  **[1]**
- Objects 'b1' and 'b2' maintain their unique states internally.  **[1]**
- Contrastingly, in procedural programming, variables like 'r.len' can be directly modified anywhere, e.g., 'r.len = -5', bypassing logical constraints.  **[1]**
- OOP prevents such direct modifications, enhancing data integrity and security.  **[1]**
