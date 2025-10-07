from rest_framework.throttling import SimpleRateThrottle


class BurstPerSecondThrottle(SimpleRateThrottle):
    scope = "burst_per_sec"

    def get_cache_key(self, request, view):
        ident = (
            request.user.pk
            if request.user and request.user.is_authenticated
            else self.get_ident(request)
        )
        return self.cache_format % {"scope": self.scope, "ident": ident}


class SustainedPerMinuteThrottle(SimpleRateThrottle):
    scope = "sustained_per_min"

    def get_cache_key(self, request, view):
        ident = (
            request.user.pk
            if request.user and request.user.is_authenticated
            else self.get_ident(request)
        )
        return self.cache_format % {"scope": self.scope, "ident": ident}
