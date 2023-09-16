from django.contrib import admin

class DjangoVisitOnSiteInNewWindowAdmin(admin.ModelAdmin):
    class Media:
        js = [
            "jquery3/jquery.js",
            "django-visit-on-site-in-new-window/js/django-visit-on-site-in-new-window.js",
        ]