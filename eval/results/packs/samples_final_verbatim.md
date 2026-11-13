# Verbatim samples from the shipped specialist packs (planner seed 21)

Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.

## Biology - Class 12 (NEB)  (`bio12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.508)

**Q1. [Plant Physiology; 1 mark; teacher]** Why does water primarily evaporate from mesophyll cells in plants?

- (a) As a result of high transpiration rates through the cuticle
- (b) Due to direct sunlight exposure on the plant's surface
- (c) From the menisci held in nanometre-scale pores in the mesophyll cell walls — pores of radius 5–10 nm
- (d) From the large open stomatal pores on the leaf surface

Key: (c) From the menisci held in nanometre-scale pores in the mesophyll cell walls — pores of radius 5–10 nm. Why: Evaporation occurs from nanometre-scale pores in the mesophyll cell walls.

**Q2. [Applied Biology; 1 mark; teacher]** What condition must be met to confirm that an organism isolated from an experimental host is responsible for the reproduced disease?

- (a) The organism must be genetically modified before re-isolation.
- (b) The organism must cause a different disease upon re-inoculation.
- (c) The organism must be re-isolated from the experimental host and shown to be the same.
- (d) The organism must be identified by its color alone.

Key: (c) The organism must be re-isolated from the experimental host and shown to be the same. Why: The organism must be re-isolated and confirmed to be the same to prove it reproduces the disease.

**Q3. [Animal Tissues; 1 mark; teacher]** In muscle tissue, what part of the sarcomere is exclusively composed of thin actin filaments?

- (a) A band
- (b) M line
- (c) I band
- (d) Z line

Key: (c) I band. Why: The I band contains only thin actin filaments as stated in the description.

**Q4. [Human Biology; 1 mark; computed]** A person has a heart rate of $70\ \text{beats min}^{-1}$ and a stroke volume of $60\ \text{mL}$. What is the cardiac output in litres per minute?

- (a) $42\ \text{L min}^{-1}$
- (b) $1.17\ \text{L min}^{-1}$
- (c) $4.2\ \text{L min}^{-1}$
- (d) $8.4\ \text{L min}^{-1}$

Key: (c) $4.2\ \text{L min}^{-1}$. Why: Cardiac output $=$ heart rate $\times$ stroke volume. $CO = 70\times 60\ \text{mL min}^{-1}$ $CO = 4.2\ \text{L min}^{-1}$

**Q5. [Developmental Biology; 3 marks; teacher]** Describe the process of neural tube formation and the type of cleavage in frogs.

Marking scheme:

- The neural plate's edges form folds, the middle becomes a groove, and the folds fuse into a neural tube, which develops into the brain and spinal cord.  **[2]**
- Frogs undergo holoblastic but unequal cleavage, where furrows penetrate completely but produce larger yolky vegetal cells.  **[1]**

**Q6. [Genetics; 5 marks; teacher]** Explain Mendel's law of independent assortment using a dihybrid cross (RrYy x RrYy) in pea plants. Predict the phenotypic ratio of the offspring and list all possible gametes formed by a double heterozygote RrYy.

Marking scheme:

- Mendel's law of independent assortment states that genes for different traits separate independently during gamete formation.  **[2]**
- In a dihybrid cross (RrYy x RrYy), a double heterozygote RrYy forms 4 types of gametes: RY, Ry, rY, and ry in equal proportions ($2^2 = 4$).  **[2]**
- The expected phenotypic ratio in the F2 generation is 9:3:3:1, representing 9 round yellow, 3 round green, 3 wrinkled yellow, and 1 wrinkled green peas.  **[1]**

## Physics - Class 11 (NEB)  (`phy11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.0935)

**Q1. [Physical Quantities; 1 mark; teacher]** How many significant figures are there in the measurement $4.700\ \text{m}$?

- (a) 5
- (b) 2
- (c) 4
- (d) 3

Key: (c) 4. Why: The measurement $4.700\ \text{m}$ has four significant figures as all trailing zeros after the decimal point are significant.

**Q2. [Nuclear physics; 1 mark; teacher]** What is the result of differentiating $m^{2}v^{2}$ using the product rule?

- (a) $2m^{2}v^{2}dm$
- (b) $2m^{2}v\,dv$
- (c) $2mv^{2}dm + 2m^{2}v\,dv$
- (d) $2mv^{2}dm$

