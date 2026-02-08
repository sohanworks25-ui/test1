from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import OPDBillForm, PatientForm, PathologyBillForm
from .models import OPDBill, PathologyBill, Patient


@login_required
def dashboard(request):
    return render(
        request,
        "core/dashboard.html",
        {
            "patient_count": Patient.objects.count(),
            "opd_count": OPDBill.objects.count(),
            "pathology_count": PathologyBill.objects.count(),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def register_patient(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard")
    return render(request, "core/patient_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def create_opd_bill(request):
    form = OPDBillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        bill = form.save(commit=False)
        bill.created_by = request.user
        bill.save()
        return redirect("dashboard")
    return render(request, "core/opd_bill_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def create_pathology_bill(request):
    form = PathologyBillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        bill = form.save(commit=False)
        bill.created_by = request.user
        bill.save()
        return redirect("dashboard")
    return render(request, "core/pathology_bill_form.html", {"form": form})


def _render_bill_pdf(title: str, bill, items):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 760, title)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 740, f"Invoice: {bill.invoice_number}")
    pdf.drawString(50, 725, f"Patient: {bill.patient.name}")
    pdf.drawString(50, 710, f"Billing Date: {bill.billing_date}")
    pdf.drawString(50, 695, f"Payment Status: {bill.payment_status}")
    y = 670
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Item")
    pdf.drawString(300, y, "Qty")
    pdf.drawString(350, y, "Unit Price")
    pdf.drawString(450, y, "Total")
    pdf.setFont("Helvetica", 10)
    y -= 20
    for line in items:
        pdf.drawString(50, y, str(line))
        pdf.drawString(300, y, str(line.quantity))
        pdf.drawString(350, y, f\"{line.unit_price}\")
        pdf.drawString(450, y, f\"{line.line_total}\")
        y -= 18
        if y < 100:
            pdf.showPage()
            y = 760
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(350, y - 20, "Subtotal:")
    pdf.drawString(450, y - 20, f\"{bill.subtotal}\")
    pdf.drawString(350, y - 35, "Discount:")
    pdf.drawString(450, y - 35, f\"{bill.discount}\")
    pdf.drawString(350, y - 50, "Total:")
    pdf.drawString(450, y - 50, f\"{bill.total_amount}\")
    pdf.drawString(350, y - 65, "Paid:")
    pdf.drawString(450, y - 65, f\"{bill.paid_amount}\")
    pdf.drawString(350, y - 80, "Due:")
    pdf.drawString(450, y - 80, f\"{bill.due_amount}\")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


@login_required
def opd_invoice_pdf(request, bill_id: int):
    bill = get_object_or_404(OPDBill, pk=bill_id)
    buffer = _render_bill_pdf("OPD Invoice", bill, bill.items.select_related(\"item\"))
    return FileResponse(buffer, as_attachment=True, filename=f\"{bill.invoice_number}.pdf\")


@login_required
def pathology_invoice_pdf(request, bill_id: int):
    bill = get_object_or_404(PathologyBill, pk=bill_id)
    buffer = _render_bill_pdf(\"Pathology Invoice\", bill, bill.items.select_related(\"test\"))
    return FileResponse(buffer, as_attachment=True, filename=f\"{bill.invoice_number}.pdf\")
