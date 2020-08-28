from datetime import datetime, timedelta

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm,
    ModelMultipleChoiceField,
    modelformset_factory,
    Select,
    DateField,
    TimeField,
)
from django.utils.timezone import get_default_timezone, make_aware
from guardian.shortcuts import assign_perm, remove_perm

from event_management.models import Event, Shift
from event_management.signup import register_signup_methods
from jep.widgets import CustomDateInput, CustomTimeInput
from user_management.models import UserProfile


class EventForm(ModelForm):
    visible_for = ModelMultipleChoiceField(queryset=Group.objects.none())
    responsible_persons = ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(), required=False
    )
    responsible_groups = ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = Event
        fields = ["title", "description", "location", "type"]

    def save(self, commit=True):
        event = super().save(commit)
        if "visible_for" in self.changed_data:
            for group in self.cleaned_data["visible_for"]:
                assign_perm("view_event", group, event)
            for group in self.fields["visible_for"].queryset.difference(
                self.cleaned_data["visible_for"]
            ):
                remove_perm("view_event", group, event)
        if "responsible_groups" in self.changed_data:
            for group in self.cleaned_data["responsible_groups"].difference(
                self.initial["responsible_groups"]
            ):
                assign_perm("change_event", group, event)
                assign_perm("view_event", group, event)
            for group in self.initial["responsible_groups"].difference(
                self.cleaned_data["responsible_groups"]
            ):
                remove_perm("change_event", group, event)
                if group not in self.cleaned_data["visible_for"]:
                    remove_perm("view_event", group, event)
        if "responsible_persons" in self.changed_data:
            for user in self.cleaned_data["responsible_persons"].difference(
                self.initial["responsible_persons"]
            ):
                assign_perm("change_event", user, event)
                assign_perm("view_event", user, event)
            for user in self.initial["responsible_persons"].difference(
                self.cleaned_data["responsible_persons"]
            ):
                remove_perm("change_event", user, event)
                remove_perm("view_event", user, event)
        return event


class ShiftForm(ModelForm):
    date = DateField(widget=CustomDateInput(format="%Y-%m-%d"))
    meeting_time = TimeField(widget=CustomTimeInput)
    start_time = TimeField(widget=CustomTimeInput)
    end_time = TimeField(widget=CustomTimeInput)

    field_order = ["date", "meeting_time", "start_time", "end_time", "signup_method_slug"]

    class Meta:
        model = Shift
        fields = ["meeting_time", "start_time", "end_time", "signup_method_slug"]
        widgets = {
            "signup_method_slug": Select(
                choices=(
                    (method.slug, method.verbose_name)
                    for receiver, method in register_signup_methods.send(None)
                )
            )
        }

    def clean(self):
        cleaned_data = super(ShiftForm, self).clean()
        cleaned_data["meeting_time"] = make_aware(
            datetime.combine(cleaned_data["date"], cleaned_data["meeting_time"])
        )
        cleaned_data["start_time"] = make_aware(
            datetime.combine(cleaned_data["date"], cleaned_data["start_time"])
        )
        cleaned_data["end_time"] = make_aware(
            datetime.combine(self.cleaned_data["date"], cleaned_data["end_time"])
        )
        if self.cleaned_data["end_time"] <= self.cleaned_data["start_time"]:
            cleaned_data["end_time"] = cleaned_data["end_time"] + timedelta(days=1)
        if not cleaned_data["meeting_time"] <= cleaned_data["start_time"]:
            raise ValidationError("Meeting time must not be after start time!")
        return cleaned_data