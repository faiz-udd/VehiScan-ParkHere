from django.contrib import admin

from vehiscanWebsite.models import ParkingLot, ParkingLotMonitor, UserProfile, EmailOTP, PendingParkingLotRegistration

# Register your models here.

admin.site.register(ParkingLot)
admin.site.register(ParkingLotMonitor)
admin.site.register(UserProfile)
admin.site.register(EmailOTP)

class PendingParkingLotRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'submitted_date')
    list_filter = ('status', 'submitted_date')
    search_fields = ('name', 'address', 'owner__user__username')
    readonly_fields = ('submitted_date',)
    
    actions = ['approve_registrations', 'reject_registrations']
    
    def approve_registrations(self, request, queryset):
        for registration in queryset:
            registration.approve_registration()
        
        self.message_user(request, f"{queryset.count()} parking lots have been approved and are now live.")
    approve_registrations.short_description = "Approve selected parking lots"
    
    def reject_registrations(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} parking lots have been rejected.")
    reject_registrations.short_description = "Reject selected parking lots"

admin.site.register(PendingParkingLotRegistration, PendingParkingLotRegistrationAdmin)