from django.apps import AppConfig


class DjangoHorizontalListFilterConfig(AppConfig):
    name = 'django_horizontal_list_filter'

    def ready(self):
        # inject our css&js into media
        from django.contrib.admin import ModelAdmin
        from django import forms
        from django.utils.translation import get_language
        from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
        from django.conf import settings

        extra_js = [
            "admin/js/vendor/jquery/jquery.js",
            "django-horizontal-list-filter/js/django-horizontal-list-filter.js",
        ]
        extra_css = []

        DJANGO_HORIZONTAL_LIST_FILTER_USE_SELECT2 = getattr(settings, "DJANGO_HORIZONTAL_LIST_FILTER_USE_SELECT2", False)
        if DJANGO_HORIZONTAL_LIST_FILTER_USE_SELECT2:
            extra_js.append("admin/js/vendor/select2/select2.full.js")
            extra_js.append("django-horizontal-list-filter/js/django-horizontal-list-filter-use-select2.js")
            extra_css.append("admin/css/vendor/select2/select2.css")
            SELECT2_LANGUAGE_CODE = SELECT2_TRANSLATIONS.get(get_language())
            if SELECT2_LANGUAGE_CODE:
                extra_js.append("admin/js/vendor/select2/i18n/%s.js" % SELECT2_LANGUAGE_CODE)
        
        extra_js += [
            "admin/js/jquery.init.js",
        ]
        extra_css += [
            "django-horizontal-list-filter/css/django-horizontal-list-filter.css",
        ]
        
        ModelAdmin.__django_horizontal_list_filter_old_media = ModelAdmin.media
        ModelAdmin.__django_horizontal_list_filter_old_get_list_filter = ModelAdmin.get_list_filter

        @property
        def media(self):
            return self.__django_horizontal_list_filter_old_media + forms.Media(css={"all": extra_css}, js=extra_js)
        
        def get_list_filter(self, request):
            getattr(request, "is_using_django_horizontal_list_filter", True)
            return ModelAdmin.__django_horizontal_list_filter_old_get_list_filter(self, request)

        ModelAdmin.media = media
        ModelAdmin.get_list_filter = get_list_filter
