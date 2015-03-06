# Networking Fundamentals Project 3: Performance Analysis of TCP Variants
__Nick Jones, Michelle Suk__

## Methodology
### Network Configuration
All tests will be run on NS-2 with the following network on configuration:
```
    +-------+                                          +-------+
    |       |                                          |       |
    |  N1   |                                          |  N4   |
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
    |  N5   |                                          |  N6   |
    |       |                                          |       |
    +-------+                                          +-------+
```
Each link will have a bandwidth of 10 Mbps.

### Randomness
In order to find the average performance of TCP variants over a variety of
different environments, we shall vary the network latency and
buffer sizes of the clients randomly over a series of tests.  We will then
average the results of these tests together to obtain a generalized performance
metric.  The properties varied for each experiement will change, however, all
properties will be within the following ranges.

| Property    | Lower Bound | Upper Bound |
| ----------- | ----------- | ----------- |
| Latency     | 10 ms       | 1 s         |
| Buffer Size | ???         | ???         |
| Start time  | 0 ms        | 2 s         |

### Experiments
#### Experiment 1: TCP Performance Under Congestion
Variables: Buffer size, start time

Iterations: N

1. For each TCP in Tahoe, Reno, NewReno, Vegas:
    2. For N tests with start time as _S_ and buffer-sizes as _B_:
        3. _CBR-flow_ = 1 Mbps
        4. While CBR-flow does not bottle-neck network:
          5. Add a CBR from N2 -> N3 with bandwidth of _CBR-flow_.
          6. Add a TCP flow from N1 -> N4
          7. Start TCP flow at time S.
          8. Measure throughput, drop-rate, latency.
          9. Increase _CBR-flow_ by 1 Mbps.

#### Experiment 2: Fairness Between TCP Variants
Variables: start time, buffer sizes

Iterations: N

1. For each __TCPa__, __TCPb__ in Reno/Reno, NewReno/Reno, Vegas/Vegas, NewReno/Vegas:
    2. For N tests with latency as __L__ and buffer-sizes as __B__:
        3. Add a CBR flow from N2 -> N3 with bandwidth of 1 Mbps.
        4. Add a __TCPa__ flow from N1 -> N4.
        5. Add a __TCPb__ flow from N5 -> N6.
        6. Measure throughput, drop-rate, latency.

#### Experiment 3: Influence of Queuing
Variables: start time, CBR flow

Iterations: N

1. For __TCP__ in Reno, SACK:
    2. For __Algo__ in DropTail, RandomEarlyDrop:
        3. For __N__ tests with start time as __S__ and CBR flow as __F__:
          4. Add a CBR flow from N5 -> N6 with bandwidth of __F__ Mbps.
          5. Add a TCP flow from N1 -> N4 using __Algo__.
          6. Start __TCP__.
          7. Start CBR at time __S__ after start of TCP flow.
          8. Measure throughput, drop-rate, latency.

### Analysis
#### Tools
We plan to use Python to interpret the data and a Python plotting library
such as [Plotly](https://plot.ly/feed/) to plot the data.
