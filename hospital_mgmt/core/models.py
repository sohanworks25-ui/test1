from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone


class Role(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    ADMIN = "admin", "Admin"
    RECEPTIONIST = "receptionist", "Receptionist"
    DOCTOR = "doctor", "Doctor"
    NURSE = "nurse", "Nurse"
    PATHOLOGIST = "pathologist", "Pathologist"
    PHARMACIST = "pharmacist", "Pharmacist"


class User(AbstractUser):
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.RECEPTIONIST)

    def is_super_admin(self) -> bool:
        return self.role == Role.SUPER_ADMIN


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commission_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username}"


class Patient(models.Model):
    SEX_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]

    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    mobile_number = models.CharField(max_length=20)
    refer_doctor = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referred_patients",
    )
    consultant_doctor = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consulted_patients",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.mobile_number})"


class OPDItem(models.Model):
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class PathologyTest(models.Model):
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class InvoiceSequence(models.Model):
    year_month = models.CharField(max_length=6, unique=True)
    last_value = models.PositiveIntegerField(default=0)

    @classmethod
    def next_invoice(cls, invoice_date: date | None = None) -> str:
        invoice_date = invoice_date or timezone.now().date()
        year_month = invoice_date.strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(year_month=year_month)
            sequence.last_value += 1
            sequence.save(update_fields=["last_value"])
        return f"{year_month}-{sequence.last_value:04d}"


class BillingBase(models.Model):
    invoice_number = models.CharField(max_length=16, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, default="due")
    billing_date = models.DateField(default=timezone.now)

    class Meta:
        abstract = True

    def calculate_totals(self, subtotal: Decimal) -> None:
        self.subtotal = subtotal
        self.total_amount = max(subtotal - self.discount, Decimal("0"))
        self.due_amount = max(self.total_amount - self.paid_amount, Decimal("0"))
        if self.due_amount == 0:
            self.payment_status = "paid"
        elif self.paid_amount > 0:
            self.payment_status = "partial"
        else:
            self.payment_status = "due"


class OPDBill(BillingBase):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="opd_bills")

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = InvoiceSequence.next_invoice(self.billing_date)
        subtotal = sum(item.line_total for item in self.items.all()) if self.pk else Decimal("0")
        self.calculate_totals(subtotal)
        super().save(*args, **kwargs)


class OPDLineItem(models.Model):
    bill = models.ForeignKey(OPDBill, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(OPDItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        return self.item.name


class PathologyBill(BillingBase):
    pathologist = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="pathology_bills")

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = InvoiceSequence.next_invoice(self.billing_date)
        subtotal = sum(item.line_total for item in self.items.all()) if self.pk else Decimal("0")
        self.calculate_totals(subtotal)
        super().save(*args, **kwargs)


class PathologyLineItem(models.Model):
    bill = models.ForeignKey(PathologyBill, on_delete=models.CASCADE, related_name="items")
    test = models.ForeignKey(PathologyTest, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        return self.test.name


class PathologyReport(models.Model):
    bill = models.ForeignKey(PathologyBill, on_delete=models.CASCADE, related_name="reports")
    report_file = models.FileField(upload_to="pathology_reports/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CommissionRecord(models.Model):
    ROLE_CHOICES = [("doctor", "Doctor"), ("pharmacist", "Pharmacist"), ("pathologist", "Pathologist")]

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bill_reference = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.staff} - {self.amount}"
