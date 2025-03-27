from django.conf import settings


def global_vars(request):
    static_url = settings.STATIC_URL.rstrip('/')  # Remove trailing slash if exists
    return {'dist': f'{static_url}/frontend/dist/'}
