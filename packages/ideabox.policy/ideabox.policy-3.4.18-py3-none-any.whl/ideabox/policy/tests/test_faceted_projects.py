# -*- coding: utf-8 -*-

from ideabox.policy.testing import IdeaboxTestCase
from ideabox.policy.testing import IDEABOX_POLICY_INTEGRATION_TESTING
from ideabox.policy.tests.utils import make_named_image
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from zope.component import queryMultiAdapter


class TestFacetedProject(IdeaboxTestCase):

    layer = IDEABOX_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        self.campaign = api.content.create(
            container=self.portal,
            type="campaign",
            id="campaign",
        )

    def test_faceted_rendering(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My first project",
        )
        api.content.transition(project, "deposit")
        view = queryMultiAdapter((self.campaign, self.request), name="faceted-explorer")
        self.assertIn("My first project", view())
        self.assertNotIn("@@images/project_image/project_faceted", view())
        self.assertNotIn('<span class="theme"', view())
        self.assertNotIn('id="btn-create-projects"', view())
        img = NamedBlobImage(**make_named_image())
        project.project_image = img
        self.assertIn("@@images/project_image/project_faceted", view())
        project.project_theme = ["PROP"]
        self.assertIn('<span class="theme"', view())

        self.campaign.project_submission = True
        view = queryMultiAdapter((self.campaign, self.request), name="faceted-explorer")
        self.assertIn('id="btn-create-projects"', view())

        api.portal.set_registry_record(
            "ideabox.policy.browser.controlpanel.IIdeaBoxSettingsSchema.ts_project_submission_path",
            "https://e-guichet.imio.be/",
        )
        self.assertIn("https://e-guichet.imio.be/", view())
