from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, Flashcard, Module, Question, UserProfile, UserCategoryProgress, DailyTip
from datetime import date


# صفحه خوش‌آمدگویی اولیه (دارای دو دکمه ورود و ثبت‌نام)
def welcome_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'drug_app_core/welcome.html')


# صفحه ورود اختصاصی
def login_view(request):
    error = None
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')

        try:
            profile = UserProfile.objects.get(student_id=student_id)
            if not profile.is_approved:
                error = 'حساب کاربری شما هنوز توسط مدیر تایید نشده است.'
            else:
                user = authenticate(
                    request, username=profile.user.username, password=password
                )
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    error = 'رمز عبور اشتباه است.'
        except UserProfile.DoesNotExist:
            error = 'کاربری با این شماره دانشجویی یافت نشد.'

        return render(request, 'drug_app_core/login.html', {'error': error})

    return render(request, 'drug_app_core/login.html')


# صفحه ثبت‌نام اختصاصی
def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        student_id = request.POST.get('student_id')
        national_id = request.POST.get('national_id')
        password = request.POST.get('password')

        if UserProfile.objects.filter(student_id=student_id).exists():
            error = 'این شماره دانشجویی از قبل ثبت‌نام کرده است!'
            return render(request, 'drug_app_core/register.html', {'error': error})

        username = f'student_{student_id}'
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(
            user=user,
            student_id=student_id,
            national_id=national_id,
            full_name=full_name,
            is_approved=False  # در انتظار تایید ادمین
        )

        # اینجا به جای لاگین مستقیم، کاربر را به صفحه پیام هدایت می‌کنیم یا در صفحه ثبت‌نام پیام موفقیت نشان می‌دهیم
        return render(request, 'drug_app_core/register.html', {
            'success_message': 'ثبت‌نام با موفقیت انجام شد. بعد از تایید ادمین می‌توانید وارد اکانت شوید.'
        })

@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'student_id': request.user.username,
            'full_name': request.user.username,
        },
    )

    # منطق محاسبه استریک بر اساس ورود روزانه
    today = date.today()
    if profile.last_active_date != today:
        if profile.last_active_date:
            from datetime import timedelta
            if profile.last_active_date == today - timedelta(days=1):
                profile.streak_days += 1  # روز متوالی بعدی
            elif profile.last_active_date < today - timedelta(days=1):
                profile.streak_days = 1   # قطع شدن زنجیره و ریست شدن استریک
        else:
            profile.streak_days = 1

        profile.last_active_date = today
        profile.save()

    modules = Module.objects.all().order_by('order', 'id')[:3]
    daily_tips = DailyTip.objects.filter(is_active=True).order_by('-created_at')

    return render(
        request, 'drug_app_core/dashboard.html', {
            'profile': profile,
            'modules': modules,
            'daily_tips': daily_tips
        }
    )


@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'drug_app_core/profile.html', {'profile': profile})


@login_required
def learning_view(request):
    modules = Module.objects.all().order_by('order')
    return render(request, 'drug_app_core/learning.html', {'modules': modules})


@login_required
def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    questions = module.questions.all()
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    submitted = False

    for q in questions:
        q.user_answer = None
        q.user_is_correct = False

    if request.method == 'POST':
        submitted = True
        correct_count = 0
        total_questions = questions.count()

        for q in questions:
            user_ans = request.POST.get(f'q_{q.id}')
            if user_ans:
                q.user_answer = user_ans
            if user_ans == q.correct_option:
                q.user_is_correct = True
                correct_count += 1
            else:
                q.user_is_correct = False

        if total_questions > 0 and not profile.completed_modules.filter(
            id=module.id
        ).exists():
            earned_coins = correct_count * 5
            profile.coins += earned_coins
            profile.score += correct_count * 10
            profile.completed_modules.add(module)
            profile.save()

    return render(
        request,
        'drug_app_core/module_detail.html',
        {'module': module, 'questions': questions, 'submitted': submitted},
    )

