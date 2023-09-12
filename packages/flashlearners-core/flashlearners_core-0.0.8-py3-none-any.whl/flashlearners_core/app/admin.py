from django.contrib import admin
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class SubscriptionInlineAdmin(admin.TabularInline):
    can_delete = False
    model = Subscription
    fk_name = 'created_by'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (SubscriptionInlineAdmin, )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", )}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    'subscription'
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
                "fields": ("username", "first_name", 'subscription', "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "first_name", 'subscription', "is_staff", "is_superuser")
    list_filter = ('subscription', "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name")
    ordering = ("username", "first_name", "created_at")


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
                    'created_at', 'updated_at')


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
    search_fields = ('title',)
    list_display = ('title', 'created_at', 'updated_at')


class MediaAdmin(BaseModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'type', 'url', 'is_local', 'created_at',
                    'updated_at')


class VideoAdmin(BaseModelAdmin):
    search_fields = ('title',)
    list_display = ('topic', 'media', 'created_at', 'updated_at')


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
admin.site.register(Media, MediaAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Versioning)
