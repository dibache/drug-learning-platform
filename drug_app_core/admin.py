from django.contrib import admin
from .models import Flashcard, Module, Question, UserProfile
from .models import DailyTip

admin.site.register(UserProfile)
admin.site.register(Module)
admin.site.register(Question)
admin.site.register(Flashcard)
@admin.register(DailyTip)
class DailyTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')