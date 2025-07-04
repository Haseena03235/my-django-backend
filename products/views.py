from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, Banner
from .serializers import ProductSerializer, BannerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.storage import default_storage
from rest_framework import permissions

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if self.request.query_params.get('latest') == 'true':
            queryset = queryset.order_by('-created_at')[:10]  # Return latest 10 products
        return queryset

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        image = request.FILES['image']
        # Save the image or process it as needed
        return Response({"message": f"Image '{image.name}' uploaded!"}, status=status.HTTP_200_OK)

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]
