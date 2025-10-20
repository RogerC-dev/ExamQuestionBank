from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services.pdf_parser import PDFParser
from .models import Question
from .serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateUpdateSerializer
)


class ExtractExamPDFView(APIView):
    """
    將試卷 PDF 匯出為 json 並回傳
    """
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="上傳試卷 PDF 並轉換為 JSON",
        manual_parameters=[
            openapi.Parameter(
                name='file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='試卷 PDF 檔案'
            )
        ],
        responses={200: "轉換成功"}
    )
    def post(self, request):
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({"error": "請上傳 PDF 檔案"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            questions = PDFParser.parse_questions(pdf_file)
            return Response({
                "count": len(questions["questions"]),
                "level": questions["level"],
                "category": questions["category"],
                "subject": questions["subject"],
                "time_length": questions["time_length"],
                "questions": questions["questions"],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExtractAnswerPDFView(APIView):
    """
    將試卷答案 PDF 匯出答案並回傳
    """
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="上傳答案 PDF 並轉換為 JSON",
        manual_parameters=[
            openapi.Parameter(
                name='file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='試卷答案 PDF 檔案'
            )
        ],
        responses={200: "轉換成功"}
    )
    def post(self, request):
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({"error": "請上傳 PDF 檔案"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answers = PDFParser.parse_answers(pdf_file)
            return Response({
                "count": len(answers["answers"]),
                "notes": answers["notes"],
                "answers": answers["answers"],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    題目的 CRUD API

    list: 取得題目列表（簡化版）
    retrieve: 取得單一題目詳細資訊（包含選項、標籤）
    create: 建立新題目
    update: 更新題目
    partial_update: 部分更新題目
    destroy: 刪除題目
    """
    queryset = Question.objects.all().prefetch_related('options', 'tags').select_related('created_by')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """根據不同的動作回傳不同的序列化器"""
        if self.action == 'list':
            return QuestionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return QuestionCreateUpdateSerializer
        return QuestionDetailSerializer

    @swagger_auto_schema(
        operation_summary="取得題目列表",
        operation_description="回傳簡化版的題目列表",
        responses={200: QuestionListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="取得題目詳細資訊",
        operation_description="回傳完整的題目資訊，包含選項和標籤",
        responses={200: QuestionDetailSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="建立新題目",
        operation_description="建立一個新題目，可同時建立選項和標籤",
        request_body=QuestionCreateUpdateSerializer,
        responses={201: QuestionDetailSerializer()}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        # 使用 QuestionDetailSerializer 回傳完整資訊
        response_serializer = QuestionDetailSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="更新題目",
        operation_description="完整更新題目資訊",
        request_body=QuestionCreateUpdateSerializer,
        responses={200: QuestionDetailSerializer()}
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        # 使用 QuestionDetailSerializer 回傳完整資訊
        response_serializer = QuestionDetailSerializer(question)
        return Response(response_serializer.data)

    @swagger_auto_schema(
        operation_summary="部分更新題目",
        operation_description="部分更新題目資訊",
        request_body=QuestionCreateUpdateSerializer,
        responses={200: QuestionDetailSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="刪除題目",
        operation_description="刪除指定的題目",
        responses={204: "刪除成功"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)