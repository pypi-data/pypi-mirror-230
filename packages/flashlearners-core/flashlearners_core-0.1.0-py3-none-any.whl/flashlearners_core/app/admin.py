from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class SubscriptionInlineAdmin(admin.TabularInline):
    can_delete = False
    model = Subscription
    fk_name = 'created_by'
    extra = 0


class TokenInlineAdmin(admin.TabularInline):
    model = Token
    fk_name = 'user'
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class HasActiveSubscriptionFilter(SimpleListFilter):
    title = "Has Active Subscription"
    parameter_name = "has_active_subscription"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        f = dict(created_by_id=OuterRef("pk"), expiry__gt=timezone.now())
        if self.value() == "yes":
            return queryset.filter(Exists(Subscription.objects.filter(**f)))
        else:
            return queryset.exclude(Exists(Subscription.objects.filter(**f)))


class UserAdmin(BaseUserAdmin):
    inlines = (SubscriptionInlineAdmin, TokenInlineAdmin)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "avatar")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "first_name", "avatar", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "first_name", 'current_subscription', "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_active", HasActiveSubscriptionFilter)
    search_fields = ("username", "first_name")
    ordering = ("username", "first_name", "created_at")

    def current_subscription(self, obj):
        return obj.current_subscription

    def has_active_subscription(self, obj):
        return obj.has_active_subscription

    current_subscription.short_description = "Current Description"
    current_subscription.admin_order_field = "current_subscription"
    current_subscription.boolean = False

    has_active_subscription.short_description = "Has active subscription"
    has_active_subscription.admin_order_field = "current_subscription"
    has_active_subscription.boolean = True


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


class FaqAdmin(BaseModelAdmin):
    search_fields = ('question',)
    list_filter = ("type", )
    list_display = ('question', 'type', 'answer', 'created_at', 'updated_at')


class FeedbackAdmin(BaseModelAdmin):
    search_fields = ('type', 'feature')
    list_filter = ("type", "feature")
    list_display = ('feature', 'type', 'description', 'rating',
                    'created_by', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class FlashCardAdmin(BaseModelAdmin):
    search_fields = ('type', 'feature')
    list_display = ('topic', 'question', 'answer',
                    'created_at', 'updated_at')


class FlashCardInlineAdmin(admin.TabularInline):
    model = FlashCard
    extra = 0
    fk_name = 'topic'


class GuideAdmin(BaseModelAdmin):
    search_fields = ('title',)
    list_filter = ("type", )
    list_display = ('title', 'type', 'created_at', 'updated_at')


class NovelChapterAdmin(admin.TabularInline):
    model = NovelChapter
    extra = 0
    fk_name = 'novel'


class NovelAdmin(BaseModelAdmin):
    inlines = (NovelChapterAdmin, )
    list_filter = ('is_active', )
    search_fields = ('title',)
    list_display = ('title', 'is_active', 'created_at', 'updated_at')


class MediaAdmin(BaseModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'type', 'url', 'is_local', 'created_at',
                    'updated_at')


class VideoAdmin(BaseModelAdmin):
    search_fields = ('title', 'topic__name')
    list_display = ('topic', 'title', 'created_at', 'updated_at')


class NotificationAdmin(BaseModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'created_at', 'updated_at')


class PaymentAdmin(BaseModelAdmin):
    search_fields = ('reference', 'created_by__first_name',
                     'created_by__email')
    list_filter = ('status', 'mode')
    list_display = (
        'created_by', 'reference', 'amount', 'status',
        'created_at', 'updated_at'
    )


class TopicInlineAdmin(admin.TabularInline):
    model = Topic
    fk_name = 'subject'
    extra = 0


class SubjectAdmin(BaseModelAdmin):
    inlines = (TopicInlineAdmin, )
    search_fields = ('name', )
    list_filter = ("requires_calculator", "allow_free", "is_active")
    list_display = ('name', 'requires_calculator', 'allow_free',
                    'current_affair', 'is_active', 'created_at', 'updated_at')


class TopicAdmin(BaseModelAdmin):
    inlines = (FlashCardInlineAdmin, )
    search_fields = ('name', 'subject__name')
    list_filter = ("allow_free", "is_active")
    list_display = ('name', 'subject', 'parent', 'is_active',
                    'allow_free', 'created_at', 'updated_at')


class OptionAdmin(admin.TabularInline):
    model = Option
    extra = 0
    fk_name = 'question'


class QuestionAdmin(BaseModelAdmin):
    inlines = (OptionAdmin, )
    search_fields = ('name', 'subject__name')
    list_filter = ("type", "is_active")
    list_display = ('title', 'subject', 'topic', 'is_active',
                    'created_at', 'updated_at')


class SessionAdmin(BaseModelAdmin):
    search_fields = ('name', )
    ordering = ('-year', )
    list_display = ('name', 'year', 'created_at', 'updated_at')



User_ = get_user_model()

admin.site.register(User_, UserAdmin)
admin.site.register(Faq, FaqAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(FlashCard, FlashCardAdmin)
admin.site.register(Guide, GuideAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Novel, NovelAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
# admin.site.register(Versioning)
