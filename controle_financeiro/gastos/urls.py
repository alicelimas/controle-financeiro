from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dados-graficos/', views.dados_graficos, name='dados_graficos'),
    path('apagar/<int:gasto_id>/', views.apagar_gasto, name='apagar_gasto'),
    path('historico/', views.historico, name='historico'),
    path('exportar-gastos/', views.exportar_gastos, name='exportar_gastos'),
]