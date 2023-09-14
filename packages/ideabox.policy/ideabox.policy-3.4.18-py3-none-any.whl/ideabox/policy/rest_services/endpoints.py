# -*- coding: utf-8 -*-

from ideabox.policy.utils import get_vocabulary
from plone.restapi.services import Service


class ThemeProjectGet(Service):
    def reply(self):
        voc_theme = get_vocabulary("ideabox.vocabularies.theme")
        result = [{"id": voc.value, "text": voc.title} for voc in voc_theme]
        return result


class DistrictProjectGet(Service):
    def reply(self):
        voc_district = get_vocabulary("ideabox.vocabularies.district")
        result = [{"id": voc.value, "text": voc.title} for voc in voc_district]
        return result
