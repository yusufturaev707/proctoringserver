import time

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.exams.models import Test
from apps.exams.serializers import TestSerializer
from core.api_service import TestAPIClient


class LoadTestsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Test.objects.filter(status=1).order_by('-id')
            serializer = TestSerializer(queryset, many=True)

            data = {
                "status": "success",
                "data": serializer.data,
                "message": "Testlar ro'yxati muvaffaqiyatli yuklab olindi!"
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"XXX: {e}")
            data = {"status": "error", "data": None, "message": str(e)}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CheckCandidateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            imei = request.GET.get('imei')
            test_key = request.GET.get('test_key')
            
            if not imei:
                response_data = {"status": False, "message": "IMEI kiritilmadi!"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if not test_key:
                response_data = {"status": False, "message": "Test tanlanmadi!"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # MinScore tekshiruvi

            
            # Test mavjudligini tekshirish
            test = Test.objects.filter(key=test_key).first()
            if not test:
                response_data = {"status": False, "message": "Test topilmadi!"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            # External api ga bog'lanish
            student_api = TestAPIClient()
            data = student_api.verify_candidate(imei, test.key)

            if data.get('status') != 1:
                response_data = {"status": False, "message": str(data["message"])}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            item = data.get('data', {})
            response_data = {
                "status": item['status'],
                "image_base64": item.get('image_base64', ''),
                "imei": item.get('imie', ''),
                "test_link": item.get('test_link', ''),
                "message": item.get('message', '123')
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            response_data = {"status": False, "message": f"External API server bilan bog'lanishda xatolik: {e}"}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            response_data = {"status": False, "message": str(e)}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)