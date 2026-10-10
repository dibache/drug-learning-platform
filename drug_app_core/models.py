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
    student_id = models.CharField(max_length=50, unique=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    coins = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=1)
    last_active_date = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(default=False) # تایید شده توسط ادمین
    completed_modules = models.ManyToManyField(Module, blank=True)

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


# ۴. دسته‌بندی‌های پویا (ایجاد شده توسط ادمین)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# ۵. جعبه لایتنر (متصل به دسته‌بندی پویا)
class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  # اگر خالی باشد یعنی عمومی (ادمین)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    drug_name = models.CharField(max_length=100)
    front_text = models.CharField(max_length=255)
    back_text = models.TextField()
    box_level = models.IntegerField(default=1)
    next_review_date = models.DateField(auto_now_add=True)

    def __str__(self):
        cat_name = self.category.name if self.category else "بدون دسته"
        owner = self.user.username if self.user else "عمومی (ادمین)"
        return f"{owner} - [{cat_name}] {self.drug_name}"

# میزان تسلط کاربر روی هر دسته بندی
class UserCategoryProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_cards = models.IntegerField(default=0)
    mastered_cards = models.IntegerField(default=0)  # تعداد کارت هایی که "بلد بودم" زده است

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} - {self.category.name} (تسلط: {self.mastered_cards}/{self.total_cards})"

class DailyTip(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان نکته")
    content = models.TextField(verbose_name="متن نکته")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "نکته روزمره بالینی"
        verbose_name_plural = "نکات روزمره بالینی"