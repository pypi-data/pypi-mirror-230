from .package import Package
class User:
    def __init__(self, user: dict, package: Package):
        self.package = package

        self.email = user['pterodactyl']['attributes']['email']
        self.first_name = user['pterodactyl']['attributes']['first_name']
        self.last_name = user['pterodactyl']['attributes']['last_name']  
        self.username = user['pterodactyl']['attributes']['username']
        self.language = user['pterodactyl']['attributes']['language']
        self.id = user['pterodactyl']['attributes']['id']
        self.external_id = user['pterodactyl']['attributes']['external_id']
        self.root_admin = user['pterodactyl']['attributes']['root_admin']
        self.uuid = user['pterodactyl']['attributes']['uuid']
        self.created_at = user['pterodactyl']['attributes']['created_at']
        self.updated_at = user['pterodactyl']['attributes']['updated_at']
        self.relationships = user['pterodactyl']['attributes']['relationships']
        self.coins = user['coins']
