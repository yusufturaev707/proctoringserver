from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from PIL import Image
from pyzbar.pyzbar import decode

from apps.barcode.forms import BarcodeUploadForm
from apps.barcode.models import BarcodeCode
from apps.exams.models import Test
from apps.users.models import BarcodeUpload


def decode_barcode(image_file):
    try:
        image_file.seek(0)
        img = Image.open(image_file)
        barcodes = decode(img)
        return barcodes[0].data.decode('utf-8') if barcodes else None
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
                sent = BarcodeCode.objects.filter(**filter_params, is_sent=True).count()
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
