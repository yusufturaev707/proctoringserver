from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import IntegrityError
import cv2
import numpy as np
import zxingcpp

from apps.barcode.forms import BarcodeUploadForm
from apps.barcode.models import BarcodeCode
from apps.exams.models import Test
from apps.regions.models import Region
from apps.users.models import BarcodeUpload


def _try_decode(image):
    """Bitta rasmda barcode o'qishga urinish."""
    results = zxingcpp.read_barcodes(image)
    return results[0].text if results else None


def _preprocess_variants(gray):
    """Har xil shart-sharoit uchun rasmning preprocessed variantlarini yaratish."""
    variants = []

    # 1. CLAHE вЂ” notekis yorug'lik (buklangan qog'oz: bir tarafi yorug', bir tarafi soya)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))

    # 2. Adaptive threshold вЂ” kuchli soya/yorug'lik farqi uchun
    #    Har bir kichik hududni alohida threshold qiladi
    variants.append(
        cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY, 51, 15)
    )

    # 3. Yaltiroq plyonka uchun вЂ” Gaussian blur yaltiroqni yumshatadi,
    #    keyin Otsu threshold optimal chegarani topadi
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)

    # 4. Ingichka/uzilgan chiziqlar uchun вЂ” morphological closing
    #    Uzilgan barcode chiziqlarini yopib, qayta ulaydi
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
    closed = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel, iterations=2)
    variants.append(closed)

    # 5. Kuchli CLAHE вЂ” juda past kontrast (xira rasm) uchun
    clahe_strong = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
    variants.append(clahe_strong.apply(gray))

    return variants


