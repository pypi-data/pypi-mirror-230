class TedeeClientException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        
class TedeeAuthException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class TedeeRateLimitException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class TedeeWebhookException(Exception):
    def __init__(self, msg):
        super().__init__(msg)