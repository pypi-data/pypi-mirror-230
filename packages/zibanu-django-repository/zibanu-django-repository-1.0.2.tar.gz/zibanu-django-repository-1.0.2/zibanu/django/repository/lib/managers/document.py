# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/02/23 15:45
# Project:      Zibanu Django Project
# Module Name:  document
# Description:
# ****************************************************************
from zibanu.django.db import models


class Document(models.Manager):
    """
    Manager class for Document model
    """
    def get_by_uuid(self, uuid: str) -> models.QuerySet:
        """
        Get a document queryset from the uuid value
        Parameters
        ----------
        uuid: String with uuid value

        Returns
        -------
        qs: Queryset with filter by uuid value
        """
        return self.filter(uuid__exact=uuid)

    def get_by_code(self, code: str) -> models.QuerySet:
        """
        Get a document queryset from the code value.

        Parameters
        ----------
        code: String with code value

        Returns
        -------
        qs: Queryset with filter by code value.
        """
        return self.filter(code__exact=code)

