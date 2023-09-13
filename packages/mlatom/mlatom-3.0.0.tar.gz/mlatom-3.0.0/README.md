# Brief Introduction
A Package for Atomistic Simulations with Machine Learning

**manual**: http://mlatom.com/manual/  
**tutorial**: http://mlatom.com/tutorial/ 


#  Tasks Performed by MLatom
A brief overview of MLatom capabilities (see above links for more up-to-date version). See sections below for more details.

## Tasks
- Estimating accuracy of ML models.
- Creating ML model and saving it to a file.
- Loading existing ML model from a file and performing ML calculations with this model.
- ML-accelerated calculation of absorption spectra within nuclear ensemble approach
- Learning curves
- ML-two photon absorption

## Data Set Operations
- Converting XYZ coordinates into an input vector (molecular descriptor) for ML.
- Sampling subsets from a data set.


# Sampling
- none: simply splitting the data set into the training, test, and, if necessary, training set into the subtraining and validation sets (in this order) without changing the order of indices.
- random sampling.
- user-defined: requests MLatom to read indices for the training, test, and, if necessary, for the subtraining and validation sets from files.
- [ structure-based sampling ](http://mlatom.com/self-correcting-machine-learning-and-structure-based-sampling/)
  - from unsliced and sliced data
- [ farthest-point traversal iterative procedure ](https://en.wikipedia.org/wiki/Farthest-first_traversal), which starts from two points farthest apart.


# ML Algorithm
[ Kernel ridge regression](https://web.stanford.edu/~hastie/ElemStatLearn/) with the following kernels:
- [ Gaussian ](https://doi.org/10.1103/PhysRevLett.108.058301).
- [ Laplacian ](https://doi.org/10.1103/PhysRevLett.108.058301).
- exponential.
- [ Matérn ](http://dx.doi.org/10.1198/jasa.2010.tm09420) ([ details of implementation ](http://dx.doi.org/10.1021/acs.jpclett.8b02469)).
Permutationally invariant kernel and self-correction are also supported.


# Hybrid QM/ML Approaches
[ Δ-machine learning ](http://dx.doi.org/10.1021/acs.jctc.5b00099).


# Molecular Descriptors
- [ Coulomb matrix ](https://doi.org/10.1103/PhysRevLett.108.058301)
  - [ sorted by norms of its rows ](http://dx.doi.org/10.1021/ct400195d);
  - unsorted;
  - permuted.
- [ Normalized inverse internuclear distances (RE descriptor)](http://mlatom.com/self-correcting-machine-learning-and-structure-based-sampling/)
  - sorted for user-defined atoms by the sum of their nuclear repulsions to all other atoms;
  - unsorted;
  - permuted.


# ML models
The [ KREG (Kernel-ridge-regression using RE descriptor and the Gaussian kernel function )](http://dx.doi.org/10.1021/acs.jpclett.8b02469) model is the default ML method.

## General-purpose ML models
- AIQM1 (requires interfaces to other programs as described in http://MLatom.com/AIQM1)
- Models available via interface to [TorchANI](https://doi.org/10.1021/acs.jcim.0c00451)
  - ANI-1x
  - ANI-1ccx
  - ANI-2x

# Model Validation
[ ML model can be validated (generalization error can be estimated) in several ways: ](https://web.stanford.edu/~hastie/ElemStatLearn/)

- on a hold-out test set not used for training. Both training and test sets can be sampled in one of the ways described above;
- by performing N-fold cross-validation. User can define the number of folds N. If N is equal to the number of data points, leave-one-out cross-validation is performed. Only random or no sampling can be used for cross-validation.
- by performing leave-one-out cross-validation (special case of N-fold cross-validation).
MLatom prints out mean absolute error (MAE), mean signed error (MSE), root-mean-squared error (RMSE), mean values of reference and estimated values, largest positive and negative outliers, correlation coefficient and its squared value R2 as well as coefficients of linear regression and corresponding standard deviations.


# Hyperparameter Tuning
Gaussian, Laplacian, and Matérn kernels have σ and λ tunable hyperparameters. MLatom can determine them by performing user-defined number of iterations of hyperparameter optimization on a logarithmic grid. User can adjust number of grid points, starting and finishing points on the grid. Hyperparameter are tuned to minimize either mean absolute error or root-mean-square error as defined by the user. [ Hyperparameters can be tuned to minimize ](https://web.stanford.edu/~hastie/ElemStatLearn/)

- the error of the ML model trained on the subtraining set in a hold-out validation set. Both subtraining and validation sets are parts of the training set, which can be used at the end with optimal parameters for training the final ML model. These sets ideally should not overlap and can be [ sampled ](http://mlatom.com/features/#Sampling) from the training set in one of the ways described above;
- N-fold cross-validation error. User can define the number of folds N. If N is equal to the number of data points, leave-one-out cross-validation is performed. Only random or no sampling can be used for cross-validation.

Note that hyperparameter tuning can be performed together with model validation. This means that for example one can perform outer loop of the cross-validation for model validation and tune hyperparameters via inner loop of the cross-validation.

Apart from natively implemented logarithmic grid search for hyperparameters, MLatom also provides the interface to the [ hyperopt package ](http://hyperopt.github.io/hyperopt/) implementing hyperparameter optimization using Bayesian methods with Tree-structured Parzen Estimator (TPE).


# First Derivatives
MLatom can be also used to estimate first derivatives from an ML model. Two scenarios are possible:

- partial derivatives are calculated for each dimension of given input vectors (analytical derivatives for Gaussian and Matern kernels);
- first derivatives are calculated in XYZ coordinates for input files containing molecular XYZ coordinates (analytical derivatives for the RE and Coulomb matrix descriptors).
- derivatives for interfaced models


# UV/vis spectra
MLatom can significantly accelerate the calculation of cross-section with the Nuclear Ensemble Approach (NEA).

In brief, this feature uses fewer QC calculation to achieve higher precision and reduce computational cost. You can find more detail on this paper (please cite it when using this feature):

> Bao-Xin Xue, Mario Barbatti, Pavlo O. Dral, [ Machine Learning for Absorption Cross Sections ](https://doi.org/10.1021/acs.jpca.0c05310), J. Phys. Chem. A 2020, 124, 7199–7210. DOI: 10.1021/acs.jpca.0c05310.

# Interfaces to 3<sup>rd</sup>-party software
MLatom also provides interfaces to some third-party software where extra ML model types are natively implemented. It allows users to access other popular ML model types within MLatom's workflow. Currently available third-party model types are:

- [ANI](https://doi.org/10.1039/c6sc05720a) (through [TorchANI](https://doi.org/10.1021/acs.jcim.0c00451)) 
- [DeepPot-SE](https://papers.nips.cc/paper/2018/hash/e2ad76f2326fbc6b56a45a56c59fafdb-Abstract.html) and [DPMD](https://doi.org/10.1103/PhysRevLett.120.143001) (through [DeePMD-kit](https://doi.org/10.1016/j.cpc.2018.03.016)) 
- [GAP](https://doi.org/10.1103/Physrevlett.104.136403)-[SOAP](https://doi.org/10.1103/physrevb.87.184115) (through [GAP](www.libatoms.org) suite and [QUIP](http://github.com/libAtoms/QUIP))  
- [PhysNet](https://doi.org/10.1021/acs.jctc.9b00181) (through [PhysNet](github.com/MMunibas/PhysNet)) 
- [sGDML](https://doi.org/10.1038/s41467-018-06169-2) (through [sGDML](www.sgdml.org)) 

# About Program
MLatom: a Package for Atomistic Simulations with Machine Learning    
Version 2.3.3
http://mlatom.com/                             
                                                                           
Copyright (c) 2013-2022 Pavlo O. Dral                   
http://dr-dral.com/                            
                                                                           
All rights reserved. This work is licensed under the [Attribution-NonCommercial-NoDerivatives 4.0 International](http://creativecommons.org/licenses/by-nc-nd/4.0/) license. See LICENSE.CC-BY-NC-ND-4.0.  
The above copyright notice and this permission notice shall be included  in all copies or substantial portions of the Software.           
The software is provided "as is", without warranty of any kind, express  or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.                                   
                                                                           
Cite as: 

1. Pavlo O. Dral, J. Comput. Chem. 2019, 40, 2339-2347             
2. Pavlo O. Dral, Fuchun Ge, Bao-Xin Xue, Yi-Fan Hou, Max Pinheiro Jr, Jianxing Huang, Mario Barbatti, Top. Curr. Chem. 2021, 379, 27              
3. Pavlo O. Dral, Peikun Zheng, Bao-Xin Xue, Fuchun Ge, Yi-Fan Hou, Max Pinheiro Jr, Yuming Su, Yiheng Dai, Yangtao Chen, MLatom: A Package for Atomistic Simulations with Machine Learning, version 2.3.3, Xiamen University, Xiamen, China, 2013-2022.               


# License

This work is licensed under the [Attribution-NonCommercial-NoDerivatives 4.0 International](http://creativecommons.org/licenses/by-nc-nd/4.0/) license. See LICENSE.CC-BY-NC-ND-4.0.

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a>
