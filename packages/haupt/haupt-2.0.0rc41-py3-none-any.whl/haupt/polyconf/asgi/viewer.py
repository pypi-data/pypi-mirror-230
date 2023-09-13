"""
ASGI config for deploy project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from haupt import settings
from polyaxon.contexts import paths as ctx_paths
from polyaxon.env_vars.keys import (
    EV_KEYS_SANDBOX_IS_LOCAL,
    EV_KEYS_SERVICE,
    EV_KEYS_UI_IN_SANDBOX,
)
from polyaxon.services.values import PolyaxonServices

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haupt.polyconf.settings")
os.environ.setdefault("ASGI_APPLICATION", "haupt.polyconf.asgi.viewer.application")
os.environ[EV_KEYS_SERVICE] = PolyaxonServices.STREAMS
os.environ[EV_KEYS_UI_IN_SANDBOX] = "true"
os.environ[EV_KEYS_SANDBOX_IS_LOCAL] = "true"
settings.set_sandbox_config(path=ctx_paths.CONTEXT_OFFLINE_ROOT)
application = get_asgi_application()
