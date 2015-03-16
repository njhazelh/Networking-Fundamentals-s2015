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

set NAME "experiment2"
set ITERATIONS 10

# TCP Variants
set RENO 0
set NEW_RENO 1
set VEGAS 2
set UDP 3
set VARIANT_COMBOS {{0 0} {1 0} {2 2} {1 2}}

set ns [new Simulator]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

# Open files for output
#puts $file "TCP1, TCP2, Time, CBR Bandwidth, TCP1 Bandwidth, TCP2 Bandwidth, TCP1 Loss Rate, TCP2 Loss Rate, TCP1 Latency, TCP2 Latency"

# copied from http://www.isi.edu/nsnam/ns/tutorial/nsscript4.html#second
proc finish-and-record {ns cbr_bw tcp1_id tcp2_id sink1 sink2} {
    global file

    #Get the current time
    set now [$ns now]

    #How many bytes have been received by the traffic sinks?
    set tcp1_name [enum->tcp_name $tcp1_id]
    set tcp1_bytes [$sink1 set bytes_]
    set tcp1_bw [expr $tcp1_bytes/$now*8/1000000]
    set tcp1_loss 0
    set tcp1_lat 0

    set tcp2_name [enum->tcp_name $tcp2_id]
    set tcp2_bytes [$sink2 set bytes_]
    set tcp2_bw [expr $tcp2_bytes/$now*8/1000000]
    set tcp2_loss 0
    set tcp2_lat 0

    set line "$tcp1_name, $tcp2_name, $now, $cbr_bw, $tcp1_bw, $tcp2_bw, $tcp1_loss, $tcp2_loss, $tcp1_lat, $tcp2_lat"

    #Calculate the bandwidth (in MBit/s) and write it to the files
    puts $line

    $ns halt
    delete $ns
    exit 0
}

proc enum->tcp {enum} {
    global RENO NEW_RENO VEGAS
    if {$enum == $RENO} {
        return [new Agent/TCP/Reno]
    } elseif {$enum == $NEW_RENO} {
        return [new Agent/TCP/Newreno]
    } elseif {$enum == $VEGAS} {
        return [new Agent/TCP/Vegas]
    } else {
        error "enum->tcl_name: $enum is not  a TCP id"
    }
}

proc enum->tcp_name {enum} {
    global RENO NEW_RENO VEGAS
    if {$enum == $RENO} {
        return "Reno"
    } elseif {$enum == $NEW_RENO} {
        return "NewReno"
    } elseif {$enum == $VEGAS} {
        return "Vegas"
    } else {
        error "enum->tcl_name: $enum is not  a TCP id"
    }
}

proc run-single-test {tcp1_id tcp2_id cbr_bw} {
    global n1 n2 n3 n4 n5 n6

    set ns [Simulator instance]

    set tcp1_start [expr {5.0 * rand()}]
    set tcp2_start [expr {5.0 * rand()}]

    # configure links
    $ns duplex-link $n1 $n2 10Mb 2ms DropTail
    $ns duplex-link $n5 $n2 10Mb 2ms DropTail
    $ns duplex-link $n2 $n3 10Mb 2ms DropTail
    $ns duplex-link $n3 $n4 10Mb 2ms DropTail
    $ns duplex-link $n3 $n6 10Mb 2ms DropTail

    # Add CBR Flow
    set udp0 [new Agent/UDP]
    set null0 [new Agent/Null]
    set cbr0 [new Application/Traffic/CBR]
    $udp0 set class_ 0
    $ns attach-agent $n2 $udp0
    $ns attach-agent $n3 $null0
    $ns connect $udp0 $null0
    # Configure CBR Bandwidth
    $cbr0 attach-agent $udp0
    $cbr0 set packetSize_ 500
    $cbr0 set interval_ 0.005

    # Add TCP1 Flow
    set tcp1_inst [enum->tcp $tcp1_id]
    set sink1 [new Agent/TCPSink]
    set cbr1 [new Application/Traffic/CBR]
    $tcp1_inst set class_ 1
    $ns attach-agent $n1 $tcp1_inst
    $ns attach-agent $n4 $sink1
    $ns connect $tcp1_inst $sink1
    # Add Traffic to TCP1 Flow
    $cbr1 attach-agent $tcp1_inst
    $cbr1 set packetSize_ 500
    $cbr1 set interval_ 0.005

    # Add TCP2 Flow
    set tcp2_inst [enum->tcp $tcp2_id]
    set sink2 [new Agent/TCPSink]
    set cbr2 [new Application/Traffic/CBR]
    $tcp2_inst set class_ 2
    $ns attach-agent $n5 $tcp2_inst
    $ns attach-agent $n6 $sink2
    $ns connect $tcp2_inst $sink2
    # Add Traffic to TCP2 Flow
    $cbr2 attach-agent $tcp2_inst
    $cbr2 set packetSize_ 500
    $cbr2 set interval_ 0.005

    $ns at 0 "$cbr0 start"
    $ns at $tcp1_start "$cbr1 start"
    $ns at $tcp2_start "$cbr2 start"
    $ns at 60 "finish-and-record $ns $cbr_bw $tcp1_id $tcp2_id $sink1 $sink2"

    $ns run
}

proc finish {} {
    global file

    close $file
    # Run Python Script
    exit 0
}

# Call from command line with arguments
# ns experiment2.tcl <tcp_combo_number> <cbr_bandwidth>
proc main {argv argc} {
    global VARIANT_COMBOS
    set tcp1 [lindex [lindex $VARIANT_COMBOS [lindex $argv 0]] 0]
    set tcp2 [lindex [lindex $VARIANT_COMBOS [lindex $argv 0]] 1]
    run-single-test $tcp1 $tcp2 [lindex $argv 1]
}

main $argv $argc
