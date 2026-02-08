from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    CommissionRecord,
    Department,
    OPDBill,
    OPDItem,
    OPDLineItem,
    PathologyBill,
    PathologyLineItem,
    PathologyReport,
    PathologyTest,
    Patient,
    StaffProfile,
    User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")


admin.site.register(Department)
admin.site.register(StaffProfile)
admin.site.register(Patient)
admin.site.register(OPDItem)
admin.site.register(PathologyTest)
admin.site.register(OPDBill)
admin.site.register(OPDLineItem)
admin.site.register(PathologyBill)
admin.site.register(PathologyLineItem)
admin.site.register(PathologyReport)
admin.site.register(CommissionRecord)
