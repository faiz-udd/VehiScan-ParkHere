"""This module contains the views for the Perfect Parking website."""
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .models import ParkingLot, ParkingLotMonitor, PendingParkingLotRegistration
from .utility import record_user_query
from django.db.models import QuerySet
from geopy.geocoders import Nominatim
from geopy.distance import distance
from geopy.distance import distance as geopy_distance
from .forms import  UserDetailsForm
from .models import UserProfile
from . import WebPaths
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, timezone
from .forms import ParkingLotRegistrationForm, ParkingLotForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserForm, DriverProfileForm, ParkingLotOwnerProfileForm, ProfileForm
from django.contrib.auth.models import User
from .forms import RegistrationForm
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
import random
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EmailOTP
from django.utils import timezone


class WebPages:
    HOME_PAGE = "website/index.html"
    PARKING_LOT = "website/parking-lot.html"
    PARKING_LOTS = "website/parking-lots.html"
    BOOK_SPACE = "website/book.html"
    PARKING_LOT_MONITOR = "website/parking-lot-monitor.html"
    PARKING_LOT_MONITORS = "website/parking-lot-monitors.html"
   
    REGISTER_USER = "registration/register-user.html"
    LOGIN_USER = "registration/login.html"
    PRIVACY_POLICY = "website/privacy-policy.html"
 
    
def index(request):
    parking_lots: QuerySet = ParkingLot.objects.all()
    return render(request, WebPages.HOME_PAGE, {"parking_lots": parking_lots})

def login_user(request):
    if request.method == "POST":  # FORM SUBMITTED
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('parking-lots')  # Redirect to parking lots page after logi
        else:
            return redirect('login')  # Redirect to login page if authentication fails
    else:  # FORM NOT SUBMITTED
        form = AuthenticationForm()
        return render(request, WebPages.LOGIN_USER, {"form": form})

