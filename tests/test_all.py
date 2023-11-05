"""bw-file-submit tests"""
# pylint: disable=import-error, too-few-public-methods, protected-access, unnecessary-pass

try:
    from unittest import mock
except ImportError:
    try:
        import mock
    except ImportError:
        mock = None

import os
import tempfile

from django import forms
from django.contrib.admin.sites import AdminSite
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase, RequestFactory
from django.views.generic import FormView

from file_resubmit import widgets
from file_resubmit import admin

if not mock:
    raise ImproperlyConfigured("For testing mock is required.")


# shortest possible PNG file, courtesy http://garethrees.org/2007/11/14/pngcrush/
# pylint: disable=line-too-long
PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestForm(forms.Form):
    """form for tests"""

    pass


class OneFileForm(forms.Form):
    """file form for tests"""

    name = forms.CharField(required=True)
    upload_file = forms.FileField(widget=widgets.ResubmitFileWidget())


class OneImageForm(forms.Form):
    """image form for tests"""

    name = forms.CharField(required=True)
    upload_image = forms.ImageField(widget=widgets.ResubmitImageWidget())


class BaseResubmitFileMixin:
    """mixin for testing"""

    factory = RequestFactory()

    with tempfile.NamedTemporaryFile(delete=False) as temporary_file:
        temporary_content = os.urandom(1024)
        temporary_file.write(temporary_content)
        temporary_file.close()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temporary_image:
        temporary_image.write(PNG)
        temporary_image.close()

    def get_resubmit_field(self, form, field_name):
        """get the resubmit value of a field"""
        resubmit_field_name = f"{field_name}_cache_key"
        name_prefix = f'name="{resubmit_field_name}"'
        value_prefix = 'value="'
        rendered = str(form[field_name])
        self.assertIn(name_prefix, rendered)
        name_prefix_idx = rendered.index(name_prefix)
        value_idx = rendered.index(value_prefix, name_prefix_idx)
        value_close_idx = rendered.index('"', value_idx + len(value_prefix))
        value = rendered[value_idx + len(value_prefix) : value_close_idx]
        return resubmit_field_name, value


class TestResubmitFileWidget(BaseResubmitFileMixin, TestCase):
    """test cases for ResubmitFileWidget"""

    class DummyFormView(FormView):
        """A form view to use in tests"""

        template_name = "blank.html"  # TemplateView requires this attribute
        form_class = TestForm
        success_url = "/done/"

    class OneFileView(DummyFormView):
        """view for testing file uploads"""

        form_class = OneFileForm

    class OneImageView(DummyFormView):
        """view for testing image uploads"""

        form_class = OneImageForm

    def test_file_widget(self):
        """does the file widget work normally"""
        request = self.factory.get("/example/")
        response = self.OneFileView.as_view()(request)
        form = response.context_data["form"]
        file_field = form.fields.get("upload_file")
        self.assertIsInstance(file_field.widget, widgets.ResubmitFileWidget)

    def test_file_resubmit(self):
        """does the file widget work when re-submitting"""
        data = {}
        with open(self.temporary_file.name, "rb") as fo:
            request = self.factory.post("/example/", {"upload_file": fo})
        response = self.OneFileView.as_view()(request)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        resubmit_field, resubmit_value = self.get_resubmit_field(form, "upload_file")
        data = {resubmit_field: resubmit_value}
        resubmit_req = self.factory.post("/example/", data)
        resubmit_resp = self.OneFileView.as_view()(resubmit_req)
        form = resubmit_resp.context_data["form"]
        uploaded_file = form.cleaned_data["upload_file"]
        self.assertEqual(uploaded_file.read(), self.temporary_content)

    def test_image_widget(self):
        """does the image widget work normally"""
        request = self.factory.get("/example/")
        response = self.OneImageView.as_view()(request)
        form = response.context_data["form"]
        image_field = form.fields.get("upload_image")
        self.assertIsInstance(image_field.widget, widgets.ResubmitImageWidget)

    def test_image_resubmit(self):
        """does the image widget work when resubmitting"""
        data = {}
        with open(self.temporary_image.name, "rb") as fo:
            request = self.factory.post("/example/", {"upload_image": fo})
        response = self.OneImageView.as_view()(request)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        resubmit_field, resubmit_value = self.get_resubmit_field(form, "upload_image")
        data = {resubmit_field: resubmit_value}
        resubmit_req = self.factory.post("/example/", data)
        resubmit_resp = self.OneImageView.as_view()(resubmit_req)
        form = resubmit_resp.context_data["form"]
        uploaded_image = form.cleaned_data["upload_image"]
        self.assertEqual(uploaded_image.read(), PNG)


class TestModel(models.Model):
    """
    I skip the step of saving the model to the database
    """

    def save_base(self, *args, **kwargs):
        """override save"""
        pass

    class Meta:
        """make it abstract"""

        abstract = True


class TestModelAdmin(ModelAdmin):
    """
    Instead of returning with a redirect to the change
    list page, I just return the saved object
    """

    # pylint: disable=no-self-use
    def response_add(
        self, request, obj, *args, **kwargs
    ):  # pylint: disable=unused-argument
        """return saved object"""
        return obj


