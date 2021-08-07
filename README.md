# DEF CON AI Village / Twitter Algorithmic Ethics Bug Bounty

## Introduction
As one of the world's leading social networks, Twitter and its artificial intelligence systems have tremendous power to influence public perceptions, discourse, and, whether we like it or not -- how individuals are represented.
As part of the [DEF CON 29 AI Village](https://aivillage.org), Twitter has launched a first-of-its-kind [algorithmic ethics bug bounty](https://hackerone.com/twitter-algorithmic-bias?type=team) for which this is a submission.
The bug bounty seeks to address representational and allocative harms which can lead to a variety of negative outcomes, as detailed in their [image crop analysis paper](https://arxiv.org/abs/2105.08667) and [its associated code](https://github.com/twitter-research/image-crop-analysis), from which our analysis borrows heavily.
Our work builds on this previous image crop analysis conducted by Twitter, leveraging a subset of the [FaceScrub](http://vintage.winklerbros.net/facescrub.html) dataset to evaluate the efficacy of their changes in saliency. 

## Methods
Using the aforementioned FaceScrub dataset, we randomize the set of images which could be successfully retrieved (since many hyperlinks in the dataset are now dead). 
Using the `join_images` function, we combine one male and one female image - randomly allocating each to the left or the right side of the image - separated by 200 pixels of whitespace.
We then leverage Twitter's saliency map to find whether the crop prefers the left or right image.
Since there are over 25,000 examples in our dataset, not all crops could be examined in the time allocated, so aggregate results are reported below along with spot-checked findings.

## Findings
![Image displaying a chart with 14,382 female results and 10,813 male results](https://raw.githubusercontent.com/erickgalinkin/algorithmic_ethics/main/counts.png)

In the course of this research, we found that the saliency map more appropriately balances features associated with male and female faces, cropping them relatively similarly.
However, the issue of the "male gaze" cases where a male face is compared with a female body, leading to a slight bias when cropping images that contain both male and female subjects.

