"""This module contains the views for the Perfect Parking website."""
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .models import ParkingLot, ParkingLotMonitor, ParkingSpot, Booking, User, UserProfile ,Payment, Notification
from . import WebPaths
from .utility import record_user_query
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, QuerySet, Q
from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .forms import UserProfileForm


class WebPages:
    HOME_PAGE = "website/home.html"
    PARKING_LOT = "website/parking-lot.html"
    PARKING_LOT_MONITOR = "website/parking-lot-monitor.html"
    PARKING_LOT_MONITORS = "website/parking-lot-monitors.html"
    PARKING_LOTS = "website/parking-lots.html"
    REGISTER_USER = "registration/register.html"
    LOGIN = "registration/login.html"
    lOG_OUT= 'accounts/logout'
    PRIVACY_POLICY = "website/privacy-policy.html"  
    SEARCH= 'website/search.html'

def home(request):
    return render(request, WebPages.HOME_PAGE)

def index(request):
    """Home page view"""
    try:
        parking_lots = ParkingLot.objects.all()
        context = {
            'parking_lots': parking_lots,
            'page_title': 'Available Parking Lots'
        }
        return render(request, WebPages.PARKING_LOTS, context)
    except Exception as e:
        messages.error(request, f"Error loading parking lots: {str(e)}")
        return render(request, 'website/parking-lots.html', {'parking_lots': []})


def login_user(request):
    """
    Authenticates and logs in a user based on their submitted username and password.

    Args:
        request: An HttpRequest object that contains metadata about the current request.

    Returns:
        If the submitted form data is valid and the user exists, redirects to the parking lots page. Otherwise,
        redirects to the login page.

    Raises:
        None
    """
    if request.method == "POST":  # FORM SUBMITTED
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(WebPages.PARKING_LOTS)
        else:
            return redirect(WebPaths.LOGIN)
    else:  # FORM NOT SUBMITTED
        form = AuthenticationForm()
        return render(request, "registration/login.html", {"form": form})

def logout_user(request):
    logout(request)
    return render(request, WebPages.HOME_PAGE)


def parking_lot(request, parking_lot_id):
    parking_lot = get_object_or_404(ParkingLot, pk=parking_lot_id)
    return render(request, WebPages.PARKING_LOT, {"parking_lot": parking_lot})

def parking_lots(request):
    """Builds the parking lots page.

    Args:
        request (HttpRequest): _description_

    Returns:
        _type_: _description_
    """
    try:
        parking_lots = ParkingLot.objects.all()
        context = {
            'parking_lots': parking_lots,
            'page_title': 'Available Parking Lots'
        }
        return render(request, 'website/parking-lots.html', context)
    except Exception as e:
        messages.error(request, f"Error loading parking lots: {str(e)}")
        return render(request, 'website/parking-lots.html', {'parking_lots': []})

def parking_lot_monitor(request, parking_lot_monitor_id):
    parking_lot_monitor = get_object_or_404(
        ParkingLotMonitor, 
        pk=parking_lot_monitor_id
    )
    return render(
        request,
        WebPages.PARKING_LOT_MONITOR,
        {"parking_lot_monitor": parking_lot_monitor},
    )

