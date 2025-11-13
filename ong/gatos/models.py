from django.db import models
from django.utils.functional import cached_property
from datetime import date

class Temperamento(models.Model):
    docil = models.BooleanField(default=False, verbose_name="Dócil")
    agressivo = models.BooleanField(default=False, verbose_name="Agressivo")
    calmo = models.BooleanField(default=False, verbose_name="Calmo")
    brincalhao = models.BooleanField(default=False, verbose_name="Brincalhão")
    arisco = models.BooleanField(default=False, verbose_name="Arisco")
    independente = models.BooleanField(default=False, verbose_name="Independente")
    carente = models.BooleanField(default=False, verbose_name="Carente")
    
    class Meta:
        verbose_name = "Temperamento"
        verbose_name_plural = "Temperamentos"
        db_table = "temperamento"
    
    def __str__(self):
        caracteristicas = []
        if self.docil:
            caracteristicas.append("Dócil")
        if self.agressivo:
            caracteristicas.append("Agressivo")
        if self.calmo:
            caracteristicas.append("Calmo")
        if self.brincalhao:
            caracteristicas.append("Brincalhão")
        if self.arisco:
            caracteristicas.append("Arisco")
        if self.independente:
            caracteristicas.append("Independente")
        if self.carente:
            caracteristicas.append("Carente")
        return ", ".join(caracteristicas)

class Sociavel(models.Model):
    gatos = models.BooleanField(default=False, verbose_name="gatos")
    desconhecidos = models.BooleanField(default=False, verbose_name="desconhecidos")
    cachorros = models.BooleanField(default=False, verbose_name="cachorros")
    criancas = models.BooleanField(default=False, verbose_name="crianças")
    nao_sociavel = models.BooleanField(default=False, verbose_name="Não sociável")
    
    class Meta:
        verbose_name = "Socialização"
        verbose_name_plural = "Socializações"
        db_table = "sociavel"
    
    def __str__(self):
        caracteristicas = []
        if self.gatos:
            caracteristicas.append("Gatos")
        if self.desconhecidos:
            caracteristicas.append("Desconhecidos")
        if self.cachorros:
            caracteristicas.append("Cachorros")
        if self.criancas:
            caracteristicas.append("Crianças")
        if self.nao_sociavel:
            caracteristicas.append("Não sociável")
        return ", ".join(caracteristicas)

class Cuidado(models.Model):
    castrado = models.BooleanField(default=False, verbose_name='Castrado')
    vacinado = models.BooleanField(default=False, verbose_name="Vacinado")
    vermifugado = models.BooleanField(default=False, verbose_name="Vermifugado")
    cuidado_especial = models.BooleanField(default=False, verbose_name="Cuidado especial")
    fiv_negativo = models.BooleanField(default=False, verbose_name="FIV negativo")
    fiv_positivo = models.BooleanField(default=False, verbose_name="FIV positivo")
    felv_negativo = models.BooleanField(default=False, verbose_name="FeLV negativo")
    felv_positivo = models.BooleanField(default=False, verbose_name="FeLV positivo")
    
    class Meta:
        verbose_name = "Cuidado"
        verbose_name_plural = "Cuidados"
        db_table = "cuidado"
    
    def __str__(self):
        status = []
        if self.castrado:
            status.append("Castrado")
        if self.vacinado:
            status.append("Vacinado")
        if self.vermifugado:
            status.append("Vermifugado")
        if self.cuidado_especial:
            status.append("Cuidado especial")
        if self.fiv_negativo:
            status.append("FIV-")
        if self.fiv_positivo:
            status.append("FIV+")
        if self.felv_negativo:
            status.append("FeLV-")
        if self.felv_positivo:
            status.append("FeLV+")
        return ", ".join(status)
    
class Moradia(models.Model):
    casa_com_quintal = models.BooleanField(default=False, verbose_name="Casa com quintal")
    apartamento = models.BooleanField(default=False, verbose_name="Apartamento")
    
    class Meta:
        verbose_name = "Moradia"
        verbose_name_plural = "Moradias"
        db_table = "moradia"
    
    def __str__(self):
        tipos = []
        if self.casa_com_quintal:
            tipos.append("Casa com quintal")
        if self.apartamento:
            tipos.append("Apartamento")
        return ", ".join(tipos)

class Gato(models.Model):
    SEXO_CHOICES = [
        ("M", "Macho"),
        ("F", "Fêmea"),
    ]
    
    nome = models.CharField(max_length=100, verbose_name="Nome do gato")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo", blank=False, null=False)
    data_nascimento = models.DateField(verbose_name="Data de nascimento")
    descricao = models.TextField(max_length=10000, verbose_name="Sobre o gato")
    imagem = models.ImageField(upload_to="gatos/", verbose_name="Foto do gato")
    lar_temporario = models.BooleanField(default=False, verbose_name="Precisa de lar temporário")
    
    # Relacionamentos
    cuidado = models.ForeignKey(Cuidado, on_delete=models.CASCADE, verbose_name="Cuidados")
    temperamento = models.ForeignKey(Temperamento, on_delete=models.CASCADE, verbose_name="Temperamento")
    sociavel = models.ForeignKey(Sociavel, on_delete=models.CASCADE, verbose_name="Socialização")
    moradia = models.ForeignKey(Moradia, on_delete=models.CASCADE, verbose_name="Moradia adequada")
    
    #Status de adocao
    adotado = models.BooleanField(default=False, verbose_name="Adotado")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Gato"
        verbose_name_plural = "Gatos"
        db_table = "gatos"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.nome} ({self.get_sexo_display()})"
    
    @cached_property
    def em_lar_temporario(self):
        from django.apps import apps
        LarTemporarioAtual = apps.get_model('lares_temporarios', 'LarTemporarioAtual')
        return LarTemporarioAtual.objects.filter(gato=self).exists()
    
    @property
    def idade(self):
        """Retorna a idade formatada: meses / anos / anos e meses."""
        if not self.data_nascimento:
            return "Data de nascimento não informada"
        hoje = date.today()
        anos = hoje.year - self.data_nascimento.year
        meses = hoje.month - self.data_nascimento.month
        dias = hoje.day - self.data_nascimento.day
        if dias < 0:
            meses -= 1
        if meses < 0:
            anos -= 1
            meses += 12

        total_meses = anos * 12 + meses
        if total_meses < 1:
            return "Menos de 1 mês"
        if total_meses < 12:
            return f"{total_meses} mês{'es' if total_meses != 1 else ''}"
        if meses == 0:
            return f"{anos} ano{'s' if anos != 1 else ''}"
        return f"{anos} ano{'s' if anos != 1 else ''} e {meses} mês{'es' if meses != 1 else ''}"