Key: (c) $2mv^{2}dm + 2m^{2}v\,dv$. Why: The differentiation of $m^{2}v^{2}$ by the product rule yields $2mv^{2}dm + 2m^{2}v\,dv$.

**Q3. [Reflection at curved mirror; 1 mark; teacher]** Which of the following describes the behavior of a ray parallel to the principal axis after reflection from a concave mirror?

- (a) It appears to originate from the focal point $F$.
- (b) It diverges away from the principal axis.
- (c) It passes through the focal point $F$.
- (d) It reflects back along the same path.

Key: (c) It passes through the focal point $F$. Why: A ray parallel to the principal axis reflects through $F$ for a concave mirror.

**Q4. [DC Circuits; 1 mark; computed]** A cell of emf $24\ \text{V}$ and internal resistance $2\ \Omega$ is connected to an external resistance of $10\ \Omega$. Find the current in the circuit.

- (a) $3\ \text{A}$
- (b) $12\ \text{A}$
- (c) $2\ \text{A}$
- (d) $2.4\ \text{A}$

Key: (c) $2\ \text{A}$. Why: For a cell with internal resistance $I = \dfrac{E}{R + r}$. $I = \dfrac{E}{R+r} = \dfrac{24}{10+2}$ $I = 2\ \text{A}$

**Q5. [Electric field; 2 marks; teacher]** Derive the expression for the electric field $E_s$ on the surface of a uniformly charged sphere using the surface charge density.

Marking scheme:

- From Step 6, $E_s = \frac{1}{4\pi\varepsilon_0}\cdot\frac{Q}{R^2}$.  **[1]**
- Using surface charge density $\sigma = \frac{Q}{4\pi R^2}$, rewrite as $E_s = \frac{\sigma}{\varepsilon_0}$.  **[1]**

**Q6. [Dynamics; 5 marks; teacher]** Describe an experiment to determine the coefficient of static friction ($\mu_s$) between a block and an inclined plane using the angle of friction. Include how to calculate $\mu_s$ using the measured height ($h$) and base ($b$) of the incline.

Marking scheme:

- Place a block on a hinged plane. 2.  **[1]**
- Slowly raise one end of the plane until the block just begins to slide. 3.  **[1]**
- Measure the vertical height ($h$) and horizontal base ($b$) of the inclined plane at this point. 4.  **[1]**
- Calculate the angle of inclination ($\theta$) using $\tan\theta = h/b$. 5.  **[1]**
- The coefficient of static friction ($\mu_s$) is equal to $\tan\theta$, so $\mu_s = h/b$.  **[1]**

## Biology - Class 11 (NEB)  (`bio11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.4911)

**Q1. [Biomolecules and Cell Biology; 1 mark; computed]** An organism has $2n = 14$ chromosomes in its somatic cells. How many chromosomes does each gamete contain?

- (a) $28$
- (b) $14$
- (c) $7$
- (d) $3.5$

Key: (c) $7$. Why: Meiosis halves the chromosome number, so a gamete is haploid ($n$). $n = \dfrac{2n}{2} = \dfrac{14}{2}$ $n = 7$

**Q2. [Biota and Environment; 1 mark; teacher]** Which of the following best describes the symbol used to denote the effect of interspecific interactions where one species is neither helped nor harmed?

- (a) $+$
- (b) $-$
- (c) $0$
- (d) $*$

Key: (c) $0$. Why: The symbol $0$ denotes no effect on a species in interspecific interactions.

**Q3. [Ecology; 1 mark; teacher]** Which international agreement aims to limit global warming to $1.5\degree C$?

- (a) Kyoto Protocol (1997)
- (b) Rio Declaration (1992)
- (c) Paris Agreement (2015)
- (d) Montreal Protocol (1987)

Key: (c) Paris Agreement (2015). Why: The Paris Agreement of 2015 specifically targets limiting global warming to $1.5\degree C$.

**Q4. [Faunal Diversity; 1 mark; teacher]** What term describes the mechanism by which a microorganism propels itself forward in a wide spiral pattern using coordinated movement of its cilia?

- (a) Avoiding reaction
- (b) Ciliary beat
- (c) Metachronal rhythm
- (d) Oblique stroke

