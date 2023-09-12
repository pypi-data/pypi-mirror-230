import inspect
import threading


class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        current_user.user = user

        return self.get_response(request)

current_user = threading.local()
