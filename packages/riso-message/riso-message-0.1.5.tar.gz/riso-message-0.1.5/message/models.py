from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import CASCADE, BooleanField, CharField, ForeignKey, PositiveIntegerField, TextField
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

User = get_user_model()


class Notification(TimeStampedModel):
    title = CharField(_("Title"), max_length=255, blank=True, null=True)
    message = TextField(_("Message"), blank=True, null=True)

    to_user = ForeignKey(User, verbose_name=_("Receiver"), related_name="notifications", on_delete=CASCADE)

    is_read = BooleanField(_("Is read"), default=False)

    # for generic relation
    content_type = ForeignKey(
        ContentType, verbose_name=_("Notification from"), related_name="notifications", on_delete=CASCADE
    )
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        db_table = "message_notification"

    def __str__(self):
        return f"{self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        self.is_read = False
        self.save()

    @property
    def get_object_absolute_url(self):
        try:
            return self.content_object.get_absolute_url()
        except AttributeError:
            return ""