Key: (c) Metachronal rhythm. Why: The passage explicitly states that the metachronal rhythm drives the animal forward in a wide spiral pattern.

**Q5. [Evolutionary Biology; 3 marks; teacher]** Explain how the rise of the Himalayas influenced evolutionary isolation and provide an example of this process.

Marking scheme:

- The rise of the Himalayas during the Miocene and Pliocene isolated northern and southern faunas, preventing interbreeding.  **[1]**
- This physical barrier led to the division of one fauna into two distinct groups.  **[1]**
- Additionally, it created diverse habitats from Terai to alpine desert within 150 km, further promoting isolation and speciation.  **[1]**

**Q6. [Floral Diversity; 5 marks; teacher]** Describe the floral characteristics of the androecium and gynoecium found in the family Brassicaceae.

Marking scheme:

- In the family Brassicaceae, the androecium consists of 6 stamens arranged in two whorls: an outer pair of two short stamens and an inner quartet of longer stamens, forming a tetradynamous arrangement.  **[2]**
- The androecium is polyandrous and epipetalous.  **[1]**
- The gynoecium is bicarpellary and syncarpous, featuring a superior ovary that initially appears unilocular but becomes bilocular due to a false septum known as the replum.  **[1]**
- Placentation within the ovary is parietal.  **[1]**

## Physics - Class 12 (NEB)  (`phy12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.1859)

**Q1. [Rotational dynamics; 1 mark; teacher]** If a spinning body reduces its moment of inertia, what happens to its angular velocity $\omega$?

- (a) It becomes zero.
- (b) It remains constant.
- (c) It increases.
- (d) It decreases.

Key: (c) It increases. Why: A reduction in moment of inertia with zero external torque results in an increase in angular velocity to conserve angular momentum $L$.

**Q2. [Magnetic field; 1 mark; computed]** A straight wire of length $20\ \text{cm}$ carrying a current of $6\ \text{A}$ is placed perpendicular to a magnetic field of $30\ \text{mT}$. Find the force on the wire.

- (a) $0.0036\ \text{N}$
- (b) $0.36\ \text{N}$
- (c) $0.036\ \text{N}$
- (d) $0.072\ \text{N}$

Key: (c) $0.036\ \text{N}$. Why: The force on a current-carrying conductor in a magnetic field is $F = BIL\sin\theta$. $F = BIL\sin 90^{\circ} = 30\times10^{-3}\times6\times20\times10^{-2}$ $F = 0.036\ \text{N}$

**Q3. [Polarization; 1 mark; teacher]** Which law relates to the angle at which reflected light becomes completely plane-polarized?

- (a) Snell's law
- (b) Huygens's principle
- (c) Brewster's law
- (d) Malus's law

Key: (c) Brewster's law. Why: Brewster's law is mentioned as one of the two formulae the NEB asks for related to polarization.

**Q4. [Thermoelectric effects; 1 mark; teacher]** What is the term used to describe the temperature at which the thermo-electromotive force (e.m.f.) of a thermocouple peaks when the cold junction is at $0\,^\circ C$?

- (a) $\theta_0$
- (b) $\theta_i$
- (c) $\theta_n$
- (d) $2\theta_n$

Key: (c) $\theta_n$. Why: The passage explicitly states that the e.m.f. peaks at the neutral temperature $\theta_n$.

**Q5. [Electrical circuits; 2 marks; teacher]** How do you convert electrical energy dissipated as heat into calories using the formula?

Marking scheme:

- To convert electrical energy $H$ into calories, use $H = \frac{I^2Rt}{J}$, where $J = 4.2\ \text{J cal}^{-1}$.  **[1]**
- This converts joules to calories based on the mechanical equivalent of heat.  **[1]**

**Q6. [Fluid statics; 5 marks; teacher]** Calculate the work done in blowing a soap bubble of radius $3\ \text{cm}$ and determine the excess pressure inside it, given that the surface tension $T = 0.03\ \text{N m}^{-1}$. Additionally, explain how surface tension changes with temperature and the effect of detergents on it.

Marking scheme:

