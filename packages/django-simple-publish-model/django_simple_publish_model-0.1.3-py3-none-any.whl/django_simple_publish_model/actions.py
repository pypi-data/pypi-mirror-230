from django.utils.translation import ugettext as _
from django.utils.translation import ngettext
from django.contrib import messages

def publish_selected_items(modeladmin, request, queryset):
    published = 0
    for item in queryset.all():
        if not item.is_published():
            published += 1 
            item.do_publish(save=True)
    modeladmin.message_user(request, ngettext(
            '%d item was successfully marked as published.',
            '%d items were successfully marked as published.',
            published,
        ) % published, messages.SUCCESS)
publish_selected_items.short_description = _("Publish Selected Items")


def unpublish_selected_items(modeladmin, request, queryset):
    unpublished = 0
    for item in queryset.all():
        if item.is_published():
            unpublished += 1
            item.do_unpublish(save=True)
    modeladmin.message_user(request, ngettext(
            '%d item was successfully marked as unpublished.',
            '%d items were successfully marked as unpublished.',
            unpublished,
        ) % unpublished, messages.SUCCESS)

unpublish_selected_items.short_description = _("Unpublish Selected Items")
