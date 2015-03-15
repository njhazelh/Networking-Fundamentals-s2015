
# Experiment 1

proc exp1_test {} {
	
	# Create a simulator object
	set ns [new Simulator]

	# Create six nodes
	set n0 [$ns node]
	set n1 [$ns node]
	set n2 [$ns node]
	set n3 [$ns node]
	set n4 [$ns node]
	set n5 [$ns node]

	# Create links between nodes
	set duplex-link $n0 $n1 10Mb
	set duplex-link $n1 $n4 10Mb
	set duplex-link $n1 $n2 10Mb
	set duplex-link $n2 $n3 10Mb
	set duplex-link $n2 $n5 10Mb

	# TO DO
	#	Determine which TCP variant is being tested
	#	Open trace file
	# 	Set sinks
	#	CBR flow rate

	# Finish procedure
	proc finish {} {
		
	}
}