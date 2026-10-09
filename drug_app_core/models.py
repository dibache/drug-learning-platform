from django.contrib.auth.models import User
from django.db import models


# ۱. پروفایل کاربر (شامل اطلاعات دانشجویی، سکه‌ها و امتیاز کاپ)
class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  student_id = models.CharField(
      max_length=20, unique=True
  )  # شماره دانشجویی (یکتا)
  national_id = models.CharField(max_length=10)  # کد ملی
  full_name = models.CharField(
      max_length=100
  )  # نام و نام خانوادگی به صورت کامل
  coins = models.IntegerField(default=0)
  cup_score = models.IntegerField(default=0)

  def __str__(self):
    return f"{self.full_name} ({self.student_id})"


# ۲. ۱۲ مبحث اطلاعات دارویی کارآموزی عرصه ۱
class Module(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  order = models.IntegerField(default=1)

  def __str__(self):
    return self.title


# ۳. سوالات تستی و سناریوهای بالینی با تگ دارویی لایتنر
class Question(models.Model):
  module = models.ForeignKey(Module, on_delete=models.CASCADE)
  text = models.TextField()
  option_a = models.CharField(max_length=255)
  option_b = models.CharField(max_length=255)
  option_c = models.CharField(max_length=255)
  option_d = models.CharField(max_length=255)
  correct_option = models.CharField(max_length=1)  # A, B, C یا D
  explanation = models.TextField()
  drug_tag = models.CharField(max_length=100)

  def __str__(self):
    return f"{self.module.title} - سوال {self.id}"


# ۴. جعبه لایتنر (فلش‌کارت‌های اختصاصی دانشجو)
class Flashcard(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  drug_name = models.CharField(max_length=100)
  front_text = models.CharField(max_length=255)
  back_text = models.TextField()
  box_level = models.IntegerField(default=1)
  next_review_date = models.DateField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} - {self.drug_name} (جعبه {self.box_level})"