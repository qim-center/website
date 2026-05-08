+++
title = "Local Thickness"
description = "Fast local thickness in 2D and 3D — a pip-installable algorithm described in our CVPR 2023 workshop paper."
authors = ["Vedrana Andersen Dahl", "Anders Bjorholm Dahl"]
tags = ["Analysis", "Morphometry"]
image = "images/tools/local-thickness.png"
source_url = "https://github.com/vedranaa/local-thickness"
+++


Local thickness is a fundamental morphological measure defined as the radius of the largest circle (in 2D) or sphere (in 3D) that fits inside an object at any given point. Our fast algorithm computes local thickness in a fraction of the time compared to conventional approaches.

The method was presented at the 8th IEEE Workshop on Computer Vision for Microscopy Image Analysis (CVMI), held in conjunction with CVPR 2023.

{{< fig src="/images/tools/local-thickness/initial_example.png" caption="Local thickness computed on a 3D volume. The colour map indicates the thickness value at every point in the structure." >}}

## Algorithm

The conventional local thickness algorithm dilates the distance field of an object with increasingly larger spherical structuring elements — an accurate but computationally expensive process. Our fast algorithm instead uses **n consecutive dilations with a sphere of radius 1**, replacing one dilation with a sphere of radius n. This seemingly simple substitution yields mathematically equivalent results while being substantially faster.

In every iteration, small structuring elements operate on subsets (super-levels) of the distance field, and only values larger than the current iteration counter are updated. This means a distance value `d(x) = 5` propagates freely for 5 iterations, correctly filling in the sphere of radius 5.


## Instalation

Install the module using `pip install localthickness` or clone the repository.

Basic usage:

```Python
import localthickness as lt

#  Make a binary test volume. 
B = lt.create_test_volume((100, 500, 400), sigma=15, boundary=0.001)

# Compute thickness and separation.
thickness = lt.local_thickness(B, scale=0.5)
separation = lt.local_thickness(~B, scale=0.5)

# Visualize.
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(10, 5))
ax[0].imshow(B[10])
ax[1].imshow(thickness[10], cmap=lt.black_plasma())
ax[2].imshow(separation[10], cmap=lt.white_viridis())
```
{{< fig src="/images/tools/local-thickness/mwe_figure.png" caption="Output of the minimal working example — binary volume (left), thickness map (centre), separation map (right)." >}}


## Citation

If you use this tool in your work, please cite:

```bibtex
@inproceedings{dahl2023fast,
  title={Fast Local Thickness},
  author={Dahl, Vedrana Andersen and Dahl, Anders Bjorholm},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops},
  pages={4335--4343},
  year={2023}
}
```

## Applications

Local thickness is widely used in quantitative analysis of porous materials, biomedical imaging, and materials science — wherever the structural dimensions of a 3D object need to be measured at every point. The measure has also been used as a building block for computing sphericity and roundness of objects in large volumes.
