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
            print(imei)
            test_key = request.GET.get('test_key')
            if not imei:
                data = {"status": "error", "data": None, "message": "Pinfl kiritilmadi!"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if not test_key:
                data = {"status": "error", "data": None, "message": "Test tanlanmadi!"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            score = MinScore.objects.all().first()

            res = requests.get(f"http://127.0.0.1:5000/api/check-candidate-exam/",
                               json={"imei": imei, "test_key": test_key}, timeout=5)
            data_res = res.json()

            if res.status_code in [400, 404, 401, 405, 500]:
                data = {
                    "status": "error",
                    "score": 0,
                    "data": None,
                    "message": f"{data_res['message']}"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            elif res.status_code == 200:
                data = {
                    "status": "success",
                    "score": score.score,
                    "data": {
                        "image_base64": data_res['data']['image_base64'],
                        "imei": data_res['data']['imei'],
                        "test_link": data_res['data']['test_link'],
                        "is_enrolled": data_res['data']['is_enrolled'],
                        "is_finished": data_res['data']['is_finished'],
                        "is_cheating": data_res['data']['is_cheating'],
                        "is_blocked": data_res['data']['is_blocked'],
                        "warning_text": Test.objects.filter(key=test_key).first().warning_instructions.strip(),
                    }
                }
                return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            data = {"status": "error",  "data": None, "message": str(e)}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)