def logout_user(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout

def parking_lot(request, parking_lot_id):
    parking_lot = get_object_or_404(ParkingLot, pk=parking_lot_id)
    return render(request, WebPages.PARKING_LOT, {"parking_lot": parking_lot})

def parking_lots(request):
    location_query = request.GET.get('location', '')
    start_time = request.GET.get('start_time')
    duration = request.GET.get('duration')

    # Geocode using OpenStreetMap Nominatim
    geolocator = Nominatim(user_agent="perfect_parking")
    location = geolocator.geocode(location_query)
    
    parking_lots = ParkingLot.objects.all()  # Replace with your actual query
    if not location:
        return render(request, WebPages.PARKING_LOTS, {'parking_lots': parking_lots} )

    # Get nearby parking lots (example query - adjust with your actual model)
    parking_lots = ParkingLot.objects.all()  # Replace with your actual query
    for lot in parking_lots:
        lot.distance = distance((location.latitude, location.longitude), 
                             (lot.latitude, lot.longitude)).km

    context = {
        'location': location,
        'parking_lots': parking_lots,
        'search_coords': [location.latitude, location.longitude],
        'start_time': start_time,
        'duration': duration
    }
    return render(request, WebPages.PARKING_LOTS, context)


def parking_lot_monitor(request, parking_lot_monitor_id):
    parking_lot_monitor = get_object_or_404(
        ParkingLotMonitor, pk=parking_lot_monitor_id
    )
    return render(
        request,
        WebPages.PARKING_LOT_MONITOR,
        {"parking_lot_monitor": parking_lot_monitor},
    )


def parking_lot_monitors(request):
    parking_lot_monitor_list: QuerySet = ParkingLotMonitor.objects.all()

    if request.method == "POST":  # FORM SUBMITTED
        latitude = float(request.POST["latitude"])
        longitude = float(request.POST["longitude"])

        record_user_query(latitude, longitude, request)

        # Calculate distance for each monitor
        for monitor in parking_lot_monitor_list:
            monitor.distance = geopy_distance(
                (latitude, longitude), (monitor.latitude, monitor.longitude)
            ).km

        # Sort by distance (nearest first)
        parking_lot_monitor_list = sorted(
            parking_lot_monitor_list, key=lambda m: m.distance
        )

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
    form_errors = []
    show_email_error = False

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        user_type = request.POST.get("user_type")
        avatar = request.FILES.get("avatar")

        # Check OTP verification in session
        if request.session.get('otp_verified_email') != email:
            form_errors.append("Please verify your email address with the OTP sent before registering.")

        if not email or not password or not confirm_password or not first_name or not last_name or not phone or not user_type:
            form_errors.append("All fields are required.")
        if password != confirm_password:
            form_errors.append("Passwords do not match.")
        if avatar and not avatar.content_type.startswith("image/"):
            form_errors.append("Profile picture must be an image file.")
        if User.objects.filter(username=email).exists():
            form_errors.append(f"A user with the email {email} already exists.")
            show_email_error = True

        if not form_errors:
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            if created:
                user.set_password(password)
                user.save()
            else:
                # If user already exists, do not proceed
                return JsonResponse({'success': False, 'errors': [f"A user with the email {email} already exists."]})

            # Only create UserProfile if it doesn't exist
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(
                    user=user,
                    phone_number=phone,
                    user_type=user_type,
                    avatar=avatar if avatar and avatar.content_type.startswith("image/") else None
                )
            login(request, user)
            del request.session['otp_verified_email']
            return JsonResponse({'success': True, 'message': 'Registration successful.'})

        return JsonResponse({'success': False, 'errors': form_errors})

    return render(request, "registration/register-user.html", {
        "form_errors": form_errors,
        "show_email_error": show_email_error
    })


#Account Section
@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(ParkingLot, pk=pk, owner__user=request.user)
    if request.method == "POST":
        form = ParkingLotForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('account')  # Redirect to the account page after saving
    else:
        form = ParkingLotForm(instance=listing)
    return render(request, "listings/edit.html", {"form": form, "listing": listing})

@login_required
def view_listing(request, pk):
    listing = get_object_or_404(ParkingLot, pk=pk, owner__user=request.user)
    return render(request, 'listings/view.html', {'listing': listing})

@login_required
def performance(request):
    if not request.user.profile.user_type == 'LOT_OWNER':
        return redirect('account')
    
    # Add performance metrics logic
    return render(request, 'account/performance.html')


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ParkingLotForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user.profile
            listing.save()
            return redirect('account')
    else:
        form = ParkingLotForm()
    
    return render(request, 'listings/create.html', {'form': form})

# views.py
@login_required
def register_parking(request):
    try:
        owner = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, "You need to register as a parking lot owner first")
        return redirect('account')

    if request.method == 'POST':
        form = ParkingLotRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save parking lot
            parking_lot = form.save(commit=False)
            parking_lot.owner = owner
            parking_lot.available_spaces = parking_lot.total_spaces
            parking_lot.save()

            # Create monitor
            ParkingLotMonitor.objects.create(
                parkingLot=parking_lot,
                name=form.cleaned_data['monitor_name'],
                latitude=form.cleaned_data['monitor_latitude'],
                longitude=form.cleaned_data['monitor_longitude'],
                camera_type=form.cleaned_data['camera_type'],
                resolution=form.cleaned_data['resolution'],
                ip_address=form.cleaned_data['ip_address'],
                installation_date=form.cleaned_data['installation_date'],
                maintenance_due=form.cleaned_data['maintenance_due'],
                status='ACTIVE'
            )

            messages.success(request, 'Parking space registered successfully!')
            return redirect('view_listing', pk=parking_lot.pk)
    else:
        form = ParkingLotRegistrationForm()

    return render(request, 'listings/register_parking.html', {'form': form})
    
# views.py
@login_required
def account(request):
    active_tab = request.GET.get('tab', 'listings' if request.user.profile.user_type == 'LOT_OWNER'  else '')
    
    context = {
        'active_tab': active_tab,
        'user_profile': request.user.profile,
        'active_listings': ParkingLot.objects.filter(owner__user=request.user, is_active=True),
        'pending_listings': ParkingLot.objects.filter(owner__user=request.user, is_active=False),
    }
    return render(request, 'account/accounts.html', context)

