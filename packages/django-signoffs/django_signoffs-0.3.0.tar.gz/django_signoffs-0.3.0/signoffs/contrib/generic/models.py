"""
    Signoff models with Generic Model relations

    # EXPERIMENTAL - unsupported
    # TODO: fields.SignoffSet will require special case for GenericModelSignet,
            which will need a GenericRelation to provide manager to do reverse lookup
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from signoffs.models import AbstractApprovalStamp, AbstractSignet


class GenericModelSignet(AbstractSignet):
    """A Signet with a generic relation to any model"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta(AbstractSignet.Meta):
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class GenericModelApprovalStamp(AbstractApprovalStamp):
    """A Stamp of Approval with a generic relation to any model"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