- The work done to blow a soap bubble of radius $3\ \text{cm}$ is $W = 8\pi R^2 T = 8\pi (0.03)^2 (0.03) = 2.26\times10^{-4}\ \text{J}$.  **[2]**
- The excess pressure inside the bubble is $4T/R = 4(0.03)/(0.03) = 4\ \text{Pa}$.  **[2]**
- Surface tension decreases with increasing temperature and is reduced by detergents.  **[1]**

## Chemistry - Class 11 (NEB)  (`chem11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.748)

**Q1. [Foundation and Fundamentals; 1 mark; computed]** How many molecules are present in $5\ \text{mol}$ of a substance? ($N_A = 6.022\times10^{23}\ \text{mol}^{-1}$)

- (a) $3.011\times10^{22}\ \text{molecules}$
- (b) $6.022\times10^{24}\ \text{molecules}$
- (c) $3.011\times10^{24}\ \text{molecules}$
- (d) $3.011\times10^{23}\ \text{molecules}$

Key: (c) $3.011\times10^{24}\ \text{molecules}$. Why: Number of particles $N = n\times N_A$ with $N_A = 6.022\times10^{23}\ \text{mol}^{-1}$. $N = nN_A = 5\times6.022\times10^{23}$ $N = 3.011\times10^{24}$

**Q2. [Modern Chemical Manufactures; 1 mark; teacher]** Why is a long purification train necessary in the production process involving vanadium(V) oxide as a catalyst?

- (a) To increase the yield of the final product.
- (b) To convert iron pyrites into iron oxide.
- (c) To protect the vanadium(V) oxide catalyst from dust, moisture, and arsenic.
- (d) To enhance the reactivity of the vanadium(V) oxide catalyst.

Key: (c) To protect the vanadium(V) oxide catalyst from dust, moisture, and arsenic. Why: The long purification train exists to protect the vanadium(V) oxide catalyst from dust, moisture, and arsenic.

**Q3. [Chemistry of Non-metals; 1 mark; teacher]** Why is ammonia ($\text{NH}_3$) collected by the downward displacement of air?

- (a) It reacts with air to form nitrogen oxides.
- (b) It is denser than air.
- (c) It is lighter than air.
- (d) It is highly soluble in water.

Key: (c) It is lighter than air. Why: Ammonia is collected by the downward displacement of air because it is lighter than air.

**Q4. [Hydrocarbons; 1 mark; teacher]** Which of the following is a method to produce alkynes?

- (a) From $\text{Zn} + \text{HCl}$
- (b) From $\text{NaOH} + \text{CH}_3\text{COOH}$
- (c) From $\text{CaC}_2 + \text{H}_2\text{O}$
- (d) From $\text{H}_2\text{SO}_4 + \text{Na}_2\text{CO}_3$

Key: (c) From $\text{CaC}_2 + \text{H}_2\text{O}$. Why: The passage explicitly states that alkynes can be produced industrially from $\text{CaC}_2 + \text{H}_2\text{O}$.

**Q5. [Fundamental Principles of Organic Chemistry; 3 marks; teacher]** Explain why rotation around a carbon-carbon double bond is restricted and state the approximate energy required to break this bond.

Marking scheme:

- Rotation around a C=C double bond is restricted because it contains a π bond.  **[1]**
- Breaking this π bond requires disrupting the double bond.  **[1]**
- The energy required to break this bond is approximately 250 kJ mol⁻¹.  **[1]**

**Q6. [Chemical Bonding and Shapes of Molecules; 5 marks; teacher]** Using VSEPR theory, predict and explain the shape of $\text{H}_2\text{O}$ molecule. Account for its bond angle based on the presence of lone pairs. Include the number of lone pairs present on each atom.

Marking scheme:

- The $\text{H}_2\text{O}$ molecule has a bent shape due to the presence of two lone pairs on the oxygen atom.  **[2]**
- Oxygen has six valence electrons; forming two bonds with hydrogen leaves four electrons as two lone pairs.  **[1]**
- These lone pairs repel the bonding pairs, reducing the bond angle from ideal tetrahedral (109.5°) to approximately 104.5°.  **[1]**
- The molecule has 2 lone pairs on the oxygen atom and no lone pairs on the hydrogen atoms.  **[1]**

## Chemistry - Class 12 (NEB)  (`chem12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 2.991)

**Q1. [Chemical Kinetics; 1 mark; teacher]** For the reaction $A + 2B \rightarrow C$, if the initial rates at 298 K suggest that doubling the concentration of A doubles the rate while doubling the concentration of B quadruples the rate, what is the overall order of the reaction?

