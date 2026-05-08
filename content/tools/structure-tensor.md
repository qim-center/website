+++
title = "Structure Tensor"
description = "Analyses orientation in volumetric images using the gradient-based structure tensor method."
authors = ["Niels Jeppesen"]
tags = ["Analysis", "Orientation"]
image = "images/tools/structure-tensor.png"
source_url = "https://github.com/Skielex/structure-tensor"
+++

## Overview

The structure tensor is a 3×3 symmetric positive semi-definite matrix that summarizes orientation in a small neighbourhood around every point in a 3D volume. It captures how intensities change along different directions, making it a fundamental tool for analysing fibrous, layered, and other anisotropic structures in volumetric data.

This tool provides an efficient implementation for computing the structure tensor and extracting dominant orientations and shape measures from large 3D datasets.

## Algorithm

Given a 3D volume $V$, the squared intensity change along a direction $\mathbf{u}$ in a neighbourhood around a point $\mathbf{p}$ can be expressed as $\mathbf{u}^T S \, \mathbf{u}$, where $S$ is the structure tensor. Minimising this quadratic form with respect to $\mathbf{u}$ yields the predominant local orientation.

The structure tensor $S$ at a point $\mathbf{p}$ is computed from the gradient $\nabla V$ as:

$$S = \sum_{\mathcal{N}} \nabla V \, \nabla V^T$$

where the sum is taken over a local neighbourhood $\mathcal{N}$ around $\mathbf{p}$.

{{< fig src="/images/tools/structure-tensor/Figure1.png" caption="**Figure 1:** Minimisation problem in 2D. The paraboloid surface is defined by values of $D$ for any displacement $(x, y)$. In orange-red are the values of $D$ above the unit circle, and the dot indicates the minimum corresponding to the predominant orientation. In magenta-red are the values above the line $y = 1$, and the dot indicates the minimum corresponding to optical flow." >}}

Computation involves two Gaussian scale parameters:

- **Noise scale $\sigma$** — used for derivative computation. The volume is convolved with derivatives of a Gaussian to obtain $\nabla_\sigma V$, making the gradient estimation robust to noise.
- **Integration scale $\rho$** — the size of the neighbourhood over which orientation information is averaged, controlled by convolving the outer product with a Gaussian $K_\rho$.

### Eigendecomposition

Since $S$ is symmetric positive semi-definite, its eigendecomposition yields three real, non-negative eigenvalues $\lambda_1 \leq \lambda_2 \leq \lambda_3$ with corresponding orthogonal eigenvectors $\mathbf{v}_1, \mathbf{v}_2, \mathbf{v}_3$.

The eigenvector $\mathbf{v}_1$ associated with the smallest eigenvalue $\lambda_1$ indicates the **predominant local orientation** — the direction of minimal intensity variation. The eigenvectors $\mathbf{v}_2$ and $\mathbf{v}_3$ span the orthogonal plane.

### Shape Measures

From the eigenvalues, three normalised shape measures are derived, which sum to 1:

| Measure | Formula | Meaning |
|---|---|---|
| $c_l$ (linear) | $\frac{\lambda_3 - \lambda_2}{\lambda_3}$ | Anisotropic, line-like structure |
| $c_p$ (planar) | $\frac{\lambda_2 - \lambda_1}{\lambda_3}$ | Sheet-like structure |
| $c_s$ (spherical) | $\frac{\lambda_1}{\lambda_3}$ | Isotropic, blob-like structure |

High $c_l$ indicates a well-defined fibrous orientation, high $c_p$ indicates a layered structure, and high $c_s$ indicates isotropic regions.

{{< fig src="/images/tools/structure-tensor/Figure2.png" caption="**Figure 2:** Neighbourhoods and structures corresponding to linear, planar and spherical shape measures." >}}

{{< fig src="/images/tools/structure-tensor/Figure5.png" caption="**Figure 5:** Orientation analysis on synthetic objects — shape measures $c_l$, $c_p$, $c_s$ visualised using RGB colour channels (red = $c_l$, green = $c_p$, blue = $c_s$)." >}}

## Features

- Computes structure tensor for every voxel in large 3D volumes
- Extracts dominant orientation ($\mathbf{v}_1$) and shape measures ($c_l, c_p, c_s$)
- Configurable noise scale $\sigma$ and integration scale $\rho$
- Also computes fractional anisotropy and other diffusion-like metrics
- Can be used as a standalone application or via our HPC platform
- Efficient enough for large volumetric datasets

## Usage

The tool can be used both as a standalone application and through our High Performance Computing platform. For large 3D image datasets that require cluster access, please contact us.

## Applications

- **Fibre orientation analysis** in materials science and bioimaging
- **Layer detection** in sedimentary and layered materials
- **Quality control** of anisotropic materials
- **Preprocessing** for diffusion tensor imaging and optical flow
- **Feature detection** — corner and interest point detection in 3D

{{< fig src="/images/tools/structure-tensor/Figure7.png" caption="**Figure 7:** Using colour to visualise dominant orientation of cotton fibres in woven fabric. Colour reveals the direction of the twist holding the cotton fibres together in a yarn." >}}