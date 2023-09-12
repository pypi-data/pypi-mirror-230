
class Package:
    def __init__(self, default: list, extra: list):
        self.default = default
        self.extra = extra
        self.name = default['name']
        self.ram = default['ram']
        self.cpu = default['cpu']
        self.disk = default['disk']
        self.servers = default['servers']
        self.databases = default['databases']
        self.backups = default['backups']
        self.allocations = default['allocations']
        self.extra_ram = extra['ram']
        self.extra_cpu = extra['cpu']
        self.extra_disk = extra['disk']
        self.extra_servers = extra['servers']
        self.extra_databases = extra['databases']
        self.extra_backups = extra['backups']
        self.extra_allocations = extra['allocations']