- (a) 4
- (b) 1
- (c) 3
- (d) 2

Key: (c) 3. Why: The reaction is first order with respect to A and second order with respect to B, making the overall order 3.

**Q2. [Aldehydes and Ketones; 1 mark; teacher]** What is the common name for a 37-40% (w/v) aqueous solution of methanal?

- (a) Paraformaldehyde
- (b) Methanol
- (c) Formalin
- (d) Acetaldehyde

Key: (c) Formalin. Why: The passage explicitly defines formalin as a 37-40% (w/v) aqueous solution of methanal.

**Q3. [Studies of Heavy Metals; 1 mark; teacher]** In the process of iron extraction from its oxide, what is the product formed when $\text{Fe}_2\text{O}_3$ reacts with carbon monoxide?

- (a) $\text{Fe}_2\text{O}_3$
- (b) $3\text{CO}$
- (c) $2\text{Fe}$
- (d) $3\text{CO}_2$

Key: (c) $2\text{Fe}$. Why: The reaction produces iron as indicated by the equation $\text{Fe}_2\text{O}_3 + 3\text{CO} \Rightarrow 2\text{Fe} + 3\text{CO}_2$.

**Q4. [Electrochemistry; 1 mark; computed]** A cell transfers $n = 3$ moles of electrons with $E^\circ_{\text{cell}} = 0.46\ \text{V}$. Calculate $\Delta G^\circ$ in kJ ($F = 96500\ \text{C mol}^{-1}$).

- (a) $-66.5\ \text{kJ}$
- (b) $-44.4\ \text{kJ}$
- (c) $-133\ \text{kJ}$
- (d) $-266\ \text{kJ}$

Key: (c) $-133\ \text{kJ}$. Why: $\Delta G^\circ = -nFE^\circ_{\text{cell}}$. $\Delta G^\circ = -3\times 96500\times 0.46\ \text{J}$ $\Delta G^\circ = -133\ \text{kJ}$

**Q5. [Haloalkanes; 3 marks; teacher]** Compare the reaction profiles of S(N)2 and S(N)1 reactions based on the presence of transition states and intermediates.

Marking scheme:

- S(N)2 reaction has one transition state and no intermediate, indicated by a single maximum in its profile.  **[2]**
- S(N)1 reaction has two maxima separated by a minimum, where the minimum represents the carbocation intermediate.  **[1]**

**Q6. [Electrochemistry; 5 marks; teacher]** Describe the operation of a Daniell cell (Zn(s) | Zn²⁺(1 M) || Cu²⁺(1 M) | Cu(s)), including the direction of electron flow and the role of the salt bridge. (5 Marks)

Marking scheme:

- In a Daniell cell, Zn acts as the anode and Cu as the cathode.  **[1]**
- At the Zn anode, Zn(s) oxidizes to Zn²⁺(aq), releasing electrons.  **[1]**
- These electrons flow through the external circuit to the Cu cathode where Cu²⁺(aq) is reduced to Cu(s).  **[1]**
- The overall reaction is Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s).  **[1]**
- A salt bridge maintains electrical neutrality by allowing the movement of ions between the two half-cells, thus completing the circuit.  **[1]**

## Mathematics - Class 11 (NEB)  (`math11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.8675)

**Q1. [Curve Sketching; 1 mark; teacher]** Why does the graph of $y = \frac{1}{ax+b}$ not have an $x$-intercept?

- (a) Because the vertical asymptote shifts the graph away from the x-axis.
- (b) Because the horizontal asymptote is at $y=0$.
- (c) Because the equation $\frac{1}{ax+b} = 0$ has no solution.
- (d) Because the function's domain excludes zero.

Key: (c) Because the equation $\frac{1}{ax+b} = 0$ has no solution. Why: The equation $\frac{1}{ax+b}=0$ has no solution because no value of $x$ can make the denominator infinite or undefined.

**Q2. [Computational Methods; 1 mark; teacher]** In a linear programming problem, what term describes the function $Z = ax + by$ that needs to be maximised or minimised?

- (a) Constraint function
- (b) Non-negativity function
- (c) Objective function
- (d) Optimization limit

