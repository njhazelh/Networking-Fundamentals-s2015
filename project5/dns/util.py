__author__ = 'njhazelh'

def domain_to_dns(name):
    """
    Convert a domain name to dns format.
    :param name: The name to convert.
    :return: The dns formatted version of name.
    """
    converted = b''
    for label in name.split("."):
        converted += chr(len(label))
        converted += label.encode()
    converted += b'\x00'
    return converted

def dns_to_domain(dns):
    """
    Take a dns formatted domain name and convert it to a normal IPv4 String.
    :param dns: The dns bytestring of the domain to get.
    :return: An formatted domain name.
    """
    converted = ""
    index = 1
    next_len = dns[0]
    while next_len > 0:
        while next_len > 0:
            c = chr(dns[index])
            index += 1
            converted += c
            next_len -= 1
        converted += "."
        next_len = dns[index]
        index += 1
    return converted[:-1], index - 1
