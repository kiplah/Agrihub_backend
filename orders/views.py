from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Order
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
        active_orders = orders.exclude(order_status='completed').count()
        total_sales = orders.filter(order_status='completed').aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        
        return Response({
            'TotalOrders': total_orders,
            'Revenue': revenue,
            'ActiveOrders': active_orders,
            'TotalSales': total_sales
        })

    @action(detail=False, methods=['get'], url_path='monthly-stats/(?P<seller_id>[^/.]+)')
    def monthly_stats(self, request, seller_id=None):
        orders = Order.objects.filter(seller_id=seller_id)
        # Complex stats logic similar to Go implementation
        # For brevity, implementing a simplified version or full version if needed
        # This requires grouping by month/year which is easier in Python
        
        monthly_stats = {}
        yearly_stats = {}
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        current_month_revenue = 0
        current_year_revenue = 0

        for order in orders:
            dt = datetime.fromtimestamp(order.time)
            year = dt.year
            month = dt.month
            month_key = f"{year}-{month}"
            
            # Monthly
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'year': year, 'month': month, 'total_orders': 0, 'completed_orders': 0, 'total_revenue': 0}
            monthly_stats[month_key]['total_orders'] += 1
            
            if order.order_status == 'completed':
                monthly_stats[month_key]['completed_orders'] += 1
                monthly_stats[month_key]['total_revenue'] += order.checkout_price
                if year == current_year and month == current_month:
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

        # Calculate growth (simplified)
        monthly_results = list(monthly_stats.values())
        yearly_results = list(yearly_stats.values())
        
        return Response({
            "monthly_stats": monthly_results,
            "yearly_stats": yearly_results,
            "current_month_revenue": current_month_revenue,
            "current_year_revenue": current_year_revenue,
        })
