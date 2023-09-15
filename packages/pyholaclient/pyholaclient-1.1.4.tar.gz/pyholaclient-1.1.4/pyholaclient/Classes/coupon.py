
class Coupon:
    def __init__(self, coins: int, ram: int, disk: int, cpu: int, servers: int, backups: int, allocation: int, database: int,uses: int,  code: str = None):
        self.code = code
        self.coins = coins
        self.ram = ram
        self.disk = disk
        self.cpu = cpu
        self.servers = servers
        self.backups = backups
        self.allocation = allocation
        self.database = database
        self.uses = uses
