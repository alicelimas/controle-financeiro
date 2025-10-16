from django import forms
from .models import Gasto, Categoria

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descrição', 'categoria', 'valor', 'recorrência', 'data_gasto']
        widgets = {
            'descrição': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Supermercado'}),
            'categoria': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex.: 100.00'}),
            'recorrência': forms.Select(attrs={'class': 'form-select'}),
            'data_gasto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = "Selecione uma categoria"

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return valor
    
    def clean_descrição(self):
        descrição = self.cleaned_data['descrição']
        if len(descrição) < 3:
            raise forms.ValidationError("A descrição deve ter pelo menos 3 caracteres.")
        return descrição

    def clean_data_gasto(self):
        data_gasto = self.cleaned_data['data_gasto']
        from datetime import date
        if data_gasto > date.today():
            raise forms.ValidationError("A data não pode ser no futuro.")
        return data_gasto