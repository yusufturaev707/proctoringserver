from celery.result import AsyncResult

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from apps.notification.serializers import (
    WarningNotificationSerializer,
    BulkWarningNotificationSerializer,
)
from apps.notification.tasks import process_bulk_warnings


class SendWarningAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = WarningNotificationSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'message': 'Ogohlantirish saqlandi'},
                    status=status.HTTP_201_CREATED
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': f'Xatolik yuz berdi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkWarningThrottle(AnonRateThrottle):
    rate = '100/min'


class BulkSendWarningAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [BulkWarningThrottle]

    def post(self, request):
        serializer = BulkWarningNotificationSerializer(data=request.data)

        if not serializer.is_valid():
            print(f"Serializer error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validatsiyadan o'tdi — Celery'ga yuborish
        warnings_data = serializer.validated_data['warnings']
        print(f"Warning data: {warnings_data}")
        # exam obyektlarini olib tashlaymiz (JSON serializable emas)
        clean_data = []
        for item in warnings_data:
            clean_item = {k: v for k, v in item.items() if k != 'exam'}
            clean_data.append(clean_item)

        task = process_bulk_warnings.delay(clean_data)

        return Response(
            {
                'task_id': task.id,
                'status': 'accepted',
                'message': f"{len(clean_data)} ta warning qabul qilindi, background'da saqlanmoqda.",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class BulkWarningTaskStatusAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        response_data = {
            'task_id': task_id,
            'status': result.status,
        }

        if result.successful():
            response_data['result'] = result.result
        elif result.failed():
            response_data['error'] = str(result.result)

        return Response(response_data)
