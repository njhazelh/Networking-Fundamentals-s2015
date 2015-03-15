# Experiment 2
# This experiment tests TCP variant against each other for fairness.
#
# The network is an H pattern with a 10 Mbps CBR over the bridge,
# and one TCP over the top and bottom.
#
# Variants compared are as follows:
# Reno/Reno
# NewReno/Reno
# Vegas/Vegas
# NewReno/Vegas

set name "experiment2" # used to name folders
set iterations 1000

# TCP Variants
set RENO "Reno"
set NEW_RENO "NewReno"
set VEGAS "Vegas"
set VARIANT_COMBOS {{RENO RENO}
                    {NEW_RENO RENO}
                    {VEGAS VEGAS}
                    {NEW_RENO VEGAS}}

# Open files for output
set f [open "results/$name/out.tr" w]
$ns trace-all $f
set nf [open "results/$name/out.nam" w]
$ns namtrace-all $nf

set udp0 [new Agent/UDP]
$ns attach-agent $n2 $udp0
set cbr0 [new Application/Traffic/CBR]
$cbr0 attach-agent $udp0
$udp0 set class_ 0

set null0 [new Agent/Null]
$ns attach-agent $n3 $null0

$ns connect $udp0 $null0
$ns at 0.5 "$cbr0 start"

$cbr0 set packetSize_ 500
$cbr0 set interval_ 0.005

set tcp [new Agent/TCP]
$tcp set class_ 1
$ns attach-agent $n1 $tcp

set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink

$ns connect $tcp $sink

$ns color 0 Blue
$ns color 1 Red

$ns at 3.0 "finish"

# copied from http://www.isi.edu/nsnam/ns/tutorial/nsscript4.html#second
proc record-result {} {
    global sink0 sink1 sink2 f0 f1 f2
    #Get an instance of the simulator
    set ns [Simulator instance]
    #Set the time after which the procedure should be called again
    set time 0.5
    #How many bytes have been received by the traffic sinks?
    set bw0 [$sink0 set bytes_]
    set bw1 [$sink1 set bytes_]
    set bw2 [$sink2 set bytes_]
    #Get the current time
    set now [$ns now]
    #Calculate the bandwidth (in MBit/s) and write it to the files
    puts $f0 "$now [expr $bw0/$time*8/1000000]"
    puts $f1 "$now [expr $bw1/$time*8/1000000]"
    puts $f2 "$now [expr $bw2/$time*8/1000000]"
    #Reset the bytes_ values on the traffic sinks
    $sink0 set bytes_ 0
    $sink1 set bytes_ 0
    $sink2 set bytes_ 0
    #Re-schedule the procedure
    $ns at [expr $now+$time] "record"
}

proc run-single-test {number tcp1 tcp2} {
    reset
    set ns [new Simulator]
    set n1 [$ns node]
    set n2 [$ns node]
    set n3 [$ns node]
    set n4 [$ns node]
    set n5 [$ns node]
    set n6 [$ns node]

    $ns duplex-link $n1 $n2 10Mb 10ms DropTail
    $ns duplex-link $n5 $n2 10Mb 10ms DropTail
    $ns duplex-link $n2 $n3 10Mb 10ms DropTail
    $ns duplex-link $n3 $n4 10Mb 10ms DropTail
    $ns duplex-link $n3 $n6 10Mb 10ms DropTail

    $ns duplex-link-op $n1 $n2 orient right-down
    $ns duplex-link-op $n5 $n2 orient right-up
    $ns duplex-link-op $n2 $n3 orient right
    $ns duplex-link-op $n3 $n4 orient right-up
    $ns duplex-link-op $n3 $n6 orient right-down

    $ns run
}

proc run-experiment-2 {} {
    foreach {combo} $VARIANT_COMBOS {
        set tcp1 [lindex $combo 0]
        set tcp2 [lindex $combo 1]
        # generate random config

        for {set i 0} {$i<iterations} {incr x} {
            run-single-test $i $tcp1 $tcp2 #other config
        }
    }
}

proc finish {} {
    global ns f nf
    $ns flush-trace
    close $f
    close $nf

    puts "running nam..."
    exec nam out.nam &
    exit 0
}

run-experiment-2
