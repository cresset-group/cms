"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.views.static import serve

from cms.apps.feeds import registered_feeds
from cms.apps.pages.admin import site as admin_site
from cms.apps.pages.sitemaps import registered_sitemaps


__all__ = ("patterns", "url", "include", "urlpatterns", "handler404", "handler500",)


admin.autodiscover()


urlpatterns = patterns("",
                       # TinyMCE configuration views.
                       url(r"^admin/tinymce-init.js$", "django.views.generic.simple.direct_to_template", kwargs={"template": "admin/tinymce_init.js", "mimetype": "text/javascript"}, name="tinymce_init"),
                       url(r"^admin/tinymce-link-list.js$", "cms.apps.media.views.tinymce_link_list", name="tinymce_link_list"),
                       url(r"^admin/tinymce-image-list.js$", "cms.apps.media.views.tinymce_image_list", name="tinymce_image_list"),
                       # Admin views.
                       url(r"^admin/", include(admin_site.urls)),
                       # Permalink redirection service.
                       url(r"^links/(?P<content_type_id>\d+)/(?P<object_id>.+)/$", "cms.apps.pages.views.permalink_redirect", name="permalink_redirect"),
                       # Google sitemap service.
                       url(r"^sitemap.xml$", "django.contrib.sitemaps.views.index", {"sitemaps": registered_sitemaps}, name="sitemap"),
                       url(r"^sitemap-(?P<section>.+)\.xml$", "django.contrib.sitemaps.views.sitemap", {"sitemaps": registered_sitemaps}),
                       # RSS feed service.
                       url(r"^feeds/(?P<url>.*)/$", "django.contrib.syndication.views.feed", {"feed_dict": registered_feeds}, name="feeds"),
                       # Basic robots.txt.
                       url(r"^robots.txt$", "django.views.generic.simple.direct_to_template", kwargs={"template": "robots.txt", "mimetype": "text/plain"}, name="robots_txt"),)


# Set up static media serving.

if settings.SERVE_STATIC_MEDIA:
    for media_url, media_root in settings.STATIC_MEDIA:
        media_regex = r"^%s(.*)" % media_url.lstrip("/")
        urlpatterns += patterns("", url(media_regex, serve, {"document_root": media_root}))


handler404 = "cms.apps.pages.views.handler404"


handler500 = "cms.apps.pages.views.handler500"

