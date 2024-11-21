from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return f"{self.username}"

class Address(models.Model):
    HOME = "home"
    OFFICE = "office"
    SHOP = "shop"
    OTHER = "other"

    ADDRESS_TYPES = [
        (HOME, "Home"),
        (OFFICE, "Office"),
        (SHOP, "Shop"),
        (OTHER, "Other"),
    ]

    user = models.ForeignKey(CustomUser, related_name="addresses", on_delete=models.CASCADE)
    receiver_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)  # Receiver's phone number
    alternate_phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional alternate number
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default=HOME)
    is_default = models.BooleanField(default=False)  # Mark if it's the default address

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.address_type.capitalize()} - {self.address_line_1}, {self.city}"
