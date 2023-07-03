from django.shortcuts import render

def vprofile(request):
    context = {}
    return render(request, 'vendor/vprofile.html', context)