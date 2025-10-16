from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Gasto, Categoria
from .forms import GastoForm
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv

def index(request):
    categoria_id = request.GET.get('categoria')
    edit_gasto_id = request.GET.get('editar')  
    form = GastoForm()
    
    if request.method == 'POST':
        if 'edit_gasto_id' in request.POST:
            # Edição de gasto
            gasto = get_object_or_404(Gasto, id=request.POST['edit_gasto_id'])
            form = GastoForm(request.POST, instance=gasto)
            if form.is_valid():
                form.save()
                messages.success(request, 'Gasto editado com sucesso!')
                return redirect('index')
            else:
                messages.error(request, 'Erro ao editar gasto. Verifique os dados.')
                edit_gasto_id = request.POST['edit_gasto_id']  # Mantém o modal aberto
        else:
            # Novo gasto
            form = GastoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Gasto adicionado com sucesso!')
                return redirect('index')
            else:
                messages.error(request, 'Erro ao adicionar gasto. Verifique os dados.')
    
    gastos = Gasto.objects.select_related('categoria').order_by('-data_gasto')[:5]
    if categoria_id:
        try:
            gastos = gastos.filter(categoria_id=int(categoria_id))
        except ValueError:
            messages.error(request, 'Categoria inválida.')
    
    categorias = Categoria.objects.all()
    edit_gasto = None
    if edit_gasto_id:
        edit_gasto = get_object_or_404(Gasto, id=edit_gasto_id)
        form = GastoForm(instance=edit_gasto)
    
    return render(request, 'index.html', {
        'form': form,
        'gastos': gastos,
        'categorias': categorias,
        'categoria_selecionada': categoria_id,
        'edit_gasto': edit_gasto
    })

def apagar_gasto(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id)
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, 'Gasto apagado com sucesso!')
        return redirect('index')
    return render(request, 'confirmar_apagar.html', {'gasto': gasto})


def dashboard(request):
    ano = request.GET.get('ano', datetime.now().year)
    categoria_id = request.GET.get('categoria')
    try:
        ano = int(ano)
    except ValueError:
        ano = datetime.now().year
        messages.error(request, 'Ano inválido. Usando o ano atual.')
    
    queryset = Gasto.objects.filter(data_gasto__year=ano).select_related('categoria')
    if categoria_id:
        try:
            queryset = queryset.filter(categoria_id=int(categoria_id))
        except ValueError:
            messages.error(request, 'Categoria inválida.')
    
    relatorio_mensal = queryset.values('data_gasto__month').annotate(total=Sum('valor'))
    relatorio_categoria = queryset.values('categoria__nome').annotate(total=Sum('valor'))
    total_ano = queryset.aggregate(total=Sum('valor'))['total'] or 0
    categorias = Categoria.objects.all()
    
    return render(request, 'dashboard.html', {
        'relatorio_mensal': relatorio_mensal,
        'relatorio_categoria': relatorio_categoria,
        'total_ano': total_ano,
        'ano': ano,
        'categorias': categorias,
        'categoria_selecionada': categoria_id
    })

def dados_graficos(request):
    ano = request.GET.get('ano', datetime.now().year)
    categoria_id = request.GET.get('categoria')
    try:
        ano = int(ano)
    except ValueError:
        ano = datetime.now().year
    
    queryset = Gasto.objects.filter(data_gasto__year=ano).select_related('categoria')
    if categoria_id:
        try:
            queryset = queryset.filter(categoria_id=int(categoria_id))
        except ValueError:
            pass  # Ignora categoria inválida para os gráficos
    
    relatorio_mensal = queryset.values('data_gasto__month').annotate(total=Sum('valor'))
    relatorio_categoria = queryset.values('categoria__nome').annotate(total=Sum('valor'))
    
    meses = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 
             7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    dados_mensal = [{'mes': meses[item['data_gasto__month']], 'total': float(item['total'])} for item in relatorio_mensal]
    dados_categoria = [{'categoria': item['categoria__nome'], 'total': float(item['total'])} for item in relatorio_categoria]
    
    return JsonResponse({
        'mensal': dados_mensal,
        'categoria': dados_categoria
    })
    
def historico(request):
    # Obter parâmetros de filtro
    categoria_id = request.GET.get('categoria')
    recorrencia = request.GET.get('recorrencia')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Consultar gastos
    gastos = Gasto.objects.select_related('categoria').order_by('-data_gasto')
    
    # Aplicar filtros
    if categoria_id:
        try:
            gastos = gastos.filter(categoria_id=int(categoria_id))
        except ValueError:
            messages.error(request, 'Categoria inválida.')
    
    if recorrencia:
        gastos = gastos.filter(recorrência=recorrencia)
    
    if data_inicio:
        try:
            gastos = gastos.filter(data_gasto__gte=data_inicio)
        except ValueError:
            messages.error(request, 'Data de início inválida.')
    
    if data_fim:
        try:
            gastos = gastos.filter(data_gasto__lte=data_fim)
        except ValueError:
            messages.error(request, 'Data de fim inválida.')
    
    # Paginação
    paginator = Paginator(gastos, 12)  # 12 gastos por página
    page = request.GET.get('page')
    try:
        gastos_paginados = paginator.page(page)
    except PageNotAnInteger:
        gastos_paginados = paginator.page(1)
    except EmptyPage:
        gastos_paginados = paginator.page(paginator.num_pages)
    
    categorias = Categoria.objects.all()
    recorrencias = Gasto.RECORRENCIA_CHOICES
    
    return render(request, 'historico.html', {
        'gastos': gastos_paginados,
        'categorias': categorias,
        'recorrencias': recorrencias,
        'categoria_selecionada': categoria_id,
        'recorrencia_selecionada': recorrencia,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })
    
def exportar_gastos(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gastos.csv"'
    writer = csv.writer(response)
    writer.writerow(['Data', 'Descrição', 'Categoria', 'Valor', 'Recorrência'])
    
    gastos = Gasto.objects.select_related('categoria').order_by('-data_gasto')
    if request.GET.get('categoria'):
        try:
            gastos = gastos.filter(categoria_id=int(request.GET.get('categoria')))
        except ValueError:
            messages.error(request, 'Categoria inválida.')
    if request.GET.get('recorrencia'):
        gastos = gastos.filter(recorrência=request.GET.get('recorrencia'))
    if request.GET.get('data_inicio'):
        try:
            gastos = gastos.filter(data_gasto__gte=request.GET.get('data_inicio'))
        except ValueError:
            messages.error(request, 'Data de início inválida.')
    if request.GET.get('data_fim'):
        try:
            gastos = gastos.filter(data_gasto__lte=request.GET.get('data_fim'))
        except ValueError:
            messages.error(request, 'Data de fim inválida.')
    
    for gasto in gastos:
        writer.writerow([
            gasto.data_gasto.strftime('%d/%m/%Y'),
            gasto.descrição,
            gasto.categoria.nome,
            gasto.valor,
            gasto.recorrência
        ])
    
    return response