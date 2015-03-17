set RENO 0
set NEW_RENO 1
set VEGAS 2

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
