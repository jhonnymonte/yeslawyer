import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Prompt
from .serializers import PromptCreateSerializer, PromptResponseSerializer
from .services.embedding_index import embedding_index
from .services.llm_provider import LLMProvider
from .throttles import BurstPerSecondThrottle, SustainedPerMinuteThrottle

log = logging.getLogger("prompts")


class CreatePromptView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = (BurstPerSecondThrottle, SustainedPerMinuteThrottle)

    @extend_schema(
        request=PromptCreateSerializer,
        responses=PromptResponseSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value={"prompt": "Hello, world!", "websocket": False},
                request_only=True,
                response_only=False,
            )
        ],
    )
    def post(self, request):
        ser = PromptCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        prompt_text = ser.validated_data["prompt"]
        use_ws = ser.validated_data.get("websocket", False)

        llm = LLMProvider()
        response_text = llm.generate(prompt_text)

        with transaction.atomic():
            obj = Prompt.objects.create(
                user=request.user, prompt=prompt_text, response=response_text
            )
            embedding_index.add(obj.id, obj.prompt)

        data = PromptResponseSerializer(obj).data

        if use_ws:
            try:
                channel_layer = get_channel_layer()
                group_name = f"user_{request.user.id}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {"type": "prompt.message", "event": "prompt_completed", "data": data},
                )
            except Exception as e:
                log.exception("websocket_send_failed: %s", e)

        log.info("prompt_created", extra={"user_id": request.user.id, "prompt_id": obj.id})
        return Response(data, status=status.HTTP_201_CREATED)


class SimilarPromptsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Texto del prompt a buscar (obligatorio).",
                required=True,
            ),
            OpenApiParameter(
                name="k",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Cantidad de resultados similares a devolver (por defecto: 5).",
                required=False,
                default=5,
            ),
        ],
        responses={
            200: PromptResponseSerializer(many=True),
            400: OpenApiExample(
                "Missing query param",
                value={"detail": "Missing ?q="},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                "Example request",
                value={"q": "Hello", "k": 3},
                request_only=True,
            )
        ],
        description="Busca prompts similares en el índice FAISS según el texto proporcionado en `q`.",
    )
    def get(self, request):
        query = request.query_params.get("q") or request.query_params.get("prompt")
        k = int(request.query_params.get("k", 5))
        if not query:
            return Response({"detail": "Missing ?q="}, status=400)

        ids = embedding_index.search(query, k=k)
        qs = Prompt.objects.filter(id__in=ids).order_by("-created_at")
        data = PromptResponseSerializer(qs, many=True).data
        return Response({"query": query, "results": data}, status=200)
