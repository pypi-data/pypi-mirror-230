# -*- coding: utf-8 -*-

from ideabox.policy.testing import IdeaboxTestCase
from ideabox.policy.testing import IDEABOX_POLICY_INTEGRATION_TESTING
from ideabox.policy.tests.utils import make_named_image
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from zope.component import queryMultiAdapter


class TestRestServices(IdeaboxTestCase):

    layer = IDEABOX_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_theme_project_get(self):
        pass

    def test_district_project_get(self):
        pass
