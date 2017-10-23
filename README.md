# formulaChar
### CNF formula characterizer
An automate infrastructure for producing SAT solvers experiments and record their data

### Research work
The results can be found in our paper:

> D.​Cohen​ and​ O.​Strichman,​ The ​impact of Entropy ​and ​Solution Density ​on ​selected ​SAT heuristics, ArXiv​ e-prints​ (2017)

Which is a follow up on this work:
> Chanseok Oh, Between SAT and UNSAT: The Fundamental Difference in CDCL SAT, SAT 2015: 307-323

##### Presentation
A talk summarizing our work can be found at https://ie.technion.ac.il/~ofers/presentations/entropy.pdf

### Run experiments (Scripts details)
The scripts are independent and can be run alone, detailed help can be shown with `-h` while running each of them.

exp1-exp5 are equivalent to Oh's original experiments shown in his paper:

+ `exp1` - DB-reduction
+ `exp2` - LBD-cut
+ `exp3` - Clause-size vs. LBD
+ `exp4` - Glucose vs. Luby restarts
+ `exp5` - Variable decay factor

run examples can be found in `exp1` directory's README

+ `entropy` - Computing formula entropy / solution density - with `main.py` 
+ `backbone` - Compute backbone out of formula solutions
+ `backboneSampler` - Modified MiniSat to sample estimated formula backbone
+ `modularityGen` - Tool for generating random formulas with modularity controlled parameters
+ `merge` - Merge all tables to one `.csv` file

+ `gui.py` - GUI for running the experiments remotely

### Analyze data

Scripts written in R to analyze the experiments data, can be found at:
http://ie.technion.ac.il/~ofers/entropy/supp.zip

There's a README file for re-producing the statistics tests, the data can be found on the files `exp#-results.csv`. Each statistical test has a different directory (3 tests total), results can be found in our paper.

### Heuristic based SAT-solver

Attempts to improve COMiniSatPS based on our results can be found at:
https://github.com/dorcoh/COMiniSatPS-BackboneModified


### CNF Formula entropy approximator

Tool implemented to aid this research work, for approximating a CNF formula entropy property by using <i>Hashing and optimization</i> technique (shrink search space and find most likely sample with an optimization oracle). More details in it's repository:
https://github.com/dorcoh/hashing-optimization

