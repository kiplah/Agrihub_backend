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

        # Products Count
        products_count = Product.objects.filter(user_id=seller_id).count()

        # Pending Payout (Wallet Balance)
        try:
            from wallet.models import Wallet
            wallet = Wallet.objects.get(user_id=seller_id)
            pending_payout = wallet.balance
        except (ImportError, Exception):
            pending_payout = 0

        # Growth Percent (Revenue this month vs last month)
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        last_month = current_month - 1 if current_month > 1 else 12
        last_month_year = current_year if current_month > 1 else current_year - 1

        # We can't filter timestamp directly easily without conversion or range
        # Approximation using filtering in python for simplicity or complex query
        # Let's reuse the monthly logic logic if possible or do a quick aggregation
        
        # Simplified: Get all orders, filter in python (not efficient for huge data but fine here)
        # Better: Filter by timestamp range
        import calendar
        
        def get_timestamp_range(year, month):
             start_dt = datetime(year, month, 1)
             # End date: first day of next month
             if month == 12:
                 end_dt = datetime(year + 1, 1, 1)
             else:
                 end_dt = datetime(year, month + 1, 1)
             return start_dt.timestamp(), end_dt.timestamp()

        curr_start, curr_end = get_timestamp_range(current_year, current_month)
        last_start, last_end = get_timestamp_range(last_month_year, last_month)

        current_month_rev = orders.filter(time__gte=curr_start, time__lt=curr_end).aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        last_month_rev = orders.filter(time__gte=last_start, time__lt=last_end).aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0

        if last_month_rev > 0:
            growth_percent = ((current_month_rev - last_month_rev) / last_month_rev) * 100
        else:
            growth_percent = 100 if current_month_rev > 0 else 0
            
        growth_percent = round(growth_percent, 1)

        # Top Products
        from django.db.models import Count
        top_products_qs = orders.values('product__id', 'product__name', 'product__imagepath') \
            .annotate(sold=Count('id')) \
            .order_by('-sold')[:5]
        
        top_products = []
        for p in top_products_qs:
            # Fix image path
            img = p['product__imagepath']
            if img:
                 if not img.startswith('http'):
                      img = f"http://127.0.0.1:8000/media/{img}" # Assuming media prefix is needed or already in db?
                      # Actually usually stored as relative path. product__imagepath is a CharField or ImageField file.url?
                      # If it is ImageField, .values() returns path string.
                      # Let's just pass the string, frontend handles http check usually?
                      # Wait, looking at frontend: {p.image ? <img src={p.image} ...
                      # It expects 'image', not 'imagepath'.
                      pass
            
            top_products.append({
                'id': p['product__id'],
                'name': p['product__name'],
                'image': img, 
                'sold': p['sold']
            })

        return Response({
            'TotalOrders': total_orders,
            'Revenue': revenue,
            'ActiveOrders': active_orders,
            'TotalSales': total_sales,
            'LowStockAlerts': low_stock_count,
            'UnreadMessages': unread_messages,
            'Products': products_count,
            'PendingPayout': pending_payout,
            'GrowthPercent': growth_percent,
            'top_products': top_products
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

    @action(detail=False, methods=['get'], url_path='buyer-stats/(?P<buyer_id>[^/.]+)')
    def buyer_stats(self, request, buyer_id=None):
        orders = Order.objects.filter(buyer_id=buyer_id)
        total_orders = orders.count()
        total_spent = orders.aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        active_orders = orders.exclude(order_status__in=['delivered', 'cancelled', 'returned']).count()
        
        distinct_addresses = orders.values('shipping_address').distinct().count()
        saved_addresses = max(distinct_addresses, 1) if total_orders > 0 else 0
        
        spending_by_day = [0] * 7
        now_ts = datetime.now().timestamp()
        seven_days_ago = now_ts - (7 * 24 * 3600)
        
        recent_orders = orders.filter(time__gte=seven_days_ago)
        for order in recent_orders:
            try:
                dt = datetime.fromtimestamp(order.time)
                day_idx = dt.weekday()
                spending_by_day[day_idx] += order.checkout_price
            except Exception:
                pass
                
        if sum(spending_by_day) == 0:
            for order in orders:
                try:
                    dt = datetime.fromtimestamp(order.time)
                    day_idx = dt.weekday()
                    spending_by_day[day_idx] += order.checkout_price
                except Exception:
                    pass

        latest_active_order = orders.exclude(order_status__in=['delivered', 'cancelled', 'returned']).order_by('-time').first()
        tracking_order = None
        if latest_active_order:
            tracking_order = {
                'id': latest_active_order.id,
                'product_name': latest_active_order.product.name,
                'status': latest_active_order.order_status,
                'checkout_price': latest_active_order.checkout_price,
                'quantity': latest_active_order.quantity,
                'time': latest_active_order.time
            }
        else:
            latest_order = orders.order_by('-time').first()
            if latest_order:
                tracking_order = {
                    'id': latest_order.id,
                    'product_name': latest_order.product.name,
                    'status': latest_order.order_status,
                    'checkout_price': latest_order.checkout_price,
                    'quantity': latest_order.quantity,
                    'time': latest_order.time
                }

        return Response({
            'TotalOrders': total_orders,
            'TotalSpent': total_spent,
            'ActiveOrders': active_orders,
            'SavedAddresses': saved_addresses,
            'SpendingByDay': spending_by_day,
            'TrackingOrder': tracking_order
        })

    @action(detail=False, methods=['get'], url_path='buyer-orders/(?P<buyer_id>[^/.]+)')
    def buyer_orders(self, request, buyer_id=None):
        orders = Order.objects.filter(buyer_id=buyer_id).order_by('-time')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

