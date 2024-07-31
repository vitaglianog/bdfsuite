from django.shortcuts import render
from django.http import HttpResponse
from .forms import DataSourceForm, ParameterForm
import palimpzest as pz
from .schemas import CaseData, ScientificPaper, Reference

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
