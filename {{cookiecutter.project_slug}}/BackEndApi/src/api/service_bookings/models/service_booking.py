from django.conf import settings
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True, default='')
    duration = models.CharField(max_length=80, blank=True, default='')
    price_label = models.CharField(max_length=80, blank=True, default='')
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    quote = models.TextField()
    author_name = models.CharField(max_length=140, blank=True, default='')
    author_role = models.CharField(max_length=140, blank=True, default='')
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return self.author_name or f'Testimonial {self.pk}'


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        REJECTED = 'rejected', 'Rejected'

    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, default='')
    transaction_code = models.CharField(max_length=120, blank=True, default='')
    verification_file = models.FileField(upload_to='booking_verifications/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_bookings',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} - {self.service.name} ({self.date} {self.time})'
