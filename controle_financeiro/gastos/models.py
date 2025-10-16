from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Gasto(models.Model):
    RECORRENCIA_CHOICES = [
        ('nenhuma', 'Nenhuma'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]

    descrição = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    recorrência = models.CharField(max_length=20, choices=RECORRENCIA_CHOICES, default='nenhuma')
    data_gasto = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descrição} - {self.valor}"