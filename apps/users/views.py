import ast

import numpy as np
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from datetime import timedelta

from core import utils
from apps.users.models import User
from apps.users.serializers import UserSerializer


class PersonFaceViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return []

    @action(methods=['post'], detail=False)
    def face_identification(self, request):
        try:
            required_score = 70
            users = User.objects.all().order_by('id')
            users_em = [np.array(ast.literal_eval(user.embedding)) for user in users]
            embedding = request.data['embedding']
            embedding = np.array(ast.literal_eval(embedding))

            face_similarities = []
            for known_embedding in users_em:
                similarity = utils.cosine_similarity(embedding, known_embedding)
                similarity_percent = utils.get_percentage(similarity, threshold=0.5)
                face_similarities.append(similarity_percent)

            if len(face_similarities) > 0:
                best_match_index = np.argmax(face_similarities)
                similarity = face_similarities[best_match_index]
                if similarity >= required_score:
                    data = {"status": status.HTTP_200_OK, "verified": True,
                            "message": f"Xodim aniqlandi! [{similarity}%]", "score": similarity}
                else:
                    data = {"status": status.HTTP_404_NOT_FOUND, "verified": False,
                            "message": f"Aniqlanmadi! [{similarity}%]", "score": similarity}
            else:
                data = {"status": status.HTTP_400_BAD_REQUEST, "verified": False,
                        "message": f"Kamerada yuz topilmadi! [0%]", "score": 0}
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            data = {"status": status.HTTP_400_BAD_REQUEST, "verified": False, "message": str(e)}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StaffLoginView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)

            if not user:
                return Response(
                    {'error': 'Login yoki parol noto\'g\'ri'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)

            # Token ichiga qo'shimcha ma'lumot
            refresh['full_name'] = user.get_full_name()

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'staff': {
                    'id': user.id,
                    'fio': user.get_full_name(),
                },
            }, status=status.HTTP_200_OK)
        except Exception as e:
            data = {'error': str(e)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class GetAccessTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token kiritilmagan',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token
            access.set_exp(lifetime=timedelta(minutes=1))

            return Response({
                'success': True,
                'access_token': str(access),
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({
                'success': False,
                'message': str(e),
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    # Faqat tizimga kirgan foydalanuvchi logout qila oladi
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token taqdim etilmadi'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()  # Tokenni qora ro'yxatga kiritish

            return Response(
                {'message': 'Tizimdan muvaffaqiyatli chiqildi'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            # Token yaroqsiz, muddati o'tgan yoki allaqachon blacklistda
            return Response(
                {'error': "Token yaroqsiz yoki muddati o'tgan"},
                 status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Kutilmagan xatolik yuz berdi'},
                status=status.HTTP_400_BAD_REQUEST
            )
