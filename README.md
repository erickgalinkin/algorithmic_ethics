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
Since there are 25634 examples in our dataset, not all crops can be examined in the time allocated, so aggregate results are reported below along with spot-checked findings.

## Findings
![Image displaying a chart with 14,832 female results and 10,802 male results](https://raw.githubusercontent.com/erickgalinkin/algorithmic_ethics/main/counts.png)

In the course of this research, we found that the saliency map more appropriately balances features associated with male and female faces, cropping them relatively similarly.
However, the issue of the "male gaze" cases where a male face is compared with a female body, leading to a slight bias when cropping images that contain both male and female subjects.
The joined images are available on Google Drive: https://drive.google.com/file/d/1QLPj6KSp-U-EEednup9SW1mAiWlaz9_F/view?usp=sharing

The identified harm is unintentional denigration -- the objectification of the female body according to heterosexual male preferences, a harm which was previously identified by the authors of the Twitter crop analysis paper.

### Recommendation for Self-Grading
Although this harm may not be completely systematic, it demonstrates that the harm has not been fully redressed, leading to unintentional denigration on a marginalized community. 
Base Point allocation -- Unintentional Denigration: 20 points
Impact -- Harm on a single axis of identity (gender): x 1.2
Affected Users -- more than 1 million: x 1.2
Likelihood -- occurs daily: x 1.3
Exploitability -- No skills needed: 1.3
Justification -- Well motivated methodology and justification: x1.25
Clarity of contribution -- Some evidence of harm but not conclusive: x1.0
Final score: 20 * (1.2 * 1.2 * 1.3 * 1.3 * 1.25) = 60.84
