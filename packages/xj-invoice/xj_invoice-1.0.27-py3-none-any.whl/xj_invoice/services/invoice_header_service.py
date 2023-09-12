import sys
import time
import os
import datetime

from ..models import *
from django.db.models import Q, F


class InvoiceHeaderService:

    @staticmethod
    def list(params):

        user_id = params.pop("user_id", "")
        sort = params.pop("sort", "-id")
        sort = sort if sort and sort in ["-id", "-sort", "id", "sort"] else "-id"

        currencies = InvoiceHeader.objects.filter(user_id=user_id, is_delete=0).order_by(
            sort)

        return list(currencies.values('head_type', 'company_name', 'tax_number', 'address', 'phone_number',
                                      'account_opening_bank',
                                      'account', 'sort')), None

    @staticmethod
    def edit(params):
        invoice_header_id = params.get('invoice_header_id', '')
        tax_number = params.get('tax_number', '')
        invoice_header_set = InvoiceHeader.objects.filter(Q(tax_number=tax_number) & ~Q(id=invoice_header_id))
        if invoice_header_set.first():
            return None, "税号已存在"
        try:
            params.pop("invoice_header_id")
            InvoiceHeader.objects.filter(id=invoice_header_id).update(**params)
            return None, None
        except Exception as e:
            return None, "参数配置错误：" + str(e)

    @staticmethod
    def delete(params):
        invoice_header_id = params.get('invoice_header_id', '')
        try:
            InvoiceHeader.objects.filter(id=invoice_header_id).update(**{"is_delete": 1})
            return None, None
        except Exception as e:
            return None, "参数配置错误：" + str(e)

    @staticmethod
    def add(params):
        tax_number = params.get('tax_number', '')
        if tax_number:
            invoice_header_set = InvoiceHeader.objects.filter(tax_number=tax_number).first()
            if invoice_header_set is not None:
                return None, "税号已存在"
        try:
            InvoiceHeader.objects.create(**params)
            return None, None
        except Exception as e:
            return None, "参数配置错误：" + str(e)
