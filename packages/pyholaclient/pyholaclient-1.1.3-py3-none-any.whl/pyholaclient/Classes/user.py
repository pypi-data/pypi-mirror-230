from .package import Package
class User:
    def __init__(self, user: dict, package: Package):
        self.package = package
        self.user = user['userinfo']
        self.email = self.user['attributes']['email']
        self.first_name = self.user['attributes']['first_name']
        self.last_name = self.user['attributes']['last_name']  
        self.username = self.user['attributes']['username']
        self.language = self.user['attributes']['language']
        self.id = self.user['attributes']['id']
        self.external_id = self.user['attributes']['external_id']
        self.root_admin = self.user['attributes']['root_admin']
        self.twofa_enabled = self.user['attributes']['2fa']
        self.uuid = self.user['attributes']['uuid']
        self.created_at = self.user['attributes']['created_at']
        self.updated_at = self.user['attributes']['updated_at']
        self.relationships = self.user['attributes']['relationships']
        self.attributes = self.user['attributes']
        self.coins = user['coins']
