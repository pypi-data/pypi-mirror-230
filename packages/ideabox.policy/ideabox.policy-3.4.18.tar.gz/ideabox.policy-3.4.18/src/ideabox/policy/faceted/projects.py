# -*- coding: utf-8 -*-

from collective.faceted.map import _
from collective.faceted.map.browser.map import MapView
from ideabox.policy.utils import can_view_rating
from plone import api
from Products.CMFPlone import PloneMessageFactory as trad_plone
from urllib.parse import urlparse
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory

import json


class ProjectsView(MapView):
    @property
    def map_configuration(self):
        map_layers = api.portal.get_registry_record("geolocation.map_layers") or []
        config = {
            "fullscreencontrol": api.portal.get_registry_record(
                "geolocation.fullscreen_control", default=True
            ),
            "locatecontrol": api.portal.get_registry_record(
                "geolocation.locate_control", default=True
            ),
            "zoomcontrol": api.portal.get_registry_record(
                "geolocation.zoom_control", default=True
            ),
            "minimap": api.portal.get_registry_record(
                "geolocation.show_minimap", default=True
            ),
            "addmarker": api.portal.get_registry_record(
                "geolocation.show_add_marker", default=False
            ),
            "geosearch": api.portal.get_registry_record(
                "geolocation.show_geosearch", default=False
            ),
            "geosearch_provider": api.portal.get_registry_record(
                "geolocation.geosearch_provider", default=[]
            ),
            "default_map_layer": api.portal.get_registry_record(
                "geolocation.default_map_layer", default=[]
            ),
            "latitude": api.portal.get_registry_record(
                "geolocation.default_latitude", default=0.0
            ),
            "longitude": api.portal.get_registry_record(
                "geolocation.default_longitude", default=0.0
            ),
            "map_layers": [
                {
                    "title": translate(_(map_layer), context=self.request),
                    "id": map_layer,
                }
                for map_layer in map_layers
            ],
            "useCluster": False,
        }
        return json.dumps(config)

    def default_image(self, obj=None):
        if getattr(obj, "project_image", None) is None:
            return "{0}/project_default.jpg".format(api.portal.get().absolute_url())
        return "{}/@@images/project_image/project_faceted".format(obj.absolute_url())

    def rating(self, context):
        return can_view_rating(context)

    def get_theme(self, key):
        if not hasattr(self, "_themes"):
            factory = getUtility(IVocabularyFactory, "collective.taxonomy.theme")
            self._themes = factory(self.context)
        try:
            return self._themes.getTerm(key).title
        except KeyError:
            return ""
    @property
    def display_projects_status(self):
        display_projects_status = api.portal.get_registry_record("ideabox.policy.browser.controlpanel.IIdeaBoxSettingsSchema.display_projects_status")
        return display_projects_status

    def get_status(self, obj):
        current_lang = api.portal.get_current_language()
        current_state = api.content.get_state(obj)
        return [current_state, translate(trad_plone(current_state), context=self.request,target_language=current_lang)]

    def get_path(self):
        context = self.context
        return "/".join(context.getPhysicalPath())

    def can_submit_project(self):
        if self.context.portal_type != "campaign":
            return False
        return getattr(self.context, "project_submission", False)

    @property
    def is_there_eguichet_project_form(self):
        if api.portal.get_registry_record(
            "ideabox.policy.browser.controlpanel.IIdeaBoxSettingsSchema.ts_project_submission_path"
        ):
            return True
        return False

    @property
    def open_project_form(self):
        form_url = ""
        campagne_ideabox_path = urlparse(self.context.absolute_url()).path
        if getattr(self.context, "ts_project_submission_path", None) is not None:
            form_url = "window.open('{}/?campagne={}','_blank')".format(
                self.context.ts_project_submission_path, campagne_ideabox_path
            )
        elif self.is_there_eguichet_project_form:
            eguichet_form_path = api.portal.get_registry_record(
                "ideabox.policy.browser.controlpanel.IIdeaBoxSettingsSchema.ts_project_submission_path"
            )
            form_url = "window.open('{}/?campagne={}','_blank')".format(
                eguichet_form_path, campagne_ideabox_path
            )
        else:
            form_url = "window.open('{}/{}','_self')".format(
                self.get_path(), "@@project_submission"
            )
        return form_url
