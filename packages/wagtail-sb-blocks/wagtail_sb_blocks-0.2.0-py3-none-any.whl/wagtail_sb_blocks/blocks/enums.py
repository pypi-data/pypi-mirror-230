from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EmbedRatio(TextChoices):
    RATIO_16_9 = "ratio-16-9", "16:9"
    RATIO_4_3 = "ratio-4-3", "4:3"

    __empty__ = _("Without ratio")


class ButtonSize(TextChoices):
    SMALL = "small", _("Small")
    LARGE = "large", _("Large")

    __empty__ = _("Normal")
