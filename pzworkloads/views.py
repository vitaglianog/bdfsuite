from django.shortcuts import render
from django.http import HttpResponse
from .forms import DataSourceForm, ParameterForm
import palimpzest as pz
from .schemas import CaseData, ScientificPaper, Reference
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import shutil

def index(request):
    if request.method == 'POST':
        data_source_form = DataSourceForm(request.POST)
        parameter_form = ParameterForm(request.POST)
        if data_source_form.is_valid() and parameter_form.is_valid():
            data_source = data_source_form.cleaned_data['data_source']
            policy = parameter_form.cleaned_data['policy']
            execution_engine = parameter_form.cleaned_data['execution_engine']
            result = None
        else:
            result = "Invalid input"
    else:
        data_source_form = DataSourceForm()
        parameter_form = ParameterForm()
        result = None

    return render(request, 'pzworkloads/index.html', {
        'data_source_form': data_source_form,
        'parameter_form': parameter_form,
        'result': result,
    })

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        # move the file into the 'cache/dataset/' folder
        with open(f'cache/dataset/{uploaded_file.name}', 'wb') as f:
            shutil.copyfileobj(uploaded_file, f)
        # Process the file as needed
        return JsonResponse({'message': 'File uploaded successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