Key: (c) Objective function. Why: The term 'objective function' is used to describe the function that needs to be maximized or minimized in a linear programming problem.

**Q3. [Trigonometric Equations and General Values; 1 mark; teacher]** Which equation represents the general solution for $\theta$ when considering the symmetry around $\alpha$ in trigonometric equations?

- (a) $\frac{\theta - \alpha}{2} = m\pi + \frac{\pi}{2}$
- (b) $\theta + \alpha = m\pi$
- (c) $\frac{\theta + \alpha}{2} = m\pi$
- (d) $\frac{\theta + \alpha}{2} = (m+1)\pi$

Key: (c) $\frac{\theta + \alpha}{2} = m\pi$. Why: The given passage directly states the general form involving the sum of $\theta$ and $\alpha$ divided by 2 equal to $m\pi$.

**Q4. [Anti-derivatives; 1 mark; computed]** Evaluate $\displaystyle\int_{0}^{1}\left(6x^{2} + 2x\right)dx$.

- (a) $4$
- (b) $8$
- (c) $3$
- (d) $1$

Key: (c) $3$. Why: By the power rule of integration $\displaystyle\int x^{n}dx = \dfrac{x^{n+1}}{n+1}$. $\displaystyle\int_0^{1}(6x^{2}+2x)dx = \left[\dfrac{6x^{3}}{3} + \dfrac{2x^{2}}{2}\right]_0^{1}$ $= 3$

**Q5. [Vectors; 3 marks; teacher]** Define coplanar vectors using the formula $\vec{c} = x\vec{a}+y\vec{b}$ and explain their relationship to spanning planes.

Marking scheme:

- Coplanar vectors satisfy $\vec{c} = x\vec{a}+y\vec{b}$, indicating $\vec{c}$ lies within the plane defined by $\vec{a}$ and $\vec{b}$.  **[2]**
- Two non-collinear vectors span a plane, meaning any vector in this plane can be expressed as a linear combination of these two vectors.  **[1]**

**Q6. [Inverse Circular Functions; 5 marks; teacher]** Explain the value of $\sin^{-1}\left(\sin\dfrac{2\pi}{3}\right)$ and discuss why the result is $\dfrac{\pi}{3}$ instead of $\dfrac{2\pi}{3}$. Also, describe how the graph of $\sin^{-1}x$ relates to the graph of $\sin x$.

Marking scheme:

- The value of $\sin^{-1}\left(\sin\dfrac{2\pi}{3}\right)$ equals $\dfrac{\pi}{3}$ because $\sin^{-1}x$ returns an angle in the range $[-\dfrac{\pi}{2}, \dfrac{\pi}{2}]$.  **[2]**
- Since $\sin\dfrac{2\pi}{3}=\dfrac{\sqrt{3}}{2}$, $\sin^{-1}\dfrac{\sqrt{3}}{2}=\dfrac{\pi}{3}$ as it lies within this range.  **[2]**
- The graph of $\sin^{-1}x$ is the reflection of the $\sin x$ graph over the line $y=x$, due to the inverse relationship where input and output values interchange roles.  **[1]**

## Mathematics - Class 12 (NEB)  (`math12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 1.9087)

**Q1. [Complex Numbers; 1 mark; teacher]** What term describes the $n$ values $1, w, \ldots, w^{n-1}$ where $w = \cos\dfrac{2\pi}{n} + i\sin\dfrac{2\pi}{n}$?

- (a) Euler's formula
- (b) Polar coordinates
- (c) $n^{\text{th}}$ roots of unity
- (d) Complex conjugates

Key: (c) $n^{\text{th}}$ roots of unity. Why: The passage defines these specific values as the $n^{\text{th}}$ roots of unity.

**Q2. [Anti-derivatives; 1 mark; teacher]** What is the area $A$ under the curve $x = y^2$ from $y=0$ to $y=2$ when integrating with respect to $y$?

- (a) $\frac{4}{3}$
- (b) $\frac{16}{3}$
- (c) $\frac{8}{3}$
- (d) $\frac{2}{3}$

Key: (c) $\frac{8}{3}$. Why: The integral $\int_0^2 y^2\,dy$ evaluates to $\frac{8}{3}$.

**Q3. [Conic Sections; 1 mark; teacher]** A circle has the equation $x^{2}+y^{2}-8x+6y-11 = 0$. What is the center of this circle?

