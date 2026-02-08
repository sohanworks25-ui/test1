from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from hospital_mgmt.core.models import Department, OPDItem, PathologyTest, StaffProfile


class Command(BaseCommand):
    help = "Seed sample hospital data"

    def handle(self, *args, **options):
        user_model = get_user_model()
        super_admin, _ = user_model.objects.get_or_create(
            username="superadmin",
            defaults={"role": "super_admin", "is_staff": True, "is_superuser": True},
        )
        if not super_admin.password:
            super_admin.set_password("admin123")
            super_admin.save()

        cardiology, _ = Department.objects.get_or_create(name="Cardiology")
        pathology, _ = Department.objects.get_or_create(name="Pathology")

        doctor_user, _ = user_model.objects.get_or_create(username="dr_smith", defaults={"role": "doctor"})
        StaffProfile.objects.get_or_create(user=doctor_user, defaults={"department": cardiology})

        path_user, _ = user_model.objects.get_or_create(username="dr_path", defaults={"role": "pathologist"})
        StaffProfile.objects.get_or_create(user=path_user, defaults={"department": pathology})

        OPDItem.objects.get_or_create(name="General Consultation", defaults={"price": 500})
        OPDItem.objects.get_or_create(name="Follow-up Consultation", defaults={"price": 300})
        PathologyTest.objects.get_or_create(name="CBC", defaults={"price": 650})
        PathologyTest.objects.get_or_create(name="X-Ray", defaults={"price": 800})

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
