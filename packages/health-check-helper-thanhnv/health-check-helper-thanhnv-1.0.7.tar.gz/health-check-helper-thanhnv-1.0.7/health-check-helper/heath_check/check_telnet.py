import socket

def check_port(host='10.1.16.211',port="11107",timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host,int(port)))
    except Exception as e:
        print(e)

    ok =True
    if result == 0:
       # print( f"Host {host} Port {port} is open")
       pass
    else:
       print (f"Host {host} Port {port} not open")
       ok = False
    sock.close()
    return ok

def check_ports (host,ports):
    for port in ports:
        check_port(host,port)

def create_list(r1, r2):
    return list(range(r1,r2+1))

def line_to_host_port(line:str):
    if ":" in line:
        host,ports_string = line.strip().split(":")
    elif "," in line :
        host, ports_string = line.strip().split(":")
    else:
        raise Exception(f' {line} telnet format error')
    _range =False
    if " " in ports_string:
       ports = ports_string.split(" ")
    elif "-" in ports_string:
        start, end = ports_string.split("-")
        ports = create_list(int(start),int(end))
        _range = True
    else:
        ports = [ports_string]

    return host, ports, _range

# host, ports  = line_to_host_port("10.1.44.16,8020 585")


# with open("example_check_port_list","r") as f:
#     lines = f.readlines()
#     for line in lines:
#         host,ports = line_to_host_port(line)
#         check_ports(host,ports)

