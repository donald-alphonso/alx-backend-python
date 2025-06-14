import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden
import time
from django.http import JsonResponse
from collections import defaultdict, deque

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request_logger')
        handler = logging.FileHandler('c:/Users/SYKO Electronics/Desktop/alx-backend-python/Django-Middleware-0x03/chats/requests.log')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        start = time(18, 0)  # 6:00 PM
        end = time(21, 0)    # 9:00 PM
        if not (start <= now <= end):
            return HttpResponseForbidden("Access to the messaging app is only allowed between 6PM and 9PM.")
        return self.get_response(request)


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            # Check if user is admin (superuser or staff)
            if user.is_superuser or user.is_staff:
                return self.get_response(request)
            # Check if user has 'moderator' group
            if user.groups.filter(name='moderator').exists():
                return self.get_response(request)
            return HttpResponseForbidden('You do not have permission to perform this action (admin or moderator only).')
        return HttpResponseForbidden('Authentication required.')


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_message_times = defaultdict(deque)
        self.limit = 5
        self.window = 60  # seconds

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/chats/messages'):
            ip = self.get_client_ip(request)
            now = time.time()
            times = self.ip_message_times[ip]
            # Remove timestamps older than 1 minute
            while times and now - times[0] > self.window:
                times.popleft()
            if len(times) >= self.limit:
                return JsonResponse({'error': 'Message rate limit exceeded. Max 5 messages per minute.'}, status=429)
            times.append(now)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip