from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from shargain.offers.models import ScrappingTarget


class ScrappingTargetAdminForm(ModelForm):
    class Meta:
        model = ScrappingTarget
        fields = "__all__"  # noqa: DJ007

    def clean_notification_config(self):
        notification_config = self.cleaned_data["notification_config"]
        if not notification_config:
            return notification_config
        if notification_config.channel != "telegram":
            raise ValidationError(_("Only telegram channel is supported for now"))
        if not notification_config.chatid:
            raise ValidationError(_("You must first register a channel (or specify a chat_id manually)"))
        return notification_config
