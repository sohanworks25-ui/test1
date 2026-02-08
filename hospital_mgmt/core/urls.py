from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api, views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("patients/new/", views.register_patient, name="patient-new"),
    path("billing/opd/new/", views.create_opd_bill, name="opd-bill-new"),
    path("billing/opd/<int:bill_id>/invoice/", views.opd_invoice_pdf, name="opd-invoice"),
    path("billing/pathology/new/", views.create_pathology_bill, name="pathology-bill-new"),
    path("billing/pathology/<int:bill_id>/invoice/", views.pathology_invoice_pdf, name="pathology-invoice"),
    path("api/", include(api.router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
