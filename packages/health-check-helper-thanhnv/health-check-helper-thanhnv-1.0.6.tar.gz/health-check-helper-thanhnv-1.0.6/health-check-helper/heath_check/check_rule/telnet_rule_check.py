from heath_check.check_telnet import line_to_host_port, check_port
from heath_check.model import HealthCheckService


def telnet_rule_check(health_check_service: HealthCheckService,timeout =3):
    data = health_check_service.data
    msg = ""
    healthy = True
    for line in data:
        host, ports, _range = line_to_host_port(line)
        for port in ports:
            ok = check_port(host, port,timeout =timeout)
            if not ok:
                health_check_service.host_port = f"{host}:{port}"
                healthy = False
                msg += f"unable to connect {host}:{port}"
    if healthy:
        health_check_service.set_healthy()
    else:
        health_check_service.set_unhealthy(msg)
