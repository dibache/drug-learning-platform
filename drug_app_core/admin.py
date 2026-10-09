from django.contrib import admin
from .models import Flashcard, Module, Question, UserProfile

admin.site.register(UserProfile)
admin.site.register(Module)
admin.site.register(Question)
admin.site.register(Flashcard)