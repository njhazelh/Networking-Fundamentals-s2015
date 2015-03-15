# Experiment 1

set name "experiment1"
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

proc record-result {} {

}


proc run-single-test {} {
	
	# Create a simulator object
	set ns [new Simulator]

	# Create six nodes
	set n1 [$ns node]
	set n2 [$ns node]
	set n3 [$ns node]
	set n4 [$ns node]
	set n5 [$ns node]
	set n6 [$ns node]

	# Create links between nodes
	set duplex-link $n1 $n2 10Mb 10ms DropTail
	set duplex-link $n2 $n5 10Mb 10ms DropTail
	set duplex-link $n2 $n3 10Mb 10ms DropTail
	set duplex-link $n3 $n4 10Mb 10ms DropTail
	set duplex-link $n3 $n6 10Mb 10ms DropTail

	$ns duplex-link-op $n1 $n2 orient right-down
    $ns duplex-link-op $n2 $n5 orient right-up
    $ns duplex-link-op $n2 $n3 orient right
    $ns duplex-link-op $n3 $n4 orient right-up
    $ns duplex-link-op $n3 $n6 orient right-down

}

proc run-experiment-1 {} {
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

run-experiment-1
