from typing import TYPE_CHECKING

from django.db import models
from django.db.models import ExpressionWrapper
from django.db.models import Q
from django.utils import timezone

if TYPE_CHECKING:
    # prevent cyclic imports
    from lsb.models import Product


class ProductQuerySet(models.QuerySet["Product"]):
    def valid(self):
        return self.filter(
            is_purchased=False,
            is_banned=False,
            is_auth_error=False,
            disabled_until__lt=timezone.now(),
        )


class ProductManager(models.Manager["Product"]):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def valid(self):
        return self.get_queryset().valid()

    def with_is_disabled(self):
        return self.annotate(
            is_disabled=ExpressionWrapper(
                Q(disabled_until__gt=timezone.now()),
                output_field=models.BooleanField(),
            )
        )

    def with_is_old_stock(self, threshold):
        return self.annotate(
            is_old_stock=ExpressionWrapper(
                Q(date_last_played__lte=threshold),
                output_field=models.BooleanField(),
            )
        )

    def with_is_ranked(self):
        return self.annotate(
            is_ranked=ExpressionWrapper(
                ~Q(rank="UNRANKED"),
                output_field=models.BooleanField(),
            )
        )
