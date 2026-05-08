import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404
from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Product
from .serializers import ProductSerializer


def store_index(request):
    return render(request, 'store/index.html')


def store_checkout(request):
    return render(request, 'store/checkout.html')


def product_detail_page(request, slug):
    try:
        product = Product.objects.get(slug=slug, active=True)
    except Product.DoesNotExist:
        raise Http404()

    # Gradient index matching the API list ordering (-created_at)
    all_ids = list(
        Product.objects.filter(active=True).order_by('-created_at').values_list('id', flat=True)
    )
    try:
        gradient_idx = (all_ids.index(product.id) % 12) + 1
    except ValueError:
        gradient_idx = 1

    discount_pct = 0
    if product.original_price and product.price:
        discount_pct = round((1 - float(product.price) / float(product.original_price)) * 100)

    serializer = ProductSerializer(product, context={'request': request})
    product_json = json.dumps(serializer.data, cls=DjangoJSONEncoder)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'product_json': product_json,
        'gradient_idx': gradient_idx,
        'discount_pct': discount_pct,
    })


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(active=True).select_related('category')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        return qs


class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(active=True).select_related('category')
    lookup_field = 'slug'