class TestResubmitAdminWidget(BaseResubmitFileMixin, TestCase):
    """test cases for Admin idgets"""

    class TestFileModel(TestModel):
        """a model to test files against"""

        admin_name = models.CharField(max_length=100, blank=False)
        admin_upload_file = models.FileField(upload_to="fake/")

    class TestImageModel(TestModel):
        """a model to test images against"""

        admin_name = models.CharField(max_length=100, blank=False)
        admin_upload_image = models.ImageField(upload_to="fake/")

    class TestFileAdmin(admin.AdminResubmitMixin, TestModelAdmin):
        """a model to test admin files against"""

        pass

    class TestImageAdmin(admin.AdminResubmitMixin, TestModelAdmin):
        """a model to test admin images against"""

        pass

    def setUp(self):  # pylint: disable=invalid-name
        """create user for tests"""
        super().setUp()
        User = get_user_model()  # pylint: disable=invalid-name
        self.user = User.objects.create_superuser(
            "TestUser", "testuser@example.com", "12345678"
        )

    def test_file_admin(self):
        """does AdminResubmitFileWidget work"""
        testadmin = self.TestFileAdmin(model=self.TestFileModel, admin_site=AdminSite())
        request = self.factory.get("/admin/example/")
        request.user = self.user
        response = testadmin.add_view(request)
        file_field = response.context_data["adminform"].form.fields.get(
            "admin_upload_file"
        )
        self.assertIsInstance(file_field.widget, admin.ResubmitFileWidget)

    def test_image_admin(self):
        """does AdminResubmitImageWidget work"""
        testadmin = self.TestImageAdmin(
            model=self.TestImageModel, admin_site=AdminSite()
        )
        request = self.factory.get("/admin/example/")
        request.user = self.user
        response = testadmin.add_view(request)
        image_field = response.context_data["adminform"].form.fields.get(
            "admin_upload_image"
        )
        self.assertIsInstance(image_field.widget, admin.AdminResubmitImageWidget)

    def test_image_resubmit_admin(self):
        """test submitting image in admin views"""
        testadmin = self.TestImageAdmin(
            model=self.TestImageModel, admin_site=AdminSite()
        )
        with open(self.temporary_image.name, "rb") as fo:
            request = self.factory.post("/admin/example/", {"admin_upload_image": fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data["adminform"].form
        resubmit_field, resubmit_value = self.get_resubmit_field(
            form, "admin_upload_image"
        )
        data = {resubmit_field: resubmit_value}
        resubmit_req = self.factory.post("/admin/example/", data)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        resubmit_resp = testadmin.add_view(resubmit_req)
        form = resubmit_resp.context_data["adminform"].form
        self.assertEqual(len(form.errors), 1)
        uploaded_image = form.cleaned_data["admin_upload_image"]
        self.assertEqual(uploaded_image.read(), PNG)

    def test_file_resubmit_admin(self):
        """test submitting file in admin views"""
        testadmin = self.TestFileAdmin(model=self.TestFileModel, admin_site=AdminSite())
        with open(self.temporary_file.name, "rb") as fo:
            request = self.factory.post("/admin/example/", {"admin_upload_file": fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data["adminform"].form
        resubmit_field, resubmit_value = self.get_resubmit_field(
            form, "admin_upload_file"
        )
        data = {resubmit_field: resubmit_value}
        resubmit_req = self.factory.post("/admin/example/", data)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        resubmit_resp = testadmin.add_view(resubmit_req)
        form = resubmit_resp.context_data["adminform"].form
        print("\n".join(str(err) for err in form.errors.items()))
        self.assertEqual(len(form.errors), 1)
        uploaded_file = form.cleaned_data["admin_upload_file"]
        self.assertEqual(uploaded_file.read(), self.temporary_content)

    def test_image_resubmit_save_admin(self):
        """test resubmitting image in admin views"""
        testadmin = self.TestImageAdmin(
            model=self.TestImageModel, admin_site=AdminSite()
        )
        with open(self.temporary_image.name, "rb") as fo:
            request = self.factory.post("/admin/example/", {"admin_upload_image": fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data["adminform"].form
        resubmit_field, resubmit_value = self.get_resubmit_field(
            form, "admin_upload_image"
        )
        data = {"admin_name": "Sample", resubmit_field: resubmit_value}
        resubmit_req = self.factory.post("/admin/example/", data)
        setattr(resubmit_req, "session", "session")
        messages = FallbackStorage(resubmit_req)
        setattr(resubmit_req, "_messages", messages)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        saved_obj = testadmin.add_view(resubmit_req)  # <=== BUG here
        self.assertEqual(saved_obj.admin_upload_image.read(), PNG)
        self.assertEqual(1, 1)

    def test_file_resubmit_save_admin(self):
        """test resubmitting file in admin views"""
        testadmin = self.TestFileAdmin(model=self.TestFileModel, admin_site=AdminSite())
        with open(self.temporary_file.name, "rb") as fo:
            request = self.factory.post("/admin/example/", {"admin_upload_file": fo})
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = testadmin.add_view(request)
        form = response.context_data["adminform"].form
        resubmit_field, resubmit_value = self.get_resubmit_field(
            form, "admin_upload_file"
        )
        data = {"admin_name": "Sample", resubmit_field: resubmit_value}
        resubmit_req = self.factory.post("/admin/example/", data)
        setattr(resubmit_req, "session", "session")
        messages = FallbackStorage(resubmit_req)
        setattr(resubmit_req, "_messages", messages)
        resubmit_req.user = self.user
        resubmit_req._dont_enforce_csrf_checks = True
        saved_obj = testadmin.add_view(resubmit_req)  # <=== BUG here
        self.assertEqual(saved_obj.admin_upload_file.read(), self.temporary_content)
        self.assertEqual(1, 1)
