'''Custom middleware used by the pages application.'''

import re

from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect

from cms.apps.pages.models import Country
from cms.models import publication_manager, path_token_generator

if 'cms.middleware.LocalisationMiddleware' in settings.MIDDLEWARE:
    from django.contrib.gis.geoip2 import GeoIP2
    from geoip2.errors import AddressNotFoundError


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PublicationMiddleware:

    '''Middleware that enables the preview mode for admin users.'''

    def __init__(self, get_response):
        self.get_response = get_response
        self.exclude_urls = [
            re.compile(url_regex) for url_regex in getattr(settings, 'PUBLICATION_MIDDLEWARE_EXCLUDE_URLS', ())
        ]

    def __call__(self, request):
        if any(map(lambda pattern: pattern.match(request.path_info[1:]), self.exclude_urls)):
            return self.get_response(request)

        # See if preview mode is requested.
        try:
            path = f'{request.path_info[1:] if request.path_info[1:] else request.path_info}'
            # Check for the value of 'preview' matching the token for the
            # current path. This is intended to throw KeyError if is not
            # present.
            token_preview_valid = path_token_generator.check_token(request.GET['preview'], path)
            # Allow something like preview=1, preview=any_other_value if
            # they are a staff user.
            user_preview = request.GET['preview'] and request.user.is_staff
        except KeyError:
            # Preview mode was not requested.
            user_preview = False
            token_preview_valid = False

        # Only allow preview mode if the user is a logged in administrator
        # or they have a token for this specific path.
        preview_mode = token_preview_valid or user_preview
        publication_manager.begin(not preview_mode)

        response = self.get_response(request)

        publication_manager.end_all()

        # Carry on as normal.
        return response


class LocalisationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.exclude_urls = [
            re.compile(url_regex) for url_regex in getattr(settings, 'LOCALISATION_MIDDLEWARE_EXCLUDE_URLS', ())
        ]

    def __call__(self, request, geoip_path=None):
        # Continue for media and admin
        if any(map(lambda pattern: pattern.match(request.path_info[1:]), self.exclude_urls)):
            return self.get_response(request)

        # Set a default country object
        request.country = None

        # Check to see if we have a country in the URL
        country_match = re.match('/([a-z]{2})/|\b', request.path)
        if country_match:

            # Try and get a country from the database
            try:
                request.country = Country.objects.get(
                    code__iexact=str(country_match.group(1))
                )

                request.path = request.path.replace('/{}'.format(
                    country_match.group(1)
                ), '')
                request.path_info = request.path

            except Country.DoesNotExist:
                pass

        # If we don't have a country at this point, we need to do some ip
        # checking or assumption
        if request.country is None:
            # Get the Geo location of the requests IP
            geo_ip = GeoIP2(path=geoip_path)

            try:
                country_geo_ip = geo_ip.country(get_client_ip(request))
            except AddressNotFoundError:
                # If there's no county found for that IP, just don't look for a country
                # and go with the default
                country_geo_ip = {}

            code = country_geo_ip.get('country_code', '')

            request.country = Country.objects.filter(
                Q(code__iexact=code) | Q(default=True)
            ).order_by('-default').first()

            if request.country:
                return redirect('/{}{}'.format(
                    request.country.code.lower(),
                    request.path,
                ))

        response = self.get_response(request)

        return response

