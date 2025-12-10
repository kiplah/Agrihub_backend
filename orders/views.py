from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import Order
from products.models import Product
from chat.models import Message
from .serializers import OrderSerializer
from datetime import datetime

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        buyer_id = self.request.query_params.get('buyer_id')
        seller_id = self.request.query_params.get('seller_id')
        if buyer_id:
            queryset = queryset.filter(buyer_id=buyer_id)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='seller-stats/(?P<seller_id>[^/.]+)')
    def seller_stats(self, request, seller_id=None):
        orders = Order.objects.filter(seller_id=seller_id)
        total_orders = orders.count()
        revenue = orders.aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        active_orders = orders.exclude(order_status__in=['delivered', 'cancelled', 'returned']).count()
        total_sales = orders.filter(order_status='delivered').aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        
        # Low Stock
        low_stock_count = Product.objects.filter(user_id=seller_id, stock_quantity__lte=F('low_stock_threshold')).count()
        
        # Unread Messages
        unread_messages = Message.objects.filter(receiver_id=seller_id, is_read=False).count()

        return Response({
            'TotalOrders': total_orders,
            'Revenue': revenue,
            'ActiveOrders': active_orders,
            'TotalSales': total_sales,
            'LowStockAlerts': low_stock_count,
            'UnreadMessages': unread_messages
        })

    @action(detail=False, methods=['get'], url_path='seller-orders/(?P<seller_id>[^/.]+)')
    def seller_orders(self, request, seller_id=None):
        orders = Order.objects.filter(seller_id=seller_id).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='monthly-stats/(?P<seller_id>[^/.]+)')
    def monthly_stats(self, request, seller_id=None):
        orders = Order.objects.filter(seller_id=seller_id)
        
        monthly_stats = {}
        yearly_stats = {}
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        current_month_revenue = 0
        current_year_revenue = 0

        for order in orders:
            dt = datetime.fromtimestamp(order.time)
            year = dt.year
            month_num = dt.month
            month_name = dt.strftime("%b") # Jan, Feb, etc.
            month_key = f"{year}-{month_num}" # Keep key for sorting if needed, or just use name if unique per year
            
            # Monthly
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'year': year, 'month': month_name, 'month_num': month_num, 'total_orders': 0, 'completed_orders': 0, 'total_revenue': 0}
            monthly_stats[month_key]['total_orders'] += 1
            
            if order.order_status == 'completed':
                monthly_stats[month_key]['completed_orders'] += 1
                monthly_stats[month_key]['total_revenue'] += order.checkout_price
                if year == current_year and month_num == current_month:
                    current_month_revenue += order.checkout_price

            # Yearly
            if year not in yearly_stats:
                yearly_stats[year] = {'year': year, 'total_orders': 0, 'completed_orders': 0, 'total_revenue': 0}
            yearly_stats[year]['total_orders'] += 1
            
            if order.order_status == 'completed':
                yearly_stats[year]['completed_orders'] += 1
                yearly_stats[year]['total_revenue'] += order.checkout_price
                if year == current_year:
                    current_year_revenue += order.checkout_price

        # Sort monthly stats by year and month_num
        monthly_results = sorted(list(monthly_stats.values()), key=lambda x: (x['year'], x['month_num']))
        yearly_results = sorted(list(yearly_stats.values()), key=lambda x: x['year'])
        
        return Response({
            "monthly_stats": monthly_results,
            "yearly_stats": yearly_results,
            "current_month_revenue": current_month_revenue,
            "current_year_revenue": current_year_revenue,
        })
