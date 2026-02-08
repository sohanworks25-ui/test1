from rest_framework import serializers

from .models import OPDBill, OPDLineItem, PathologyBill, PathologyLineItem, Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class OPDLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OPDLineItem
        fields = ["item", "quantity", "unit_price", "line_total"]


class OPDBillSerializer(serializers.ModelSerializer):
    items = OPDLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = OPDBill
        fields = "__all__"


class PathologyLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathologyLineItem
        fields = ["test", "quantity", "unit_price", "line_total"]


class PathologyBillSerializer(serializers.ModelSerializer):
    items = PathologyLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = PathologyBill
        fields = "__all__"
