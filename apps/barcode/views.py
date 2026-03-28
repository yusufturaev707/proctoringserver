from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import cv2
import numpy as np
import zxingcpp

from apps.barcode.forms import BarcodeUploadForm
from apps.barcode.models import BarcodeCode
from apps.exams.models import Test
from apps.users.models import BarcodeUpload


def _try_decode(image):
    """Bitta rasmda barcode o'qishga urinish."""
    results = zxingcpp.read_barcodes(image)
    return results[0].text if results else None


def _preprocess_variants(gray):
    """Har xil shart-sharoit uchun rasmning preprocessed variantlarini yaratish."""
    variants = []

    # 1. CLAHE — notekis yorug'lik (buklangan qog'oz: bir tarafi yorug', bir tarafi soya)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))

    # 2. Adaptive threshold — kuchli soya/yorug'lik farqi uchun
    #    Har bir kichik hududni alohida threshold qiladi
    variants.append(
        cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY, 51, 15)
    )

    # 3. Yaltiroq plyonka uchun — Gaussian blur yaltiroqni yumshatadi,
    #    keyin Otsu threshold optimal chegarani topadi
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)

    # 4. Ingichka/uzilgan chiziqlar uchun — morphological closing
    #    Uzilgan barcode chiziqlarini yopib, qayta ulaydi
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
    closed = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel, iterations=2)
    variants.append(closed)

    # 5. Kuchli CLAHE — juda past kontrast (xira rasm) uchun
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
                #     return JsonResponse({
                #         'detail': f'Kod "{code}" tanlangan parametrlarga mos kelmadi.'
                #     }, status=400)
                #
                # if barcode_code.is_sent:
                #     return JsonResponse({
                #         'detail': f'Kod "{code}" allaqachon yuborilgan.'
                #     }, status=400)

                # BarcodeCode ni is_sent=True qilish
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
                    defaults={'image': image_file, 'is_valid': True}
                )

                # Statistika: shu parametrlar bo'yicha
                filter_params = dict(
                    exam=exam, exam_date=exam_date,
                    smena=smena, region=user_region,
                )
                total = BarcodeCode.objects.filter(**filter_params).count()
                # sent = BarcodeCode.objects.filter(**filter_params, is_sent=True).count()
                sent = BarcodeUpload.objects.filter(**filter_params).count()
                remaining = total - sent

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
