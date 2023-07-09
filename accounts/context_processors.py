from vendor.models import Vendor
from django.shortcuts import get_object_or_404

def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor=None

    return dict(vendor=vendor)