def decode_barcode(image_file):
    try:
        image_file.seek(0)
        file_bytes = np.frombuffer(image_file.read(), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Avval oddiy kulrang rasmda urinish (tez)
        result = _try_decode(gray)
        if result:
            return result

        # Har xil preprocessing variantlarini sinash
        for variant in _preprocess_variants(gray):
            result = _try_decode(variant)
            if result:
                return result

        # Oxirgi urinish: rasmni 2x kattalashtirish (juda kichik barcode uchun)
        h, w = gray.shape
        upscaled = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        for variant in [upscaled] + _preprocess_variants(upscaled):
            result = _try_decode(variant)
            if result:
                return result

        return None
    except Exception:
        return None


@login_required(login_url='login-page')
def barcode_scan(request):
    if request.method == 'POST':
        form = BarcodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user_region = getattr(request.user, 'region', None)
                if not user_region:
                    return JsonResponse(
                        {'detail': "Profilingizda 'Region' ko'rsatilmagan!"}, status=400
                    )

                image_file = request.FILES.get('image')
                code = decode_barcode(image_file)

                if not code:
                    return JsonResponse(
                        {'detail': 'Rasmda barcode topilmadi.'}, status=400
                    )

                # Barcode qiymatini integer ga tekshirish va convert qilish
                try:
                    code = int(code)
                except (ValueError, TypeError):
                    return JsonResponse(
                        {'detail': f'Barcode qiymati "{code}" butun son emas!'}, status=400
                    )

                exam = form.cleaned_data['exam']
                exam_date = form.cleaned_data['exam_date']
                smena = form.cleaned_data['smena']

                # BarcodeCode da bor-yo'qligini tekshirish
                # barcode_code = BarcodeCode.objects.filter(
                #     code=code,
                #     exam=exam,
                #     exam_date=exam_date,
                #     smena=smena,
                #     region=user_region,
                # ).first()
                #
                # if not barcode_code:
                #     # BarcodeUpload ga is_valid=False bilan saqlash
                #     BarcodeUpload.objects.update_or_create(
                #         uploaded_by=request.user,
                #         exam=exam,
                #         exam_date=exam_date,
                #         smena=smena,
                #         region=user_region,
                #         code=code,
                #         defaults={'image': image_file, 'is_valid': False}
                #     )
                #     return JsonResponse({
                #         'detail': f'Kod "{code}" mavjud emas!'
                #     }, status=400)
                #
                # if barcode_code.is_sent:
                #     return JsonResponse({
                #         'detail': f'Kod "{code}" allaqachon yuborilgan.'
                #     }, status=400)
                #
                # # BarcodeCode ni is_sent=True qilish
                # barcode_code.is_sent = True
                # barcode_code.save(update_fields=['is_sent', 'updated_at'])

                # BarcodeUpload ga saqlash (is_valid=True)
                obj, created = BarcodeUpload.objects.update_or_create(
                    uploaded_by=request.user,
                    exam=exam,
                    exam_date=exam_date,
                    smena=smena,
                    region=user_region,
                    code=code,
                    defaults={'image': image_file, 'is_valid': False}
                )

                # Statistika: shu parametrlar bo'yicha
                filter_params = dict(
                    exam=exam, exam_date=exam_date,
                    smena=smena, region=user_region,
                )
                # total = BarcodeCode.objects.filter(**filter_params).count()
                total = 0
                # sent = BarcodeCode.objects.filter(**filter_params, is_sent=True).count()
                sent = BarcodeUpload.objects.filter(**filter_params).count()
                # remaining = total - sent
                remaining = 0

                msg = "Muvaffaqiyatli yuklandi" if created else "Muvaffaqiyatli yangilandi"
                return JsonResponse({
                    'message': msg,
                    'code': code,
                    'is_valid': True,
                    'stats': {
                        'total': total,
                        'sent': sent,
                        'remaining': remaining,
                    }
                }, status=200)

            except IntegrityError as e:
                return JsonResponse(
                    {'detail': f"Ma'lumotlar bazasida xatolik: {str(e)}"}, status=500
                )
            except Exception as e:
                return JsonResponse(
                    {'detail': f"Server xatosi: {str(e)}"}, status=500
                )

        return JsonResponse({'detail': form.errors.as_text()}, status=400)

    exams = Test.objects.filter(status=True).order_by('id')
    return render(request, 'barcode/scan.html', {
        'exams': exams,
        'form': BarcodeUploadForm(),
    })


@login_required(login_url='login-page')
def barcode_stats(request):
    """Tanlangan parametrlar bo'yicha statistikani qaytaradi."""
    exam_id = request.GET.get('exam')
    exam_date = request.GET.get('exam_date')
    smena = request.GET.get('smena')

    user_region = getattr(request.user, 'region', None)
    if not all([exam_id, exam_date, smena, user_region]):
        return JsonResponse({'total': 0, 'sent': 0, 'remaining': 0})

    filter_params = dict(
        exam_id=exam_id, exam_date=exam_date,
        smena=smena, region=user_region,
    )
    total = BarcodeCode.objects.filter(**filter_params).count()
    sent = BarcodeCode.objects.filter(**filter_params, is_sent=True).count()

    return JsonResponse({
        'total': total,
        'sent': sent,
        'remaining': total - sent,
    })


@staff_member_required
def admin_generate_codes(request):
    """Admin panelda BarcodeCode larni interval bo'yicha generate qilish."""
    if request.method == 'POST':
        exam_id = request.POST.get('exam')
        exam_date = request.POST.get('exam_date')
        smena = request.POST.get('smena')
        region_id = request.POST.get('region')
        range_start = request.POST.get('range_start')
        range_end = request.POST.get('range_end')

        if not all([exam_id, exam_date, smena, region_id, range_start, range_end]):
            messages.error(request, "Barcha maydonlarni to'ldiring!")
            return redirect(reverse_url())

        # Faqat raqamlardan iborat ekanligini tekshirish
        range_start = range_start.strip()
        range_end = range_end.strip()
        if not range_start.isdigit() or not range_end.isdigit():
            messages.error(request, "Interval faqat musbat butun son bo'lishi kerak!")
            return redirect(reverse_url())

        start = int(range_start)
        end = int(range_end)

        if start > end:
            messages.error(request, "Interval noto'g'ri: boshlanish <= tugash bo'lishi kerak!")
            return redirect(reverse_url())

        if end - start + 1 > 100000:
            messages.error(request, "Bir martada 100 000 dan ortiq kod yaratish mumkin emas!")
            return redirect(reverse_url())

        exam = Test.objects.filter(id=exam_id).first()
        region = Region.objects.filter(id=region_id).first()

        if not exam or not region:
            messages.error(request, "Imtihon yoki viloyat topilmadi!")
            return redirect(reverse_url())

        # Kodlarni generatsiya (integer sifatida)
        all_codes = list(range(start, end + 1))

        # Mavjud kodlarni olish (dublikatni oldini olish)
        existing_codes = set(
            BarcodeCode.objects.filter(
                exam=exam, exam_date=exam_date,
                smena=smena, region=region,
                code__in=all_codes,
            ).values_list('code', flat=True)
        )

        new_codes = []
        for code_val in all_codes:
            if code_val not in existing_codes:
                new_codes.append(BarcodeCode(
                    exam=exam,
                    exam_date=exam_date,
                    smena=smena,
                    region=region,
                    code=code_val,
                ))

        if new_codes:
            BarcodeCode.objects.bulk_create(new_codes)

        created_count = len(new_codes)
        skipped_count = (end - start + 1) - created_count
        msg = f"{created_count} ta kod yaratildi."
        if skipped_count > 0:
            msg += f" {skipped_count} ta allaqachon mavjud bo'lgani o'tkazib yuborildi."
        messages.success(request, msg)

        return redirect('admin:barcode_barcodecode_changelist')

    # GET — formani ko'rsatish
    exams = Test.objects.filter(status=True).order_by('id')
    regions = Region.objects.filter(status=True).order_by('name')
    return render(request, 'admin/barcode/generate_codes.html', {
        'exams': exams,
        'regions': regions,
        'title': 'Barcode kodlar generatsiya qilish',
    })


def reverse_url():
    from django.urls import reverse
    return reverse('admin:barcode_barcodecode_generate')


@staff_member_required
def admin_validate_uploads(request):
    """BarcodeUpload larni BarcodeCode jadvaliga solishtirish va is_sent/is_valid yangilash."""
    if request.method == 'POST':
        exam_id = request.POST.get('exam')
        exam_date = request.POST.get('exam_date')
        smena = request.POST.get('smena')
        region_id = request.POST.get('region')

        if not all([exam_id, exam_date, smena, region_id]):
            messages.error(request, "Barcha maydonlarni to'ldiring!")
            return redirect('admin:users_barcodeupload_validate')

        filter_params = dict(
            exam_id=exam_id, exam_date=exam_date,
            smena=smena, region_id=region_id,
        )

        uploads = BarcodeUpload.objects.filter(**filter_params)
        if not uploads.exists():
            messages.warning(request, "Tanlangan parametrlarga mos yuklama topilmadi.")
            return redirect('admin:users_barcodeupload_validate')

        # BarcodeCode dagi barcha kodlarni set ga olish
        valid_codes = set(
            BarcodeCode.objects.filter(**filter_params)
            .values_list('code', flat=True)
        )

        valid_count = 0
        invalid_count = 0

        for upload in uploads:
            if upload.code in valid_codes:
                # Kod mavjud — is_valid=True, BarcodeCode.is_sent=True
                if not upload.is_valid:
                    upload.is_valid = True
                    upload.save(update_fields=['is_valid', 'updated_at'])
                BarcodeCode.objects.filter(
                    code=upload.code, **filter_params,
                ).update(is_sent=True)
                valid_count += 1
            else:
                # Kod mavjud emas — is_valid=False
                if upload.is_valid:
                    upload.is_valid = False
                    upload.save(update_fields=['is_valid', 'updated_at'])
                invalid_count += 1

        msg = f"Tekshiruv yakunlandi: {valid_count} ta to'g'ri, {invalid_count} ta noto'g'ri."
        messages.success(request, msg)
        return redirect('admin:users_barcodeupload_changelist')

    # GET — formani ko'rsatish
    exams = Test.objects.filter(status=True).order_by('id')
    regions = Region.objects.filter(status=True).order_by('name')
    return render(request, 'admin/barcode/validate_uploads.html', {
        'exams': exams,
        'regions': regions,
        'title': 'Barcode yuklamalarni tekshirish',
    })
