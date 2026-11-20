# Supplementary Material

Supplementary Material for *Estimating spreading-activation breadth and verification ability from remote associates responses: A generation–verification model*. The formatted version is [Supplementary_Material.docx](Supplementary_Material.docx); this page shows the same content (Section S1 and Tables S1–S6) for reading in the browser. Equations appear here as plain text.


## Section S1. Proofs of three properties of spreadr grid matching

**Setting.** The network has *n* nodes, and **P** is the transition matrix obtained by normalizing rows by weighted degree. One spreadr update is

**a**(*t* + 1) = *T*_ε[(1 − *d*) **M**_*r* **a**(*t*)], with **M**_*r* = *r***I** + (1 − *r*)**P**ᵀ,

where *T*_ε sets components below ε to zero and leaves the others unchanged. The initial state is **a**(0) = *A*·**e**_C, where **e**_C is 1 at the cue nodes and 0 elsewhere. An item is classified as solved if and only if there is a *t* ∈ {0, …, 100} at which the solution node *k* has *a*_k(*t*) > 0.

**Property 1 (scale invariance).** For any *c* > 0, *T*_{*c*ε}(*c***x**) = *c*·*T*_ε(**x**). Because **M**_*r* is linear, induction shows that the trajectory from (*A*, ε) equals the trajectory from (*cA*, *c*ε) divided by *c*. The two have the same zero and nonzero entries at every step, so success classifications depend only on ε/*A*.

**Property 2 (decay is a rising threshold).** Let **b**(*t*) = **a**(*t*)/[*A*(1 − *d*)^*t*]. By Property 1,

**b**(*t* + 1) = *T*_{ε_t}(**M**_*r* **b**(*t*)), ε_t = (ε/*A*)/(1 − *d*)^(*t*+1), **b**(0) = **e**_C.

*a*_k(*t*) > 0 if and only if *b*_k(*t*) > 0. Hence *d* acts only through the threshold sequence ε_t: the larger *d*, the faster the threshold rises with the number of steps and the earlier activation is cut off. With ε = 0, *T*_ε is the identity, **b**(*t*) = **M**_*r*^*t* **e**_C does not depend on *d*, and *d* has no effect on any success classification.

**Property 3 (retention trades off with steps).** Because **I** and **P**ᵀ commute,

**M**_*r*^*t* = Σ_{*k*=0}^{*t*} C(*t*, *k*)(1 − *r*)^*k* *r*^(*t*−*k*) (**P**ᵀ)^*k*.

(**P**ᵀ)^*k* **e**_C is the distribution of a *k*-step random walk from the cues, so *t* steps of spreading with retention *r* are a mixture of walk distributions with number of steps *K* ~ Binomial(*t*, 1 − *r*). Ignoring the zeroing step, *r* and *t* affect activation only through the distribution of *K*. With ε = 0, 0 ≤ *r* < 1, and *d* < 1, the solution node *k* is activated at some step *t* ≤ 100 if and only if the network contains a path of length at most 100 from some cue to *k*; this condition depends on neither *r* nor *d*.

**Corollary.** With ε = 0, all pairs with *r* < 1 and *d* < 1 give the same success pattern, which agrees with the result on the networks of Chen et al. after removing the threshold (all 76 solutions activated under all 400 non-degenerate pairs). With ε > 0, all differences between pairs arise through the threshold sequence ε_t, whose scale is fixed by the arbitrary ratio ε/*A*; raising *A* from 30 to 300 is equivalent to lowering ε from .001 to .0001, which explains the 13% to 22% of flipped classifications.

**Relation to the generation–verification model.** Property 3 shows that what linear spreading provides at the individual level is the distribution of walk lengths. The generation–verification model parameterizes this distribution with a geometric distribution *K* ~ Geometric(1 − θ), *a*_c(θ) = Σ_k Pr(*K* = *k*)(**P**ᵀ)^*k* **e**_c, describing how far activation travels with a single parameter θ (spreading breadth) and without scale constants such as a threshold or initial value. On connected, non-bipartite networks, (**P**ᵀ)^*k* **e**_c converges to the stationary distribution π as *k* grows (with symmetric edge weights, π is proportional to weighted degree), so activation becomes independent of the cue as θ approaches 1 and breadth becomes less identifiable at the high end.

**Table S1. Simulation 3 (careless responders): bias (90% coverage) of the population parameters**

| Condition | μ | σ | γ | κ | δ | τ | ρ |
|---|---|---|---|---|---|---|---|
| No careless responders (key cell) | −0.03 (.91) | −0.01 (.88) | 0.00 (.91) | 0.00 (.91) | 0.00 (.90) | 0.00 (.88) | −0.03 (.90) |
| Random 5% | −0.62 (.70) | 0.44 (.64) | −0.02 (.44) | 0.12 (.83) | −0.14 (.69) | 0.30 (.07) | −0.39 (.20) |
| Random 10% | −1.16 (.40) | 0.97 (.14) | −0.04 (.04) | 0.16 (.78) | −0.34 (.13) | 0.55 (.00) | −0.59 (.03) |
| Give-up 5% | −0.04 (.89) | 0.76 (.24) | 0.00 (.86) | −0.04 (.93) | −0.05 (.86) | 0.13 (.55) | 0.29 (.36) |
| Give-up 10% | −0.30 (.78) | 1.33 (.01) | 0.01 (.75) | −0.04 (.85) | −0.12 (.69) | 0.25 (.23) | 0.42 (.07) |

*Note.* Each condition has 200 data sets with *N* = 100, *J* = 24, σ = 2.5; the first row is the key cell of Simulation 1 (1,000 data sets). Random responders choose uniformly among no answer and all candidates on each item; give-up responders give no answer with probability .9 on each item and otherwise respond according to the model. True population parameters are those of the careful responders. Bias = posterior mean − true value.

**Table S2. Simulation 3: person parameters of careful and careless responders**

| Condition | Group | Persons | True *b* | Est. *b* | Bias *b* | Cov. *b* | True *v* | Est. *v* | Bias *v* | Cov. *v* | *r*(*b*) | *r*(*v*) | Pct. *b* | Detected |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Random 5% | Careful | 19,000 | −0.47 | −1.37 | −0.89 | .86 | 3.97 | 3.95 | −0.02 | .91 | .80 | .74 | — | — |
| Random 5% | Careless | 1,000 | −0.52 | 3.25 | 3.76 | .33 | 3.95 | 1.64 | −2.31 | .02 | — | — | .96 | .72 |
| Random 10% | Careful | 18,000 | −0.56 | −2.36 | −1.80 | .71 | 3.95 | 3.90 | −0.05 | .90 | .81 | .75 | — | — |
| Random 10% | Careless | 2,000 | −0.55 | 3.63 | 4.18 | .34 | 3.96 | 1.13 | −2.83 | .01 | — | — | .95 | .89 |
| Give-up 5% | Careful | 19,000 | −0.44 | −0.09 | 0.35 | .91 | 3.95 | 3.97 | 0.02 | .91 | .81 | .75 | — | — |
| Give-up 5% | Careless | 1,000 | −0.45 | −8.46 | −8.01 | .01 | 3.98 | 2.55 | −1.43 | .21 | — | — | .03 | .94 |
| Give-up 10% | Careful | 18,000 | −0.53 | 0.01 | 0.54 | .90 | 3.96 | 4.00 | 0.04 | .92 | .79 | .77 | — | — |
| Give-up 10% | Careless | 2,000 | −0.61 | −8.91 | −8.30 | .01 | 3.95 | 2.30 | −1.65 | .13 | — | — | .06 | .97 |

*Note.* True values of careless responders are drawn from the same population but do not generate their responses, so their bias and coverage show where the estimates are pushed. *r*(*b*) and *r*(*v*) are computed for careful responders only (median within-data-set correlation). Pct. *b*: mean percentile of careless responders' posterior breadth among all participants of the data set. Detected: with *k* careless responders in a data set, the share of careless responders among the *k* participants with the highest (random) or lowest (give-up) posterior breadth.

**Table S3. Simulation 3: grid matching with careless responders**

| Condition | *r*(*r̂*, *b*) | *r*(*d̂*, *b*) | *r*(*r̂*, acc.) | *r*(*d̂*, acc.) | G–V model *r*(*b*) | Stability | Distinct estimates |
|---|---|---|---|---|---|---|---|
| Random 5% | −.13 | −.09 | .06 | −.62 | .80 | .91 | 5 |
| Random 10% | −.13 | −.10 | .10 | −.62 | .81 | .91 | 5 |
| Give-up 5% | −.14 | −.08 | .10 | −.61 | .81 | .91 | 5 |
| Give-up 10% | −.12 | −.09 | .08 | −.63 | .79 | .92 | 5 |

*Note.* Careful responders only; median within-data-set correlations. *r̂*, *d̂*: grid-matching estimates; acc.: accuracy; G–V: generation–verification model.

**Table S4. Simulation 1, all 18 cells: bias (90% coverage) of the population parameters**

| *N* | *J* | σ | μ | σ | γ | κ | δ | τ | ρ |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 12 | 1.5 | 0.01 (.93) | −0.17 (.88) | 0.00 (.94) | −0.01 (.94) | 0.03 (.91) | −0.01 (.90) | −0.11 (.97) |
| 50 | 12 | 2.5 | −0.05 (.94) | −0.19 (.88) | 0.00 (.90) | −0.07 (.91) | −0.01 (.89) | −0.03 (.93) | −0.11 (.94) |
| 50 | 12 | 3.5 | 0.01 (.94) | −0.30 (.89) | 0.01 (.91) | −0.14 (.90) | −0.03 (.87) | −0.02 (.93) | −0.04 (.93) |
| 50 | 24 | 1.5 | −0.05 (.91) | −0.07 (.88) | 0.00 (.91) | −0.02 (.89) | 0.02 (.90) | −0.01 (.90) | −0.08 (.93) |
| 50 | 24 | 2.5 | −0.08 (.94) | −0.08 (.89) | 0.00 (.93) | −0.02 (.92) | −0.01 (.90) | 0.00 (.94) | −0.05 (.92) |
| 50 | 24 | 3.5 | 0.01 (.89) | −0.19 (.94) | 0.00 (.92) | −0.06 (.93) | −0.02 (.91) | 0.00 (.89) | −0.03 (.93) |
| 100 | 12 | 1.5 | −0.13 (.92) | −0.15 (.90) | 0.00 (.94) | 0.01 (.89) | 0.00 (.93) | −0.01 (.93) | −0.04 (.97) |
| 100 | 12 | 2.5 | −0.09 (.92) | −0.01 (.91) | 0.00 (.94) | −0.02 (.94) | −0.01 (.93) | −0.01 (.90) | −0.03 (.92) |
| 100 | 12 | 3.5 | −0.02 (.92) | −0.15 (.89) | 0.00 (.95) | −0.10 (.90) | −0.02 (.89) | −0.02 (.89) | −0.03 (.93) |
| 100 | 24 | 1.5 | −0.10 (.90) | −0.03 (.88) | 0.00 (.90) | 0.01 (.91) | 0.00 (.93) | 0.01 (.91) | −0.04 (.91) |
| 100 | 24 | 2.5 | −0.03 (.91) | −0.01 (.88) | 0.00 (.91) | 0.00 (.91) | 0.00 (.90) | 0.00 (.88) | −0.03 (.90) |
| 100 | 24 | 3.5 | −0.01 (.88) | −0.17 (.88) | 0.00 (.89) | −0.03 (.92) | −0.01 (.91) | 0.00 (.92) | −0.03 (.94) |
| 200 | 12 | 1.5 | −0.07 (.89) | −0.10 (.86) | 0.00 (.89) | 0.00 (.90) | 0.00 (.89) | −0.01 (.88) | −0.06 (.93) |
| 200 | 12 | 2.5 | −0.08 (.93) | 0.00 (.94) | 0.00 (.94) | −0.04 (.92) | −0.01 (.90) | −0.01 (.90) | −0.02 (.88) |
| 200 | 12 | 3.5 | −0.01 (.92) | −0.10 (.90) | 0.00 (.89) | −0.04 (.90) | −0.01 (.91) | 0.00 (.91) | −0.01 (.91) |
| 200 | 24 | 1.5 | −0.06 (.89) | 0.00 (.88) | 0.00 (.88) | −0.01 (.90) | 0.00 (.91) | 0.00 (.90) | −0.02 (.90) |
| 200 | 24 | 2.5 | −0.01 (.92) | 0.01 (.88) | 0.00 (.89) | −0.01 (.89) | 0.00 (.89) | 0.00 (.90) | 0.00 (.93) |
| 200 | 24 | 3.5 | −0.07 (.85) | −0.12 (.85) | 0.00 (.89) | 0.01 (.90) | 0.00 (.87) | 0.00 (.86) | −0.04 (.90) |

*Note.* 200 data sets per cell (1,000 in the key cell, *N* = 100, *J* = 24, σ = 2.5). Bias = posterior mean − true value. RMSE and interval widths are in `S3a_population_long.csv` of the analysis repository.

**Table S5. Simulation 1, all 18 cells: recovery of person parameters**

| *N* | *J* | σ | *r*(*b*) | *r*(*v*) | Cov. *b* | Cov. *v* | Error *r* | *b* < −4 | −4 ≤ *b* < −1 | −1 ≤ *b* < 2 | *b* ≥ 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 12 | 1.5 | .55 | .65 | .87 | .87 | .22 | .70 | .85 | .93 | .52 |
| 50 | 12 | 2.5 | .72 | .62 | .88 | .86 | .24 | .78 | .89 | .96 | .70 |
| 50 | 12 | 3.5 | .81 | .62 | .87 | .87 | .24 | .81 | .89 | .97 | .78 |
| 50 | 24 | 1.5 | .69 | .77 | .87 | .88 | .22 | .81 | .86 | .92 | .48 |
| 50 | 24 | 2.5 | .81 | .76 | .89 | .88 | .28 | .85 | .88 | .95 | .75 |
| 50 | 24 | 3.5 | .88 | .74 | .88 | .88 | .22 | .84 | .87 | .95 | .84 |
| 100 | 12 | 1.5 | .56 | .68 | .86 | .89 | .22 | .66 | .88 | .91 | .44 |
| 100 | 12 | 2.5 | .73 | .65 | .89 | .87 | .22 | .82 | .90 | .97 | .72 |
| 100 | 12 | 3.5 | .82 | .62 | .89 | .86 | .18 | .85 | .90 | .97 | .81 |
| 100 | 24 | 1.5 | .68 | .77 | .89 | .90 | .27 | .74 | .88 | .93 | .56 |
| 100 | 24 | 2.5 | .82 | .76 | .90 | .88 | .26 | .85 | .89 | .96 | .77 |
| 100 | 24 | 3.5 | .87 | .73 | .89 | .88 | .26 | .85 | .88 | .95 | .82 |
| 200 | 12 | 1.5 | .55 | .65 | .87 | .88 | .21 | .60 | .86 | .93 | .42 |
| 200 | 12 | 2.5 | .72 | .63 | .90 | .88 | .22 | .82 | .91 | .97 | .72 |
| 200 | 12 | 3.5 | .81 | .65 | .89 | .88 | .21 | .82 | .89 | .97 | .82 |
| 200 | 24 | 1.5 | .69 | .77 | .89 | .89 | .25 | .72 | .88 | .94 | .54 |
| 200 | 24 | 2.5 | .81 | .77 | .90 | .89 | .28 | .83 | .89 | .96 | .79 |
| 200 | 24 | 3.5 | .87 | .75 | .89 | .89 | .26 | .86 | .89 | .95 | .84 |

*Note.* *r*(*b*), *r*(*v*): median within-data-set correlation between true values and posterior means. Error *r*: correlation of the estimation errors of *b* and *v*. The last four columns give the 90% coverage of *b* by true-breadth zone.

**Table S6. Simulation 1, all 18 cells: grid-matching estimates and convergence of the generation–verification model**

| *N* | *J* | σ | *r*(*r̂*, *b*) | *r*(*d̂*, *b*) | *r*(*r̂*, acc.) | *r*(*d̂*, acc.) | Stability | Distinct estimates | Data sets | Converged | Refitted | Time (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 12 | 1.5 | −.06 | −.05 | −.04 | −.62 | .92 | 4 | 200 | 1.00 | .06 | 1.5 |
| 50 | 12 | 2.5 | −.07 | −.01 | .02 | −.63 | .93 | 4 | 200 | 1.00 | .03 | 1.2 |
| 50 | 12 | 3.5 | −.04 | −.07 | .13 | −.63 | .92 | 4 | 200 | 1.00 | .01 | 1.1 |
| 50 | 24 | 1.5 | −.08 | −.05 | −.01 | −.60 | .92 | 5 | 200 | 1.00 | .04 | 2.6 |
| 50 | 24 | 2.5 | −.12 | −.05 | .08 | −.62 | .91 | 5 | 200 | 1.00 | .02 | 2.4 |
| 50 | 24 | 3.5 | −.08 | −.14 | .19 | −.63 | .92 | 5 | 200 | 1.00 | .02 | 2.4 |
| 100 | 12 | 1.5 | −.06 | −.01 | −.04 | −.64 | .93 | 4 | 200 | 1.00 | .06 | 2.5 |
| 100 | 12 | 2.5 | −.07 | −.06 | .07 | −.63 | .92 | 4 | 200 | 1.00 | .01 | 1.9 |
| 100 | 12 | 3.5 | −.03 | −.10 | .13 | −.65 | .93 | 4 | 200 | 1.00 | .03 | 1.8 |
| 100 | 24 | 1.5 | −.11 | −.06 | −.03 | −.60 | .91 | 5 | 200 | 1.00 | .01 | 3.4 |
| 100 | 24 | 2.5 | −.13 | −.08 | .10 | −.61 | .92 | 5 | 1,000 | 1.00 | .01 | 2.5 |
| 100 | 24 | 3.5 | −.09 | −.10 | .22 | −.62 | .92 | 5 | 200 | 1.00 | .03 | 2.8 |
| 200 | 12 | 1.5 | −.05 | −.01 | −.04 | −.61 | .93 | 4 | 200 | 1.00 | .04 | 3.5 |
| 200 | 12 | 2.5 | −.05 | −.04 | .05 | −.62 | .92 | 4 | 200 | 1.00 | .04 | 3.7 |
| 200 | 12 | 3.5 | −.01 | −.07 | .12 | −.66 | .93 | 4 | 200 | 1.00 | .02 | 2.8 |
| 200 | 24 | 1.5 | −.12 | −.06 | .01 | −.61 | .91 | 5 | 200 | 1.00 | .00 | 5.7 |
| 200 | 24 | 2.5 | −.13 | −.07 | .09 | −.61 | .92 | 5 | 200 | 1.00 | .01 | 4.7 |
| 200 | 24 | 3.5 | −.11 | −.11 | .20 | −.63 | .92 | 5 | 200 | 1.00 | .00 | 3.9 |

*Note.* *r̂*, *d̂*: grid-matching estimates on the same data. Stability: grid-matching stability index (median over data sets). Distinct estimates: median number of distinct (*r̂*, *d̂*) pairs in a data set. Converged: share of data sets with R̂ ≤ 1.01, bulk and tail ESS ≥ 400, and no divergent transitions after the refit rule. Time: median fitting time per data set.

