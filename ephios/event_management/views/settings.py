from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView
from dynamic_preferences.forms import global_preference_form_builder


class GeneralSettingsView(UserPassesTestMixin, SuccessMessageMixin, FormView):
    form_class = global_preference_form_builder()
    template_name = "event_management/settings/general.html"
    success_message = _("Settings successfully saved.")

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.update_preferences()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("event_management:settings_general")