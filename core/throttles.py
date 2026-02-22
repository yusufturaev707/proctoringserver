from ipware import get_client_ip
from rest_framework.throttling import SimpleRateThrottle

class IPRateThrottle(SimpleRateThrottle):
    scope = 'ip'

    def get_cache_key(self, request, view):
        ip, is_routable = get_client_ip(request)
        if ip is None:
            return None  # throttle qilma
        return self.cache_format % {
            'scope': self.scope,
            'ident': ip
        }