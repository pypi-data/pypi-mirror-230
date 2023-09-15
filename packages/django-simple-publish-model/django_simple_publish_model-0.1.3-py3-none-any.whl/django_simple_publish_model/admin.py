from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_fastadmin.admin import ToggleFieldStateAdmin

class SimplePublishModelAdmin(ToggleFieldStateAdmin, admin.ModelAdmin):

    published_field_name = "published"

    toggle_publish_state_button_title_turn_on = _("Publish")
    toggle_publish_state_button_title_turn_off = _("Unpublish")
    toggle_publish_state_button_icon_state_on = "fa fa-eye-slash"
    toggle_publish_state_button_icon_state_off = "fa fa-eye"
    toggle_publish_state_button_help_text = _("Toggle item publish state.")

    def get_toggle_field_state_configs(self):
        configs = super().get_toggle_field_state_configs()
        configs[self.published_field_name] = {
            "toggle_button_title_turn_on": self.toggle_publish_state_button_title_turn_on,
            "toggle_button_title_turn_off": self.toggle_publish_state_button_title_turn_off,
            "toggle_button_icon_state_on": self.toggle_publish_state_button_icon_state_on,
            "toggle_button_icon_state_off": self.toggle_publish_state_button_icon_state_off,
            "toggle_button_help_text": self.toggle_publish_state_button_help_text,
        }
        return configs

    toggle_publish_state_button = ToggleFieldStateAdmin.make_toggle_field_state_button("published_field_name")
