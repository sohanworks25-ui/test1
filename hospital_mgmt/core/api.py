from rest_framework import routers, viewsets

from .models import OPDBill, PathologyBill, Patient
from .serializers import OPDBillSerializer, PathologyBillSerializer, PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer


class OPDBillViewSet(viewsets.ModelViewSet):
    queryset = OPDBill.objects.all().order_by("-billing_date")
    serializer_class = OPDBillSerializer


class PathologyBillViewSet(viewsets.ModelViewSet):
    queryset = PathologyBill.objects.all().order_by("-billing_date")
    serializer_class = PathologyBillSerializer


router = routers.DefaultRouter()
router.register(r"patients", PatientViewSet)
router.register(r"opd-bills", OPDBillViewSet)
router.register(r"pathology-bills", PathologyBillViewSet)
