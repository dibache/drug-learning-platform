from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Flashcard, Module, Question, UserProfile


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
            error = (
                'این شماره دانشجویی از قبل ثبت‌نام کرده است! لطفاً شماره دانشجویی را'
                ' اصلاح کنید.'
            )
            return render(request, 'drug_app_core/register.html', {'error': error})

        username = f'student_{student_id}'
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(
            user=user,
            student_id=student_id,
            national_id=national_id,
            full_name=full_name,
        )

        login(request, user)
        return redirect('dashboard')

    return render(request, 'drug_app_core/register.html')


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'student_id': request.user.username,
            'full_name': request.user.username,
        },
    )
    modules = Module.objects.all().order_by('order')
    return render(
        request, 'drug_app_core/dashboard.html', {'profile': profile, 'modules': modules}
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
        action = request.POST.get('action')
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

        # اگر دکمه افزودن به لایتنر فشرده شده بود
        if action == 'add_flashcard':
            drug_name = request.POST.get('drug_name')
            if drug_name:
                # ابتدا بررسی می‌کنیم آیا ادمین برای این دارو فلش‌کارتی با مشخصات خاص ساخته است؟
                admin_card = Flashcard.objects.filter(user=None, drug_name=drug_name).first()

                # اگر ادمین متنی وارد کرده بود از آن استفاده کن، وگرنه متن پیش‌فرض
                back_text = admin_card.back_text if admin_card else 'نکته بالینی ثبت شده از تست'

                # ایجاد یا دریافت فلش‌کارت شخصی برای کاربر با متن واقعی ادمین
                Flashcard.objects.get_or_create(
                    user=request.user,
                    drug_name=drug_name,
                    defaults={
                        'front_text': drug_name,
                        'back_text': back_text,
                        'box_level': 1
                    }
                )
        else:
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
    # فلش‌کارت‌های عمومی ادمین (مرجع داروهای عرصه ۱)
    admin_cards = Flashcard.objects.filter(user=None).order_by('-id')

    # فلش‌کارت‌های اختصاصی/نقاط ضعف خود کاربر
    user_cards = Flashcard.objects.filter(user=request.user).order_by('-id')

    return render(request, 'drug_app_core/flashcards.html', {
        'admin_cards': admin_cards,
        'user_cards': user_cards
    })


@login_required
def ranking_view(request):
    profiles = UserProfile.objects.all().order_by('-coins', '-cup_score')
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

    context = {
        'users_count': users_count,
        'modules_count': modules_count,
        'questions_count': questions_count,
        'flashcards_count': flashcards_count,
    }
    return render(request, 'drug_app_core/custom_admin.html', context)


@staff_member_required
def admin_modules_view(request):
    modules = Module.objects.all().order_by('order')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)
        image = request.FILES.get('image')

        Module.objects.create(
            title=title, description=description, order=order, image=image
        )
        return redirect('admin_modules')
    return render(request, 'drug_app_core/admin_modules.html', {'modules': modules})


@staff_member_required
def admin_questions_view(request):
    questions = Question.objects.all().select_related('module')
    modules = Module.objects.all()
    if request.method == 'POST':
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
        return redirect('admin_questions')
    return render(
        request,
        'drug_app_core/admin_questions.html',
        {'questions': questions, 'modules': modules},
    )


@staff_member_required
def admin_users_view(request):
    profiles = UserProfile.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        coins_delta = int(request.POST.get('coins_delta', 0))
        profile = UserProfile.objects.get(id=user_id)
        profile.coins += coins_delta
        profile.save()
        return redirect('admin_users')
    return render(request, 'drug_app_core/admin_users.html', {'profiles': profiles})


@staff_member_required
def admin_flashcards_view(request):
    if request.method == 'POST':
        drug_name = request.POST.get('drug_name')
        back_text = request.POST.get('back_text')

        if drug_name and back_text:
            # ایجاد فلش‌کارت عمومی (بدون نیاز به اختصاص به یوزر خاص)
            Flashcard.objects.create(
                user=None,
                drug_name=drug_name,
                front_text=drug_name,
                back_text=back_text,
                box_level=1
            )
        return redirect('admin_flashcards')

    flashcards = Flashcard.objects.filter(user=None).order_by('-id')
    return render(request, 'drug_app_core/admin_flashcards.html', {'flashcards': flashcards})