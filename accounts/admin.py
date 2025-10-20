# from django.contrib import admin
# from .models import User, Subscription, SubscriptionPlan
# # Register your models here.
# @admin.register(User)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ['id', 'email', 'is_active']
#     search_fields = ('email',)



# class SubscriptionAdmin(admin.ModelAdmin):
#     list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active', 'is_upgraded')
#     search_fields = ('user__email', 'plan__name')
#     list_filter = ('is_active', 'is_upgraded', 'plan__free_trial')

# admin.site.register(Subscription, SubscriptionAdmin)

# class SubscriptionPlanAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'features', 'free_trial')
#     search_fields = ('name',)
#     list_filter = ('free_trial',)

# admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)


from django.contrib import admin
from django.utils.html import format_html
from .models import User, Subscription, SubscriptionPlan

# ---------- Inlines ----------
class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    can_delete = False
    readonly_fields = ("start_date", "end_date", "is_active", "is_upgraded")
    fields = ("plan", "start_date", "end_date", "is_active", "is_upgraded")


# ---------- User ----------
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "avatar_thumb", "email", "name", "plan_name", "is_active", "date_joined")
    list_display_links = ("id", "email")
    search_fields = ("email", "name")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")
    inlines = (SubscriptionInline,)
    list_select_related = ("subscription", "subscription__plan")

    fieldsets = (
        ("Account", {"fields": ("email", "password")}),
        ("Profile", {"fields": ("name", "avatar")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Links", {"fields": ("subscription",)}),  # helpful direct link
    )

    actions = ("activate_users", "deactivate_users")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Avoid N+1: join subscription + plan
        return qs.select_related("subscription", "subscription__plan")

    def plan_name(self, obj):
        if obj.subscription and obj.subscription.plan:
            return obj.subscription.plan.name
        return "—"
    plan_name.short_description = "Plan"

    def avatar_thumb(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:32px;width:32px;border-radius:50%;object-fit:cover;border:1px solid #e5e7eb" />',
                obj.avatar.url
            )
        return "—"
    avatar_thumb.short_description = "Avatar"

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} user(s).")

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} user(s).")

    class Media:
        css = {"all": ("admin/css/users.css",)}     # optional per-model CSS
        js = ("admin/js/users.js",)                 # optional per-model JS


# ---------- Subscription ----------
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user_email", "plan", "start_date", "end_date", "is_active", "is_upgraded")
    list_filter = ("is_active", "is_upgraded", "plan__free_trial", "plan__name")
    search_fields = ("user__email", "plan__name")
    date_hierarchy = "start_date"
    autocomplete_fields = ("user", "plan")
    list_select_related = ("user", "plan")
    actions = ("mark_upgraded", "cancel_subscription")

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User"

    @admin.action(description="Mark selected as upgraded")
    def mark_upgraded(self, request, queryset):
        updated = queryset.update(is_upgraded=True, is_active=True)
        self.message_user(request, f"Marked upgraded: {updated}")

    @admin.action(description="Cancel selected subscriptions")
    def cancel_subscription(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Cancelled: {updated}")


# ---------- SubscriptionPlan ----------
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration", "price", "free_trial")
    list_filter = ("free_trial", "duration")
    search_fields = ("name",)
    ordering = ("name",)

    # Show subscriptions inline under a plan (read-only)
    class SubInline(admin.TabularInline):
        model = Subscription
        fields = ("user", "start_date", "end_date", "is_active", "is_upgraded")
        extra = 0
        can_delete = False
        readonly_fields = fields

    inlines = (SubInline,)
