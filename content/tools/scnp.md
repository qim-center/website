+++
title = "Same-Class Neighbor Penalization"
description = "SCNP is an optimization method for improving topology accuracy in image segmentation deep learning models."
authors = ["Juan Miguel Valverde"]
tags = ["Segmentation", "Topology", "Deep Learning"]
image = "images/tools/scnp.png"
source_url = "https://jmlipman.github.io/SCNP-SameClassNeighborPenalization/"
+++

Same-Class Neighbor Penalization (SCNP) is a novel optimization method designed to improve the topological accuracy of image segmentation models. SCNP discourages topological errors, such as broken connections, or isolated holes or islands, by penalizing the poorest-classified neighbor of each pixel’s logit. This is achieved through simple min- and max-pooling operations over local neighborhoods, which amplify the loss contribution of pixels that are most likely to create incorrect connectivity.

<img src="https://jmlipman.github.io/SCNP-SameClassNeighborPenalization/static/images/teaser.png" />

The importance of topological accuracy arises in many real-world applications where connectivity and object counts matter more than exact boundaries. For example, in blood vessel or neuron segmentation, preserving the correct branching structure and number of connected components is critical for downstream analysis like blood flow simulation or neural circuit reconstruction.

<img src="https://jmlipman.github.io/SCNP-SameClassNeighborPenalization/static/images/results_qualitative.png" />

SCNP is simple and efficient, with a minimal computational overhead in the order of miliseconds and a few MiB of GPU memory. The entire method adds only three lines of code to any existing training pipeline, regardless of the base architecture, loss function, or optimization strategy. It operates directly on logits and consists of two pooling operations (one foreground, one background) followed by a combination step.
