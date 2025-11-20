from django import forms
from .models import LarTemporario , LarTemporarioAtual
from gatos.models import Gato
from adocoes.models import Adotados

SIM_NAO_CHOICES = [
    (True, "Sim"),
    (False, "Não"),
]

SIM_NAO_PARCIALMENTE_CHOICES = [
    ('sim', "Sim"),
    ('nao', "Não"),
    ('parcialmente', "Parcialmente"),
]

POSSO_AJUDAR_CHOICES = [
    ('sim', "Posso ajudar com os custos"),
    ('nao', "Prefiro receber os suprimentos"),
    ('parcialmente', "Posso ajudar parcialmente"),
]

TEMPO_CHOICES = [
    ('um', "Até 1 mês"),
    ('tres', "1-3 meses"),
    ('seis', "3-6 meses"),
    ('indefinido', "tempo indefinido"),
]

VISITA_CHOICES = [
    (True, "Sim"),
    (False, "Prefiro que vocês recolham o animal temporariamente para apresentar ao adotante"),
]


class LarTemporarioForm(forms.ModelForm):
    class Meta:
        model = LarTemporario
        fields = "__all__"  # inclui todos os campos do model

        widgets = {
            # ---------------- BOOLEANOS (Sim / Não) ----------------
            'foi_lar_temporario': forms.RadioSelect(choices=SIM_NAO_CHOICES),
            'mora_casa': forms.RadioSelect(choices=SIM_NAO_CHOICES),
            'restrito': forms.RadioSelect(choices=SIM_NAO_CHOICES),

            # ------------- BOOLEANOS (Sim / Não / Parcialmente) ------------
            'estrutura': forms.RadioSelect(choices=SIM_NAO_PARCIALMENTE_CHOICES),

            # ------------------ BOOLEANOS (Custos) -----------------
            'custos': forms.RadioSelect(choices=POSSO_AJUDAR_CHOICES),

            # ------------------ BOOLEANOS (Tempo) -----------------
            'duracao_aproximada': forms.RadioSelect(choices=TEMPO_CHOICES),

            # ----------------- BOOLEANOS (Visita) -----------------
            'visita': forms.RadioSelect(choices=VISITA_CHOICES),

            # -------- Data --------
            'disponibilidade_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            # -------- Campos de texto --------
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ocupacao_profissional': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11999998888'}),

            # -------- Numérico --------
            'cep': forms.NumberInput(attrs={'class': 'form-control'}),

            # -------- TextArea --------
            'animal_externo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'informacao_adicional': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_numero_contato(self):
        num = self.cleaned_data.get('numero_contato', '')
        only_digits = ''.join(c for c in num if c.isdigit())
        if len(only_digits) < 10:
            raise forms.ValidationError("Número de contato inválido. Informe DDD + número.")
        return only_digits
    

class LarTemporarioAtualForm(forms.ModelForm):
    class Meta:
        model = LarTemporarioAtual
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Gatos já adotados
        adotados_ids = Adotados.objects.values_list("gato_id", flat=True)

        # Gatos já em lar temporário atual
        em_lar_ids = LarTemporarioAtual.objects.values_list("gato_id", flat=True)

        # Filtra o select
        self.fields["gato"].queryset = (
            Gato.objects.exclude(id__in=adotados_ids)
                        .exclude(id__in=em_lar_ids)
        )