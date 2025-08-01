from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from telebot.apihelper import ApiTelegramException

from shargain.notifications.models import NotificationConfig
from shargain.notifications.senders import TelegramNotificationSender


@method_decorator(staff_member_required, name="dispatch")
class SendTestNotificationView(View):
    def get_redirect_url(self):
        return self.request.headers.get("referer", "admin:index")

    @staticmethod
    def send_notification(config: NotificationConfig):
        return TelegramNotificationSender(config).send("Test notification")

    def post(self, request, *args, **kwargs):
        # sourcery skip: use-fstring-for-formatting
        config = get_object_or_404(NotificationConfig, pk=kwargs["object_id"])
        try:
            self.send_notification(config)
        except ApiTelegramException as e:
            messages.error(request, _("Error sending test notification: {}").format(e))
        else:
            messages.success(request, _("Test notification sent successfully"))
        return redirect(self.get_redirect_url())
