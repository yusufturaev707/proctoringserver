import ast

import numpy as np
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

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
                    data = {"status": status.HTTP_200_OK, "verified": True, "message": f"Xodim aniqlandi! [{similarity}%]", "score": similarity}
                else:
                    data = {"status": status.HTTP_404_NOT_FOUND, "verified": False, "message": f"Aniqlanmadi! [{similarity}%]", "score": similarity}
            else:
                data = {"status": status.HTTP_400_BAD_REQUEST, "verified": False, "message": f"Kamerada yuz topilmadi! [0%]", "score": 0}
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            data = {"status": status.HTTP_400_BAD_REQUEST, "verified": False, "message": str(e)}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
