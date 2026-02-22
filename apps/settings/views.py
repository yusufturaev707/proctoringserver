import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.coco_class.models import HotKeyboardKey
from apps.settings.models import (AllowPublicIp, ExitPassword, )
from core.utils import validate_ip


class CheckAllowPublicIpAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            ip_address = request.GET.get('ip_address', '')

            if not validate_ip(ip_address):
                response_data = {"status": False, "message": "Ruxsat yo'q!!!"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            is_active = AllowPublicIp.objects.filter(ip_address=ip_address, is_active=True).exists()
            if not is_active:
                response_data = {"status": False, "message": "Ruxsat yo'q!"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            quit_password = '123'
            hot_keys = ['print screen']

            quit_password_obs = ExitPassword.objects.filter(is_active=True)
            if quit_password_obs.exists():
                quit_password = quit_password_obs.first().password

            hot_keys_obs = HotKeyboardKey.objects.filter(is_active=True).order_by('id')
            if hot_keys_obs.exists():
                for hot_key in hot_keys_obs:
                    hot_keys.append(hot_key.code)

            response_data = {
                "status": True,
                "quit_password": quit_password,
                "hot_keys": hot_keys,
                "message": f"Ruxsat bor."
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            response_data = {"status": False, "message": f"Javob yo'q."}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            import traceback
            traceback.print_exc()
            response_data = {"status": False, "message": "Xatolik yuz berdi."}
            print(f"Exception: {e}")
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
