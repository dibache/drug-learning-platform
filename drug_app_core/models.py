from django.contrib.auth.models import User
from django.db import models


# ۱. ۱۲ مبحث اطلاعات دارویی کارآموزی عرصه ۱
class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='modules_images/', blank=True, null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# ۲. پروفایل کاربر (شامل اطلاعات دانشجویی، سکه‌ها و امتیاز کاپ)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=10, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    coins = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    cup_score = models.IntegerField(default=0)
    completed_modules = models.ManyToManyField(Module, blank=True)

    def __str__(self):
        return f'{self.full_name or self.user.username} ({self.student_id})'


# ۳. سوالات تستی و سناریوهای بالینی با تگ دارویی لایتنر
class Question(models.Model):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='questions'
    )
    text = models.TextField()
    image = models.ImageField(upload_to='questions_images/', blank=True, null=True)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    explanation = models.TextField(blank=True, null=True)
    drug_tag = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.module.title} - {self.text[:30]}...'


# ۴. جعبه لایتنر (فلش‌کارت‌های اختصاصی دانشجو یا عمومی ادمین)
class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  # اگر خالی باشد یعنی عمومی (ادمین)
    drug_name = models.CharField(max_length=100)
    front_text = models.CharField(max_length=255)
    back_text = models.TextField()
    box_level = models.IntegerField(default=1)
    next_review_date = models.DateField(auto_now_add=True)

    def __str__(self):
        owner = self.user.username if self.user else "عمومی (ادمین)"
        return f"{owner} - {self.drug_name} (جعبه {self.box_level})"