"""
WSGI config for invisible_gallery project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invisible_gallery.settings')

application = get_wsgi_application() 