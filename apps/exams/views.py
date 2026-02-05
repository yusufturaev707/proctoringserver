import requests
from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.exams.models import Test
from apps.exams.serializers import TestSerializer
from apps.settings.models import MinScore



class LoadTestsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            queryset = Test.objects.filter(status=True).order_by('-id')
            serializer = TestSerializer(queryset, many=True)
            data = {
                "status": "success",
                "data": serializer.data,
                "message": "Testlar ro'yxati muvaffaqiyatli yuklab olindi!"
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            data = {"status": "error", "data": None, "message": str(e)}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CheckCandidateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            imei = request.GET.get('imei')
            test_key = request.GET.get('test_key')
            
            if not imei:
                data = {"status": "error", "data": None, "message": "IMEI kiritilmadi!"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if not test_key:
                data = {"status": "error", "data": None, "message": "Test tanlanmadi!"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
            # MinScore tekshiruvi
            score = MinScore.objects.all().first()
            if not score:
                print("MinScore mavjud emas, default qiymat o'rnatilmoqda.")
                score = MinScore(score=50)
            
            # Test mavjudligini tekshirish
            test = Test.objects.filter(key=test_key).first()
            if not test:
                data = {"status": "error", "data": None, "message": "Test topilmadi!"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            # Flask API ga so'rov
            res = requests.get(
                f"https://apiv1.uzbmb.uz/site/proctoring-person-exam?imie={imei}",
                timeout=5
            )
            data_res = res.json()
            print(data_res)
            if res.status_code in [400, 404, 401, 405, 403, 500]:
                data = {
                    "status": "error",
                    "score": 0,
                    "data": None,
                    "message": data_res.get('message', 'Xatolik yuz berdi')
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
            elif res.status_code == 200:
                response_status = data_res.get('status')
                if response_status != 1:
                    data = {
                        "status": "error",
                        "score": 0,
                        "data": None,
                        "message": data_res.get('message', 'Xatolik yuz berdi')
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                response_data = data_res.get('data', {})
                print(f"response_data: {response_data}")
                data = {
                    "status": response_data.get('status', False),
                    "score": int(score.score),
                    "data": {
                        "image_base64": response_data.get('image_base64', ''),
                        "imei": response_data.get('imie', ''),
                        "test_link": response_data.get('test_link', ''),
                        "is_enrolled": response_data.get('status', False),
                        "warning_text": response_data.get('message', 'Xatolik yuz berdi'),
                    }
                }
                print(f"data: {data}")
                return Response(data, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            print(f"Flask API xatosi: {str(e)}")
            data = {"status": "error", "data": None, "message": "Flask server bilan bog'lanishda xatolik"}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            data = {"status": "error", "data": None, "message": str(e)}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)