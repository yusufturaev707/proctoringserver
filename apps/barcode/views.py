from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from PIL import Image
from pyzbar.pyzbar import decode

from apps.barcode.forms import BarcodeUploadForm
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


@login_required
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

                obj, created = BarcodeUpload.objects.update_or_create(
                    uploaded_by=request.user,
                    exam=form.cleaned_data['exam'],
                    exam_date=form.cleaned_data['exam_date'],
                    smena=form.cleaned_data['smena'],
                    region=user_region,
                    defaults={'image': image_file, 'code': code}
                )

                msg = "Muvaffaqiyatli yuklandi" if created else "Muvaffaqiyatli yangilandi"
                return JsonResponse({'message': msg, 'code': code}, status=200)

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