@login_required
def account_settings(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('account')  # Redirect to the account page after saving
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, "account/settings.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })

@login_required
def lot_owner_account_settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ParkingLotOwnerProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('account')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ParkingLotOwnerProfileForm(instance=profile)
    
    return render(request, 'account/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def security_settings(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully')
            return redirect('account')  # Redirect to account page after success
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'two_factor_enabled': getattr(request.user.profile, 'two_factor_enabled', False),
        'last_used_2fa': getattr(request.user.profile, 'last_used_2fa', None),
    }
    return render(request, 'account/security.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone = form.cleaned_data.get('phone')

            user = User.objects.create_user(username=str(first_name), email=email, password=password, first_name=first_name, last_name=last_name)
            UserProfile.objects.create(user=user, phone_number=phone)

            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register-user.html', {'form': form})

@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(ParkingLot, pk=pk, owner__user=request.user)
    if request.method == "POST":
        listing.delete()
        messages.success(request, "Listing deleted successfully.")
        return redirect('account')
    return render(request, 'listings/delete.html', {'listing': listing})

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'})
        if User.objects.filter(username=email).exists():
            return JsonResponse({'success': False, 'message': 'A user with this email already exists.'})
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(email=email, defaults={'otp': otp})
        send_mail(
            'Your OTP Code',
            f'Your OTP code is: {otp}',
            'faiz.bscs4430@iiu.edu.pk',
            [email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'OTP sent to your email.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

# views.py
@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        if not email or not otp:
            return JsonResponse({'success': False, 'message': 'Email and OTP are required.'})
        try:
            otp_obj = EmailOTP.objects.get(email=email, otp=otp)
            if otp_obj.is_expired():
                return JsonResponse({'success': False, 'message': 'OTP expired.'})
            otp_obj.delete()  # Remove OTP after verification
            request.session['otp_verified_email'] = email  # Mark as verified in session
            return JsonResponse({'success': True, 'message': 'OTP verified.'})
        except EmailOTP.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid OTP.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

# Add or update the view for handling the parking lot registration

@login_required
def create_parking_lot(request):
    # Check if user is a lot owner
    if request.user.profile.user_type != 'lot_owner':
        messages.error(request, "You don't have permission to register a parking lot.")
        return redirect('account')
        
    if request.method == 'POST':
        try:
            # Create a new pending registration
            registration = PendingParkingLotRegistration(
                # Parking lot details
                name=request.POST.get('name'),
                address=request.POST.get('address'),
                hours=request.POST.get('hours'),
                isPaidParking='isPaidParking' in request.POST,
                latitude=request.POST.get('latitude'),
                longitude=request.POST.get('longitude'),
                parking_spaces=request.POST.get('parking_spaces'),
                base_price_per_hour=request.POST.get('base_price_per_hour'),
                
                # Camera details
                monitor_name=request.POST.get('monitor_name'),
                monitor_latitude=request.POST.get('monitor_latitude') or request.POST.get('latitude'),
                monitor_longitude=request.POST.get('monitor_longitude') or request.POST.get('longitude'),
                camera_stream_url=request.POST.get('camera_stream_url'),
                
                # Owner info
                owner=request.user.profile,
                status='pending'
            )
            
            # Handle image files if they exist
            if 'image' in request.FILES:
                registration.image = request.FILES['image']
                
            if 'camera_image' in request.FILES:
                registration.camera_image = request.FILES['camera_image']
                
            registration.save()
            
            messages.success(request, 
                "Your parking lot registration has been submitted successfully! "
                "Our team will review and approve it shortly."
            )
            return redirect('account')
            
        except Exception as e:
            messages.error(request, f"An error occurred during registration: {str(e)}")
    
    return render(request, 'listings/create.html')

@login_required
def my_registrations(request):
    # Check if user is a lot owner
    if request.user.profile.user_type != 'lot_owner':
        messages.error(request, "You don't have permission to view parking lot registrations.")
        return redirect('account')
        
    registrations = PendingParkingLotRegistration.objects.filter(
        owner=request.user.profile
    ).order_by('-submitted_date')
    
    return render(request, 'listings/my_registrations.html', {
        'registrations': registrations,
        'active_tab': 'listings'
    })