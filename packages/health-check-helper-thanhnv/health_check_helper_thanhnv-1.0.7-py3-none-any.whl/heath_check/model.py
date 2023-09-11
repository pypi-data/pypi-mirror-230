import json


class HealthCheckService:
    def __init__(self, system, service_group, service_name, type, data, note,message_format =None,raw={}):
        self.system = system
        self.service_group = service_group
        self.service_name = service_name
        self.type = type
        self.data = data
        self.note = note
        self.host_port = "0.0.0.0:0"
        self.result = {
            'healthy': True,
            'message': 'Service is Healthy'
        }
        self.message_format = message_format
        self.raw = raw

    def set_healthy(self):
        self.result['healthy'] = True

    def set_unhealthy(self, msg):
        self.result['healthy'] = False
        self.result['message'] = msg


def read_from_json_file(file_path):
    f = open(file_path)
    data = json.load(f)
    return from_json(data)


def from_json(json_object):
    health_check_services = list()
    for system in json_object:
        system_name = system.get("system")
        service_groups = system.get("service_groups")
        message_format = system.get("message_format")
        for service_group in service_groups:
            group_name = service_group.get("name")
            services = service_group.get("services")
            for service in services:
                service_name = service.get("name")
                note = service.get("note")
                monitor = service.get("monitor")
                monitor_type = monitor.get("type")
                data = monitor.get("data")
                health_check_service = HealthCheckService(
                    system=system_name,
                    service_group=group_name,
                    service_name=service_name,
                    type=monitor_type,
                    data=data,
                    note=note,
                    message_format=message_format,
                    raw=system
                )
                health_check_services.append(health_check_service)

    return health_check_services


if __name__ == '__main__':
    p = "monitor_source.json"
    l = read_from_json_file(p)
    print(l)