@login_required
def flashcards_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_user_flashcard':
            card_id = request.POST.get('card_id')
            Flashcard.objects.filter(id=card_id, user=request.user).delete()

        elif action == 'add_to_weakness':
            drug_name = request.POST.get('drug_name')
            category_id = request.POST.get('category_id')
            back_text = request.POST.get('back_text')

            category = Category.objects.filter(id=category_id).first() if category_id else None

            if drug_name and back_text:
                Flashcard.objects.get_or_create(
                    user=request.user,
                    drug_name=drug_name,
                    defaults={
                        'category': category,
                        'front_text': drug_name,
                        'back_text': back_text,
                        'box_level': 1
                    }
                )
        return redirect('flashcards')

    admin_cards = Flashcard.objects.filter(user=None).select_related('category').order_by('category__name', '-id')
    user_cards = Flashcard.objects.filter(user=request.user).select_related('category').order_by('-id')
    categories = Category.objects.all().order_by('order', 'name')

    admin_category_data = []
    user_category_data = []

    for cat in categories:
        admin_total = admin_cards.filter(category=cat).count()
        admin_category_data.append({
            'category': cat,
            'total': admin_total
        })

        user_total = user_cards.filter(category=cat).count()
        user_category_data.append({
            'category': cat,
            'total': user_total
        })

    return render(request, 'drug_app_core/flashcards.html', {
        'admin_cards': admin_cards,
        'user_cards': user_cards,
        'categories': categories,
        'admin_category_data': admin_category_data,
        'user_category_data': user_category_data,
    })

@login_required
def leitner_quiz_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'submit_answer':
            category_id = request.POST.get('category_id')
            drug_name = request.POST.get('drug_name')
            back_text = request.POST.get('back_text')
            result = request.POST.get('result')

            category = Category.objects.filter(id=category_id).first()
            if category:
                progress, _ = UserCategoryProgress.objects.get_or_create(
                    user=request.user,
                    category=category,
                    defaults={'total_cards': Flashcard.objects.filter(user=None, category=category).count()}
                )

                if result == 'known':
                    if progress.mastered_cards < progress.total_cards:
                        progress.mastered_cards += 1
                        progress.save()
                elif result == 'unknown':
                    if drug_name and back_text:
                        Flashcard.objects.get_or_create(
                            user=request.user,
                            drug_name=drug_name,
                            defaults={
                                'category': category,
                                'front_text': drug_name,
                                'back_text': back_text,
                                'box_level': 1
                            }
                        )
            return JsonResponse({'status': 'success'})

    categories = Category.objects.all().order_by('order', 'name')
    category_data = []

    for cat in categories:
        total = Flashcard.objects.filter(user=None, category=cat).count()
        progress, _ = UserCategoryProgress.objects.get_or_create(
            user=request.user, category=cat, defaults={'total_cards': total}
        )
        if progress.total_cards != total:
            progress.total_cards = total
            progress.save()

        percentage = int((progress.mastered_cards / total * 100)) if total > 0 else 0

        category_data.append({
            'category': cat,
            'total': total,
            'mastered': progress.mastered_cards,
            'percentage': percentage
        })

    admin_cards = Flashcard.objects.filter(user=None).select_related('category').order_by('category__name', '-id')

    return render(request, 'drug_app_core/leitner_quiz.html', {
        'category_data': category_data,
        'admin_cards': admin_cards
    })

@login_required
def dashboard_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    modules = Module.objects.all().order_by('id')
    daily_tips = DailyTip.objects.filter(is_active=True).order_by('-created_at')

    return render(request, 'drug_app_core/dashboard.html', {
        'profile': profile,
        'modules': modules,
        'daily_tips': daily_tips,
    })

@login_required
def ranking_view(request):
    # مرتب‌سازی بر اساس امتیاز (score) و سکه‌ها (coins)
    profiles = UserProfile.objects.all().order_by('-score', '-coins')
    return render(request, 'drug_app_core/ranking.html', {'profiles': profiles})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@staff_member_required
def custom_admin_dashboard(request):
    users_count = UserProfile.objects.count()
    modules_count = Module.objects.count()
    questions_count = Question.objects.count()
    flashcards_count = Flashcard.objects.filter(user=None).count()
    tips_count = DailyTip.objects.count()

    context = {
        'users_count': users_count,
        'modules_count': modules_count,
        'questions_count': questions_count,
        'flashcards_count': flashcards_count,
        'tips_count': tips_count,
    }
    return render(request, 'drug_app_core/custom_admin.html', context)


@staff_member_required
def admin_modules_view(request):
    modules = Module.objects.all().order_by('order')
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_module':
            title = request.POST.get('title')
            description = request.POST.get('description')
            order = request.POST.get('order', 0)
            image = request.FILES.get('image')

            Module.objects.create(
                title=title, description=description, order=order, image=image
            )
        elif action == 'edit_module':
            module_id = request.POST.get('module_id')
            module = get_object_or_404(Module, id=module_id)
            module.title = request.POST.get('title')
            module.description = request.POST.get('description')
            module.order = request.POST.get('order', 0)
            if request.FILES.get('image'):
                module.image = request.FILES.get('image')
            module.save()

        elif action == 'delete_module':
            module_id = request.POST.get('module_id')
            Module.objects.filter(id=module_id).delete()

        return redirect('admin_modules')

    return render(request, 'drug_app_core/admin_modules.html', {'modules': modules})