- (a) (8,6)
- (b) (3,-4)
- (c) (4,-3)
- (d) (4,3)

Key: (c) (4,-3). Why: The center of the circle is found by completing the square for the given equation, resulting in the center at (4,-3).

**Q4. [Product of Vectors; 1 mark; computed]** Find the scalar product of $\vec{a} = 2\hat{i} + 4\hat{j} + 2\hat{k}$ and $\vec{b} = 4\hat{i} + 4\hat{j} + 2\hat{k}$.

- (a) $24$
- (b) $18$
- (c) $28$
- (d) $20$

Key: (c) $28$. Why: The scalar product is $\vec{a}\cdot\vec{b} = a_1b_1 + a_2b_2 + a_3b_3$. $\vec{a}\cdot\vec{b} = a_1b_1+a_2b_2+a_3b_3 = 2\times4+4\times4+2\times2$ $\vec{a}\cdot\vec{b} = 28$

**Q5. [Product of Vectors; 2 marks; teacher]** Given a circle with center $O$ and radius $r$, where $O$ is the origin and $\vec{OB} = \vec{r}$, if $AB$ is a diameter, prove that $\angle ACB$ is a right angle for any point $C$ on the circle.

Marking scheme:

- Since $AB$ is the diameter, $\angle ACB$ subtends the semicircle. 2.  **[1]**
- By the inscribed angle theorem, any angle subtending a semicircle is a right angle, thus $\angle ACB = 90^\circ$.  **[1]**

**Q6. [Conic Sections; 5 marks; gold]** a) Find the foci and the centre of the hyperbola $9x^{2}-16y^{2}-144=0$. [2] b) A parabolic reflector is $20$ cm in diameter and $5$ cm deep. Find the position of its focus. [3] (NEB 2080 Q21a; NEB 2081 Q4)

Marking scheme:

- (a) Divide by $144$: $\dfrac{x^{2}}{16}-\dfrac{y^{2}}{9}=1$.  **[2]**
- So $a=4$, $b=3$, $c=\sqrt{16+9}=5$, and the centre is the origin.  **[1]**
- Foci: $(\pm5,\,0)$.(b) Place the vertex at the origin and the axis along the $y$-axis: $x^{2}=4ay$.  **[1]**
- The rim of the reflector is $10$ cm from the axis and $5$ cm from the vertex, so $(10,5)$ lies on the parabola:  **[1]**

## Computer Science - Class 11 (NEB)  (`cs11`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.5669)

**Q1. [Computer System; 1 mark; teacher]** How quickly can a computer system process the grading of marks for a large number of students compared to manual methods?

- (a) In weeks
- (b) In days
- (c) In minutes
- (d) In hours

Key: (c) In minutes. Why: Computers can sort and grade marks of lakhs of students in minutes, whereas manual methods took many days.

**Q2. [Multimedia; 1 mark; teacher]** Why does silence in an audio waveform appear as a thin line?

- (a) Because the horizontal axis represents time, and silence lasts for a short duration.
- (b) Because silence creates a uniform noise pattern that is depicted as a thin line.
- (c) Because the vertical axis represents the loudness of the sample, and silence has minimal loudness.
- (d) Because the waveform compresses silent intervals into thinner lines to save space.

Key: (c) Because the vertical axis represents the loudness of the sample, and silence has minimal loudness. Why: The vertical axis is the loudness of the sample, and silence corresponds to minimal loudness, showing as a thin line.

**Q3. [Computer Software and Operating System; 1 mark; teacher]** Which of the following statements correctly describes the primary purpose of application software?

- (a) It is a sub-class of system software.
- (b) It runs the machine efficiently.
- (c) It is written to solve a user's problem.
- (d) It is what a user notices most.

Key: (c) It is written to solve a user's problem. Why: Application software is written to solve a user's problem.

**Q4. [Programming Concepts and Logics; 1 mark; computed]** Convert the binary number $10100_{2}$ to decimal.

- (a) $5$
- (b) $40$
- (c) $20$
- (d) $2$

Key: (c) $20$. Why: A binary number $b_4b_3b_2b_1b_0$ has the decimal value $16b_4+8b_3+4b_2+2b_1+b_0$ (place values are powers of two). $1\times16+0\times8+1\times4+0\times2+0\times1$ $= 20$

