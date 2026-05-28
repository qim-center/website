+++
title = "Structure Tensor"
description = "Analyses orientation in volumetric images using the gradient-based structure tensor method."
authors = ["Niels Jeppesen"]
tags = ["Analysis", "Orientation"]
image = "images/tools/structure-tensor.png"
source_url = "https://github.com/Skielex/structure-tensor"
+++

The structure tensor is a 3×3 symmetric positive semi-definite matrix that summarizes orientation in a small neighbourhood around every point in a 3D volume. This tool provides an efficient implementation for computing the structure tensor and extracting dominant orientations and shape measures from large 3D datasets.

{{< fig src="/images/tools/structure-tensor/Figure7.png" caption="Structure tensor analysis on fibers, color coded based on orientation." >}}