def parking_lot_monitors(request):
    """Builds the parking lot monitors page.

    Args:
        request (HttpRequest): _description_

    Returns:
        _type_: _description_
    """
    parking_lot_monitor_list: QuerySet = ParkingLotMonitor.objects.all()

    if request.method == "POST":  # FORM SUBMITTED
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if not latitude or not longitude:
            messages.error(request, "Latitude and longitude are required.")
            return render(
                request,
                WebPages.PARKING_LOT_MONITORS,
                {"parking_lot_monitors": parking_lot_monitor_list},
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            messages.error(request, "Invalid latitude or longitude value.")
            return render(
                request,
                WebPages.PARKING_LOT_MONITORS,
                {"parking_lot_monitors": parking_lot_monitor_list},
            )

        record_user_query(latitude, longitude, request)

        context = {
            "parking_lot_monitors": parking_lot_monitor_list,
            "user_point": {"latitude": latitude, "longitude": longitude},
        }
        return render(request, WebPages.PARKING_LOT_MONITORS, context)

    return render(
        request,
        WebPages.PARKING_LOT_MONITORS,
        {"parking_lot_monitors": parking_lot_monitor_list},
    )

def privacy_policy(request):
    """Builds the privacy policy page."""
    return render(request, WebPages.PRIVACY_POLICY)

def register_user(request):
    """Guest User registers to use the app

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the user to the database
            user = form.save()
            # Add first name, last name, and email fields to the user model
            user.first_name = request.POST["first_name"]
            user.last_name = request.POST["last_name"]
            user.email = request.POST["email"]
            user.phone = request.POST['phone']
            user.save()
            return redirect(WebPaths.LOGIN)
    else:
        form = UserCreationForm()
    return render(request, WebPages.REGISTER_USER, {"form": form})

@login_required
def parking_lot_detail(request, pk):
    """Detail view for a specific parking lot"""
    try:
        parking_lot = get_object_or_404(ParkingLot, pk=pk)
        available_spots = ParkingSpot.objects.filter(
            parking_lot=parking_lot,
            is_occupied=False
        )
        context = {
            'parking_lot': parking_lot,
            'available_spots': available_spots,
            'page_title': parking_lot.name
        }
        return render(request, 'website/parking-lot.html', context)
    except Exception as e:
        messages.error(request, f"Error loading parking lot details: {str(e)}")
        return redirect('PerfectParking:home')

@login_required
def book_spot(request, spot_id):
    """Handle parking spot booking"""
    if request.method == 'POST':
        try:
            spot = get_object_or_404(ParkingSpot, id=spot_id)
            
            if spot.is_occupied:
                messages.error(request, 'This spot is already occupied.')
                return redirect('parking_lot_detail', pk=spot.parking_lot.id)
            
            # Get booking details from form
            start_time = datetime.strptime(
                request.POST.get('start_time'),
                '%Y-%m-%dT%H:%M'
            )
            end_time = datetime.strptime(
                request.POST.get('end_time'),
                '%Y-%m-%dT%H:%M'
            )
            
            # Calculate total cost
            duration = (end_time - start_time).total_seconds() / 3600  # hours
            total_cost = Decimal(str(duration)) * spot.parking_lot.base_price_per_hour
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                parking_spot=spot,
                start_time=start_time,
                end_time=end_time,
                total_cost=total_cost,
                status='PENDING'
            )
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_detail', pk=booking.id)
            
        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")
            return redirect('parking_lot_detail', pk=spot.parking_lot.id)
    
    # GET request - show booking form
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    return render(request, 'website/book-spot.html', {'spot': spot})

@login_required
def my_bookings(request):
    """User's booking list view"""
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'website/my-bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, pk):
    """Individual booking detail view"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'website/booking-detail.html', {'booking': booking})

@login_required
def cancel_booking(request, pk):
    """Cancel booking view"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        if booking.status == 'PENDING':
            booking.status = 'CANCELLED'
            booking.cancellation_reason = request.POST.get('reason', '')
            booking.save()
            messages.success(request, 'Booking cancelled successfully!')
        else:
            messages.error(request, 'This booking cannot be cancelled.')
    return redirect('booking_detail', pk=pk)

@staff_member_required
def admin_dashboard(request):
    # Get date range
    days = int(request.GET.get('days', 30))
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Calculate metrics
    total_bookings = Booking.objects.filter(
        start_time__gte=start_date
    ).count()
    
    total_revenue = Payment.objects.filter(
        status='COMPLETED',
        start_time__gte=start_date
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

@login_required
def profile_view(request):
    """User profile view"""
    profile = get_object_or_404(UserProfile, user=request.user)
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')[:5]
    return render(request, 'website/profile.html', {
        'profile': profile,
        'recent_bookings': bookings
    })

@login_required
def add_payment_method(request):
    """Add payment method view"""
    if request.method == 'POST':
        # Add payment method logic here
        messages.success(request, 'Payment method added successfully!')
        return redirect('profile')
    return render(request, 'website/add-payment-method.html')

@login_required
def booking_history(request):
    """View for user's booking history with filters"""
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    bookings = Booking.objects.filter(user=request.user)
    
    if status:
        bookings = bookings.filter(status=status)
    if date_from:
        bookings = bookings.filter(start_time__gte=date_from)
    if date_to:
        bookings = bookings.filter(end_time__lte=date_to)
        
    return render(request, 'website/booking-history.html', {
        'bookings': bookings,
        'page_title': 'Booking History'
    })

def nearby_parking_lots(request):
    """View for finding nearby parking lots"""
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lng')
    radius = request.GET.get('radius', 5.0)  # Default 5km radius
    
    if latitude and longitude:
        # Implement nearby search logic
        parking_lots = ParkingLot.objects.all()  # Replace with actual search
        context = {
            'parking_lots': parking_lots,
            'user_location': {'lat': latitude, 'lng': longitude}
        }
        return render(request, 'website/nearby-parking-lots.html', context)
    return render(request, 'website/nearby-parking-lots.html')

@login_required
def monitor_status(request):
    """View for monitoring parking lot status"""
    if not request.user.userprofile.role in ['LOT_OWNER', 'LOT_MANAGER', 'ADMIN']:
        messages.error(request, 'Access denied.')
        return redirect('home')
        
    monitors = ParkingLotMonitor.objects.all()
    return render(request, 'website/monitor-status.html', {'monitors': monitors})

class ParkingLotViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def update_occupancy(self, request, pk=None):
        """Update parking lot occupancy"""
        parking_lot = self.get_object()
        new_occupancy = request.data.get('occupancy')
        
        if new_occupancy is not None:
            parking_lot.current_occupancy = max(0, min(new_occupancy, parking_lot.max_capacity))
            parking_lot.save()
            return Response({'status': 'success'})
        return Response({'error': 'Invalid occupancy data'}, status=400)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearby parking lots"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 5.0))  # km
        
        if not all([lat, lng]):
            return Response({'error': 'Location required'}, status=400)
            
        # Use geodjango or haversine formula to find nearby lots
        # Implementation depends on your specific needs

@login_required
def update_profile(request):
    """Update user profile view"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'website/update-profile.html', {'form': form})
