# scheduled-scaler

## Problem Statement:

  Cloud infrastructure can be expensive for large and high traffic systems. 
  TPS(transaction per second) sometimes is easy to determine (for instance Black friday , Cyber monday)

  The Auto-scaling features provided by the cloud providers only works in a reactive fashion after 
  causing noticable distruptions for guests/customers. Often, Auto-Scaling is based on
  CPU & memory usage that may not neccessarily be the correct measures to scale up 
  the infrastructure.

  The Idea is to predict the TPS/order trend and scale up and down instances ahead of time
#### Overview:

  This micro-batch runs every hours to read from predicted TPS/order_count from a PG 
  instance and scale up or down cloud cluster size 

#### Design decisions:

 - Scale up or down will be intiated only when the percentage change is more than 20%
 - Scaling up and down will be done 4 at a time. e.g 20 instances scale up will be done 
 in 4 batches.
 - This application only works for GCP. However it can be modified for other providers as well.
 

### Why not Auto-scaling?

We scale ahead of time before the events or spike seasons (holiday seasons Nov-Dec) generally. Auto scaling is reactive in nature and often times, its based on CPU and memory usage. 
Predictive scaling works based on TPS/order trend.Predictive scaling and auto scaling can co-exist.

