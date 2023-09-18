from django.contrib import messages
from django.http import HttpResponseRedirect
from form_action import extra_button
from form_action import form_action

from lsb.exceptions import SkinParseException
from lsb.forms import ProductStatusRemarksForm
from lsb.models import max_datetime
from lsb.models import min_datetime

from .utils.skins import create_or_update_skins


def mark_as_handleveled(modeladmin, request, queryset):
    updated = queryset.update(is_handleveled=True)
    messages.info(request, f"{updated} product(s) marked as handleveled.")


def clear_handleveled(modeladmin, request, queryset):
    updated = queryset.update(is_handleveled=False)
    messages.info(request, f"Cleared handleveled from {updated} product(s).")


@form_action(ProductStatusRemarksForm, description="Mark as disabled")
def mark_as_disabled_with_status(modeladmin, request, queryset, form):
    status = form.cleaned_data["status"]
    remarks = form.cleaned_data["remarks"]

    to_update = {
        "disabled_until": max_datetime,
    }

    if status != "unchanged":
        to_update["status"] = None if status == "" else status
    if remarks != "unchanged":
        to_update["remarks"] = None if remarks == "" else remarks

    updated = queryset.update(**to_update)
    messages.info(
        request,
        (
            f"{updated} product(s) marked as disabled with status {status} and"
            f" remarks {remarks}."
        ),
    )


@form_action(ProductStatusRemarksForm, description="Clear disabled")
def clear_disabled_with_status(modeladmin, request, queryset, form):
    status = form.cleaned_data["status"]
    remarks = form.cleaned_data["remarks"]

    to_update = {
        "disabled_until": min_datetime,
    }

    if status != "unchanged":
        to_update["status"] = None if status == "" else status
    if remarks != "unchanged":
        to_update["remarks"] = None if remarks == "" else remarks

    updated = queryset.update(**to_update)
    messages.info(
        request,
        (
            f"Cleared disabled from {updated} product(s) marked with status"
            f" {status} and remarks {remarks}."
        ),
    )


@extra_button("Update skins")
def update_skins(request):
    try:
        created_count, updated_count = create_or_update_skins()
        messages.success(
            request,
            (
                f"{created_count}(s) skins created. {updated_count}(s) skins"
                " updated."
            ),
        )
        return HttpResponseRedirect("/admin/lsb/skin/")
    except SkinParseException as e:
        messages.error(request, str(e))
        return HttpResponseRedirect("/admin/lsb/skin/")
