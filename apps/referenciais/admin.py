from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import SalarioBaseReferencia

@admin.register(SalarioBaseReferencia)
class SalarioBaseReferenciaAdmin(admin.ModelAdmin):
    list_display = ('desde', 'valor', 'legislacao', 'rejuste')

# from apps.referenciais.models import SalarioBaseReferencia
dados = [
    {"desde": 202001, "valor": 1039.00, "legislacao": "MP 916/2019 (Lei 14.013, de 2020)", "reajuste": 4.1},
    {"desde": 202002, "valor": 1045.00, "legislacao": "MP 919/2020 (Lei 14.013, de 2020)", "reajuste": 0.58},
    {"desde": 202101, "valor": 1100.00, "legislacao": "MP 1.021/2020 (Lei 14.158, de 2021)", "reajuste": 5.26},
    {"desde": 202201, "valor": 1212.00, "legislacao": "MP 1.091/2021 (Lei 14.358, de 2022)", "reajuste": 10.16},
    {"desde": 202301, "valor": 1302.00, "legislacao": "MP 1.143/2022 (Lei 14.663, de 2023)", "reajuste": 7.43},
    {"desde": 202303, "valor": 1320.00, "legislacao": "MP 1.172/2023 (Lei 14.663, de 2023) (Reajuste rel. 2022)", "reajuste": 8.90},
    {"desde": 202401, "valor": 1412.00, "legislacao": "Decreto 11.864/2024", "reajuste": 6.97},
    {"desde": 202501, "valor": 1518.00, "legislacao": "Decreto 12.324/2024", "reajuste": 7.95},
    {"desde": 202601, "valor": 1621.00, "legislacao": "Decreto 12.797/2025", "reajuste": 6.79},
]

# for dado in dados:
#     SalarioBaseReferencia.objects.create(**dado)

# print("Registros adicionados com sucesso!")