**Q5. [Programming Concepts and Logics; 2 marks; teacher]** Calculate the difference between the ASCII values of 'K' and 'V'. What is the result?

Marking scheme:

- The ASCII value of 'K' is 75 and 'V' is 86.  **[1]**
- The difference is $75 - 86 = -11$.  **[1]**

**Q6. [Number System and Boolean Logic; 5 marks; teacher]** Explain how subtraction can be performed using an adder in a CPU and describe the operation of NAND and NOR gates, mentioning their universality. Include how to convert from octal to hexadecimal via binary.

Marking scheme:

- Subtraction in a CPU uses an adder by converting the subtrahend to its two's complement.  **[1]**
- For example, subtracting 0110 (6) from 1101 (13) involves adding the two's complement of 0110, which is 1010, to 1101, yielding 0111 (7), discarding the carry-out.  **[1]**
- NAND performs AND then NOT, while NOR does OR followed by NOT.  **[1]**
- Both are universal gates as they can replicate any logic function.  **[1]**
- To convert octal to hexadecimal, first change each octal digit to a 3-bit binary form, regroup into sets of four bits, and then convert each group to its hexadecimal equivalent.  **[1]**

## Computer Science - Class 12 (NEB)  (`cs12`, 10,203,840 params, INT8 ONNX 10.73 MB, held-out loss 3.8339)

**Q1. [Database Management System; 1 mark; teacher]** Why is it important to store and transmit data as ciphertext in a database management system?

- (a) To allow for easier transmission of data over long distances without loss.
- (b) To increase the storage capacity of the database by compressing the data.
- (c) To ensure that if data is stolen or intercepted, it remains unusable to unauthorized parties.
- (d) To speed up the backup and recovery process by encrypting data.

Key: (c) To ensure that if data is stolen or intercepted, it remains unusable to unauthorized parties. Why: Encryption ensures stolen disks or sniffed packets are useless, which aligns with the answer provided.

**Q2. [Recent Trends in Technology; 1 mark; teacher]** Which technology involves entering a computer-generated, three-dimensional environment where users can interact using a head-mounted display and sensors?

- (a) Augmented reality
- (b) Holography
- (c) Virtual reality
- (d) 3D Projection

Key: (c) Virtual reality. Why: The passage defines Virtual reality as a computer-generated, three-dimensional environment that the user can enter and interact with using a head-mounted display and sensors.

**Q3. [Web Technology II; 1 mark; teacher]** What type of programming language is used to connect to a MySQL database and retrieve records as described?

- (a) Java
- (b) JavaScript
- (c) PHP
- (d) Python

Key: (c) PHP. Why: The passage explicitly mentions using a PHP program to connect to the MySQL database.

**Q4. [Data Communication and Networking; 1 mark; computed]** What is the minimum number of bits needed to represent $500$ different values?

- (a) $8\ \text{bits}$
- (b) $63\ \text{bits}$
- (c) $9\ \text{bits}$
- (d) $500\ \text{bits}$

Key: (c) $9\ \text{bits}$. Why: $k$ bits can represent $2^k$ values, so $k = \lceil\log_2 n\rceil$. $k = \lceil\log_2 500\rceil$ $k = 9\ \text{bits}$

**Q5. [Object-Oriented Programming; 3 marks; teacher]** Explain how the concepts of inheritance and polymorphism are demonstrated in the given examples from the textbook.

Marking scheme:

- Inheritance: Student class inherits name and show() from Person, adding roll.  **[2]**
- Polymorphism: Area class uses function overloading with find() for circles and rectangles based on parameter count.  **[1]**

**Q6. [Data Communication and Networking; 5 marks; teacher]** Explain the concept of subnetting within a class C IP address block using a block size of 64. Additionally, define IP address, subnet mask, gateway, and MAC address.

Marking scheme:

- Subnetting a class C block with a size of 64 yields subnets starting at 0, 64, 128, and 192 ($4 \times 64 = 256$).  **[1]**
- An IP address uniquely identifies devices on a network.  **[1]**
- A subnet mask divides an IP address into network and host parts.  **[1]**
- A gateway routes traffic between networks.  **[1]**
- A MAC address is a unique identifier for a network interface.  **[1]**
