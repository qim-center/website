+++
author = "QIM"
title = "BugNIST"
description = "volumetric dataset for object detection and segmentation"
tags = [
    "Datasets",
]
image = "images/portfolio/bugnist/logo_bugnist.png"
+++

![BugNIST cover](/images/portfolio/bugnist/bugs_overview.png)

## BugNIST – a Dataset for Detection and Segmentation under Domain Shift

BugNIST is a large collection of volumetric scans of bugs. We created BugNIST to encourage research for analyzing µCT images. There is a great need for accurate quantitative analysis of volumetric data. With 9542 individual CT volumes, BugNIST is larger than most CT data, the imaged samples are complex-shaped bugs, and as opposed to many medical datasets, it comes with no restrictions in its use. This makes BugNIST ideal as a benchmark for deep learning.

The dataset consists of scans of 12 types of bugs that are scanned as individual bugs and in mixtures. There are 9154 individual bugs and 388 mixtures. The mixtures are annotated with their center points, making the data ideal for object detection. Detecting the bugs in the mixtures using models trained on the scans of individual bugs lead to a domain shift. This domain shift is special for volumetric scans like CT, where the appearance of the objects stays the same.

### Paper

Our ECCV 2024 paper is available from on [arxiv](https://arxiv.org/pdf/2304.01838.pdf)

### Dataset

You can download our dataset from [DTU Archive](https://archive.compute.dtu.dk/files/public/projects/BugNIST3D/zips)

### Additional information:

You can find more information on [GitHub](https://abdahl.github.io/bugnist/)

### Support

The development of the BugNIST is supported by the Infrastructure for Quantitative AI-based Tomography QUAITOM which is supported by a Novo Nordisk Foundation Data Science Programme grant (Grant number NNF21OC0069766).

![NNF logo](/images/portfolio/NNF-logo-1-300x28.png)
