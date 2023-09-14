# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/02/23 16:11
# Project:      Zibanu Django Project
# Module Name:  apps
# Description:
# ****************************************************************
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ZbDjangoRepository(AppConfig):
    """
    Inherited class from django.apps.AppConfig to define configuration for zibanu.django.repository app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = "zibanu.django.repository"
    label = "zb_repository"
    verbose_name = _("Zibanu Django Repository")

    def ready(self):
        """
        Override method used for django application loader after the application has been loaded successfully.

        Returns
        -------
        None

        Settings
        -------
        ZB_REPOSITORY_DIRECTORY: Name of directory to store the generated documents in MEDIA_ROOT path. Default "ZbRepository"
        """
        settings.ZB_REPOSITORY_DIRECTORY = getattr(settings, "ZB_REPOSITORY_DIRECTORY", "ZbRepository")
