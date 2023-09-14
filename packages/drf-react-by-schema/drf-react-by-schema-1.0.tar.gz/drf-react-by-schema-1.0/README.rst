===================
DRF React By Schema
===================

This package, with the corresponding npm package with the same name, enables a django headless infrastructure for running with react very easily, directly from your models.

Pre-requisites:
---------------

* django-rest-framework
* drf-nested-routers
* django-cors-headers
* djangorestframework-simplejwt
* django-filter

Quick start:
------------

1. Add and configure the pre-requisite apps

2. Add "drf-react-by-schema" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'drf-react-by-schema',
    ]
    
3. Configure Django Rest Framework in settings, adding the drf-react-by-schema rederer, metadata and filter backend, as in the example below::

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ),
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.JSONRenderer",
            "drf_react_by_schema.renderers.CustomBrowsableAPIRenderer",
        ],
        'DEFAULT_METADATA_CLASS': 'drf_react_by_schema.metadata.Metadata',
        'DEFAULT_FILTER_BACKENDS': [
            'rest_framework.filters.SearchFilter',
            'drf_react_by_schema.filters.DRFReactBySchemaOrderingFilter',
        ],
    }

4. Configure drf-react-by-schema, for example adding the apps that should be condered for building the API endpoints. If not added to settings, the default will be ['main']. Example::

    DRF_REACT_BY_SCHEMA = {
        'APPS': [
            'main',
        ],
        'PAGINATION_MODE': 'server',
    }


5. Include the URL configuration in your project urls.py like this::

    urlpatterns = [
        ...
        path('', include('drf_react_by_schema.urls')),
    ]

6. Start the development server and visit http://127.0.0.1:8000/api/endpoints and you will see all endpoints available.

You can customize viewsets and serializers to annotate other attributes.

This package offers special fields for added control over metadata directly from model.

More documentation will come one day.