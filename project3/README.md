# Networking Fundamentals Project 3: Performance Analysis of TCP Variants
Nick Jones, Michelle Suk

## Methodology
### Network Configuration
All tests will be run on NS-2 with the following network on configuration:
```
    +-------+                                          +-------+
    |       |                                          |       |
    |  N1   |                                          +  N4   |
    |       |                                          |       |
    +--+----+                                          +----+--+
       |                                                    |
       |            +-------+          +-------+            |
       +------------+       |          |       +------------+
                    |  N2   +----------+  N3   |
       +------------+       |          |       +------------+
       |            +-------+          +-------+            |
       |                                                    |
       |                                                    |
    +--+----+                                          +----+--+
    |       |                                          |       |
    |  N5   |                                          +  N6   |
    |       |                                          |       |
    +-------+                                          +-------+
```
Each link will have a bandwidth of 10 Mbps.

### Randomness
In order to find the average performance of TCP variants over a variety of
different environments, we shall vary the network latency and
buffer sizes of the clients randomly over a series of tests.  We will then
average the results of these tests together to obtain a generalized performance
metric.

| Property    | Lower Bound | Upper Bound |
| ----------- | ----------- | ----------- |
| Latency     | 10 ms       | 1 s         |
| Buffer Size | ???         | ???         |

### Experiments
#### Experiment 1: TCP Performance Under Congestion
1. For each TCP in Tahoe, Reno, NewReno, Vegas:
    2. For N tests with latency and buffer sizes:
        3. CBR-flow = 1 Mbps
        4. While CBR-flow does not bottle-neck network:
          5. Add a CBR from N2 -> N3 with bandwidth of CBR-flow
          6. Add a TCP flow from N1 -> N4
          7. Measure throughput, drop-rate, latency.
          8. Increase CBR-flow by 1 Mbps.

#### Experiment 2: Fairness Between TCP Variants
1. For each TCP1, TCP2 in Reno/Reno, NewReno/Reno, Vegas/Vegas, NewReno/Vegas:
    2. Add a CBR flow from N2 -> N3 with bandwidth of 1 Mbps.
    3. Add a TCP1 flow from N1 -> N4.
    4. Add a TCP2 flow from N5 -> N6.
    5. Measure throughput, drop-rate, latency.

We could vary CBR bandwidth here.

#### Experiment 3: Influence of Queuing
1. For TCP in Reno, SACK:
    2. For Algo in DropTail, RandomEarlyDrop:
        3. Add a CBR flow from N5 -> N6 with bandwidth of 1 Mbps.
        4. Add a TCP flow from N1 -> N4 using Algo.
        5. Start TCP.
        6. Start CBR when TCP steady.
        7. Measure throughput, drop-rate, latency.

We could vary CBR bandwidth here.
