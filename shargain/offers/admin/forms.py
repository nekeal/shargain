from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from shargain.offers.models import ScrappingTarget, TargetAccess


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


class TargetAccessForm(ModelForm):
    class Meta:
        model = TargetAccess
        fields = "__all__"  # noqa: DJ007

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        user = cleaned_data.get("user")
        target = cleaned_data.get("target") or getattr(self.instance, "target", None)
        if target and user and target.owner_id == user.id:
            raise ValidationError({"user": _("Target owner cannot be added to target access.")})
        return cleaned_data
