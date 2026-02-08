# Database Schema Notes

## Core Entities

- **User**: Extends Django user with a role field for RBAC.
- **Department**: Hospital departments.
- **StaffProfile**: Staff attributes, department assignment, commission configuration.
- **Patient**: Required demographics and referring/consulting doctors.
- **OPDItem** and **PathologyTest**: Billable items.
- **OPDBill** and **PathologyBill**: Billing headers with invoice sequence and payment status.
- **OPDLineItem** and **PathologyLineItem**: Bill line items.
- **PathologyReport**: File uploads linked to pathology bills.
- **CommissionRecord**: Tracks commission earnings across roles.

## Invoice Format

Invoices use `YYYYMM-XXXX` with monthly auto-incrementing sequences.
