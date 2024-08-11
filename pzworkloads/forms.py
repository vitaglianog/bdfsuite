from django import forms

class DataSourceForm(forms.Form):
    DATA_SOURCES = [
        ('reference', 'Reference Extraction'),
        ('collection', 'Supplemental data extraction'),
        ('casedata', 'Medical Schema Matching'),
    ]
    data_source = forms.ChoiceField(
        choices=DATA_SOURCES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

class ParameterForm(forms.Form):
    POLICIES = [
        ('mincost', 'Minimize Cost'),
        ('maxquality', 'Maximize Quality'),
    ]
    policy = forms.ChoiceField(
        choices=POLICIES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    EXECUTION_ENGINES = [
        ('streaming', 'Streaming Execution'),
        ('nosentinel', 'No Sentinel Execution'),
        ('sequential', 'Sequential Execution'),
        ('parallel', 'Parallel Execution'),
    ]
    execution_engine = forms.ChoiceField(
        choices=EXECUTION_ENGINES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )