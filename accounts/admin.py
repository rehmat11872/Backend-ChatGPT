from django.contrib import admin
from .models import User, Subscription, SubscriptionPlan
# Register your models here.
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'is_active']
    search_fields = ('email',)



class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active', 'is_upgraded')
    search_fields = ('user__email', 'plan__name')
    list_filter = ('is_active', 'is_upgraded', 'plan__free_trial')

admin.site.register(Subscription, SubscriptionAdmin)

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'features', 'free_trial')
    search_fields = ('name',)
    list_filter = ('free_trial',)

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)