@staff_member_required
def admin_questions_view(request):
    modules = Module.objects.all().order_by('order')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_question':
            module_id = request.POST.get('module_id')
            text = request.POST.get('text')
            image = request.FILES.get('image')
            option_a = request.POST.get('option_a')
            option_b = request.POST.get('option_b')
            option_c = request.POST.get('option_c')
            option_d = request.POST.get('option_d')
            correct_option = request.POST.get('correct_option')
            explanation = request.POST.get('explanation')
            drug_tag = request.POST.get('drug_tag')

            module = Module.objects.get(id=module_id)
            Question.objects.create(
                module=module,
                text=text,
                image=image,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                explanation=explanation,
                drug_tag=drug_tag,
            )

        elif action == 'edit_question':
            q_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=q_id)

            question.module_id = request.POST.get('module_id')
            question.text = request.POST.get('text')
            question.option_a = request.POST.get('option_a')
            question.option_b = request.POST.get('option_b')
            question.option_c = request.POST.get('option_c')
            question.option_d = request.POST.get('option_d')
            question.correct_option = request.POST.get('correct_option')
            question.explanation = request.POST.get('explanation')
            question.drug_tag = request.POST.get('drug_tag')

            if request.FILES.get('image'):
                question.image = request.FILES.get('image')

            question.save()

        elif action == 'delete_question':
            q_id = request.POST.get('question_id')
            Question.objects.filter(id=q_id).delete()

        return redirect('admin_questions')

    selected_module_id = request.GET.get('module_id')
    if selected_module_id:
        questions = Question.objects.filter(module_id=selected_module_id).select_related('module')
    else:
        questions = Question.objects.all().select_related('module')

    context = {
        'questions': questions,
        'modules': modules,
        'selected_module_id': selected_module_id,
    }
    return render(request, 'drug_app_core/admin_questions.html', context)


@staff_member_required
def admin_users_view(request):
    profiles = UserProfile.objects.all().select_related('user')
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'toggle_approve':
            profile = get_object_or_404(UserProfile, id=user_id)
            profile.is_approved = not profile.is_approved
            profile.save()
        elif action == 'delete_user':
            profile = get_object_or_404(UserProfile, id=user_id)
            user = profile.user
            profile.delete()
            if user:
                user.delete()
        elif action == 'update_coins':
            coins_delta = int(request.POST.get('coins_delta', 0))
            profile = get_object_or_404(UserProfile, id=user_id)
            profile.coins += coins_delta
            profile.save()

        return redirect('admin_users')

    return render(request, 'drug_app_core/admin_users.html', {'profiles': profiles})


@staff_member_required
def admin_flashcards_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_category':
            cat_name = request.POST.get('category_name')
            if cat_name:
                Category.objects.get_or_create(name=cat_name)

        elif action == 'add_flashcard':
            drug_name = request.POST.get('drug_name')
            category_id = request.POST.get('category_id')
            back_text = request.POST.get('back_text')

            category = Category.objects.filter(id=category_id).first()

            if drug_name and back_text:
                Flashcard.objects.create(
                    user=None,
                    category=category,
                    drug_name=drug_name,
                    front_text=drug_name,
                    back_text=back_text,
                    box_level=1
                )

        elif action == 'delete_flashcard':
            card_id = request.POST.get('card_id')
            Flashcard.objects.filter(id=card_id, user=None).delete()

        elif action == 'delete_category':
            cat_id = request.POST.get('cat_id')
            Category.objects.filter(id=cat_id).delete()

        return redirect('admin_flashcards')

    flashcards = Flashcard.objects.filter(user=None).select_related('category').order_by('-id')
    categories = Category.objects.all().order_by('order', 'name')
    return render(request, 'drug_app_core/admin_flashcards.html', {'flashcards': flashcards, 'categories': categories})


@staff_member_required
def admin_dailytips_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_tip':
            title = request.POST.get('title')
            content = request.POST.get('content')
            is_active = True if request.POST.get('is_active') == 'on' else False
            if title and content:
                DailyTip.objects.create(title=title, content=content, is_active=is_active)

        elif action == 'edit_tip':
            tip_id = request.POST.get('tip_id')
            tip = get_object_or_404(DailyTip, id=tip_id)
            tip.title = request.POST.get('title')
            tip.content = request.POST.get('content')
            tip.is_active = True if request.POST.get('is_active') == 'on' else False
            tip.save()

        elif action == 'delete_tip':
            tip_id = request.POST.get('tip_id')
            DailyTip.objects.filter(id=tip_id).delete()

        return redirect('admin_dailytips')

    tips = DailyTip.objects.all().order_by('-created_at')
    return render(request, 'drug_app_core/admin_dailytips.html', {'tips': tips})