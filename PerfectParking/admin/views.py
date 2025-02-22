from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from ..models import Booking, ParkingLot, Payment, User

@staff_member_required
def admin_dashboard(request):
    # Get date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Calculate metrics
    total_bookings = Booking.objects.filter(
        start_time__gte=start_date
    ).count()
    
    total_revenue = Payment.objects.filter(
        status='completed',
        created_at__gte=start_date
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': Booking.objects.select_related('user', 'parking_spot')
                                        .order_by('-start_time')[:10],
        'user_stats': {
            'total': User.objects.count(),
            'active': User.objects.filter(last_login__gte=start_date).count()
        }
    }
    
    return render(request, 'admin/dashboard.html', context) 