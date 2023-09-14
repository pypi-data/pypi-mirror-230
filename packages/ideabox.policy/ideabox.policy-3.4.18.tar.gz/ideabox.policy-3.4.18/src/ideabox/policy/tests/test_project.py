# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from ideabox.policy.content.project import IProject
from ideabox.policy.testing import IdeaboxTestCase
from ideabox.policy.testing import IDEABOX_POLICY_FUNCTIONAL_TESTING
from ideabox.policy.tests.utils import make_named_image
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobImage
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility

# from plone.app.discussion.browser.comments import CommentForm
from ideabox.policy.browser.comment import CommentForm
from z3c.form.interfaces import IFormLayer
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import provideAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest


import transaction


class TestProject(IdeaboxTestCase):

    layer = IDEABOX_POLICY_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        self.campaign = api.content.create(
            container=self.portal,
            type="campaign",
            id="campaign",
        )

    def test_project_schema(self):
        fti = queryUtility(IDexterityFTI, name="Project")
        schema = fti.lookupSchema()
        self.assertEqual(IProject, schema)

    def test_project_fti(self):
        fti = queryUtility(IDexterityFTI, name="Project")
        self.assertTrue(fti)

    def test_project_factory(self):
        fti = queryUtility(IDexterityFTI, name="Project")
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(
            IProject.providedBy(obj),
            "IProject not provided by {0}!".format(
                obj,
            ),
        )

    def test_project_adding(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
        )

        self.assertTrue(
            IProject.providedBy(project),
            "IProject not provided by {0}!".format(
                project.id,
            ),
        )

        parent = project.__parent__
        self.assertIn("project", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=project)
        self.assertNotIn("project", parent.objectIds())

    def test_project_globally_addable(self):
        fti = queryUtility(IDexterityFTI, name="Project")
        self.assertFalse(
            fti.global_allow, "{0} is not globally addable!".format(fti.id)
        )

    def test_project_image_rendering(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My new project",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        # created a project and test if title is in rendering
        self.assertIn("My new project", view())
        self.assertNotIn("project_image/large", view())

        good_default_img_id = "project_default_large.jpg"
        default_project_img = api.content.create(
            container=self.portal,
            type="Image",
            id=good_default_img_id,
            title="project_default_large.jpg",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        # created a default img with a specific id in portal and test if this default image is in project rendering
        self.assertIn("project_default_large.jpg", view())

        img = NamedBlobImage(**make_named_image())
        project.project_image = img
        view = queryMultiAdapter((project, self.request), name="view")
        # created a project_image and test if this image is in project rendering
        # this project_image take priority over default project img
        self.assertIn("project_image/large", view())
        self.assertNotIn("project_default_large.jpg", view())

        img1 = api.content.create(
            container=project, type="Image", id="img1", title="Image 1"
        )
        img2 = api.content.create(
            container=project, type="Image", id="img2", title="Image 2"
        )
        view = queryMultiAdapter((project, self.request), name="view")
        # created Images in project container
        # these images take priority over project_image
        self.assertNotIn("project_image/large", view())
        self.assertIn("img1", view())
        self.assertIn("img2", view())

    def test_project_disctrict_rendering(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My new project",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('class="district"', view())

        project.project_district = ["DISTRICT1", "DISTRICT2"]
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertIn('class="district"', view())
        self.assertIn("Quartier 1, Quartier 2", view())

    def test_project_theme_rendering(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My new project",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('class="theme"', view())

        project.project_theme = ["PROP", "CAVI"]
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertIn('class="theme"', view())
        self.assertIn(
            "<a href=http://nohost/plone/projets#b_start=0&c5=PROP>Propreté</a>, <a href=http://nohost/plone/projets#b_start=0&c5=CAVI>Cadre de vie et urbanisme</a>",
            view(),
        )

    def test_project_image_from_campaign(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My new project",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('class ="image campaign_image"', view())

        img = NamedBlobImage(**make_named_image())
        self.campaign.image = img
        transaction.commit()
        self.assertIn('class="image campaign_image"', view())
        self.assertIn("http://nohost/plone/campaign/@@images/image", view())

    def test_project_geolocated(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My new project",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('class="latitude"', view())

        IGeolocatable(project).geolocation = Geolocation(latitude=0, longitude=0)
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('class="geolocation_wrapper"', view())

        IGeolocatable(project).geolocation = Geolocation(latitude="4.5", longitude="45")
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertIn('class="geolocation_wrapper"', view())
        self.assertIn('class="latitude"', view())

    def test_project_author(self):
        project = api.content.create(
            container=self.campaign,
            type="Project",
            id="project",
            title="My new project",
        )
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('class ="documentByLine"', view())
        self.assertNotIn('class="documentAuthor"', view())

        api.content.transition(project, "deposit")
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertIn('class="documentByLine"', view())
        self.assertNotIn('class="documentAuthor"', view())
        self.assertNotIn('<span class="authorname">', view())

        api.user.get(userid=TEST_USER_ID).setProperties(
            {"first_name": "KAMOU", "last_name": "LOX"}
        )

        view = queryMultiAdapter((project, self.request), name="view")
        self.assertIn('class="documentAuthor"', view())
        self.assertIn('<span class="authorname">KAMOU LOX', view())

        project.original_author = "Imio Test"
        view = queryMultiAdapter((project, self.request), name="view")
        self.assertNotIn('<span class="authorname">KAMOU LOX', view())
        self.assertIn('<span class="authorname">Imio Test', view())

    # def test_project_comments(self):
    #
    #     # def make_request(form={}):
    #     #     request = TestRequest()
    #     #     request.form.update(form)
    #     #     alsoProvides(request, IFormLayer)
    #     #     alsoProvides(request, IAttributeAnnotatable)
    #     #     return request
    #     #
    #     # provideAdapter(
    #     #     adapts=(Interface, IBrowserRequest),
    #     #     provides=Interface,
    #     #     factory=CommentForm,
    #     #     name="comment-form",
    #     # )
    #     #
    #     # # The form should return an error if the comment text field is empty
    #     # request = make_request(form={})
    #
    #     project = api.content.create(
    #         container=self.campaign,
    #         type="Project",
    #         id="project",
    #         title="My new project",
    #     )
    #     conversation = IConversation(project)
    #     comment1 = createObject("plone.Comment")
    #     comment1.author_name = "Kamou Lox"
    #     conversation.addComment(comment1)
    #     import transaction
    #     transaction.commit()
    #     # # commentForm = getMultiAdapter(
    #     # #     (project, request),
    #     # #     name="comment-form",
    #     # # )
    #     # # commentForm.update()
    #     # data, errors = commentForm.extractData()
    #     # import pdb;
    #     # pdb.set_trace()
    #     # commentForm.get_author(data)
    #     # import pdb;pdb.set_trace()
    #     alsoProvides(self.request, IFormLayer)
    #     view = queryMultiAdapter((project, self.request), name="view")
    #     print(view())
    #     self.assertIn("Kamou Lox", view())
