from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Doc

# Create your views here.
def index(response):
    return render(response, 'main/index.html')

def upload(request):

    if request.method == 'POST':
        my_file = request.FILES.get('file')
        Doc.objects.create(file=my_file)
        return HttpResponse('')

    return JsonResponse({'post': 'false'})
