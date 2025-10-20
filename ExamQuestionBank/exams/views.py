from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Exam
from question_bank.models import ExamQuestion
from .serializers import (
    ExamListSerializer,
    ExamDetailSerializer,
    ExamCreateUpdateSerializer,
    ExamQuestionCreateSerializer,
    ExamQuestionSerializer
)


class ExamViewSet(viewsets.ModelViewSet):
    """
    考卷的 CRUD API

    list: 取得考卷列表
    retrieve: 取得單一考卷詳細資訊（包含所有題目）
    create: 建立新考卷
    update: 更新考卷
    partial_update: 部分更新考卷
    destroy: 刪除考卷
    add_question: 新增題目到考卷
    remove_question: 從考卷移除題目
    update_question: 更新考卷中的題目資訊（順序、配分）
    """
    queryset = Exam.objects.all().prefetch_related('exam_questions__question')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """根據不同的動作回傳不同的序列化器"""
        if self.action == 'list':
            return ExamListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ExamCreateUpdateSerializer
        return ExamDetailSerializer

    @swagger_auto_schema(
        operation_summary="取得考卷列表",
        operation_description="回傳所有考卷的列表",
        responses={200: ExamListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="取得考卷詳細資訊",
        operation_description="回傳完整的考卷資訊，包含所有題目",
        responses={200: ExamDetailSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="建立新考卷",
        operation_description="建立一個新考卷",
        request_body=ExamCreateUpdateSerializer,
        responses={201: ExamDetailSerializer()}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()

        # 使用 ExamDetailSerializer 回傳完整資訊
        response_serializer = ExamDetailSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="更新考卷",
        operation_description="完整更新考卷資訊",
        request_body=ExamCreateUpdateSerializer,
        responses={200: ExamDetailSerializer()}
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()

        # 使用 ExamDetailSerializer 回傳完整資訊
        response_serializer = ExamDetailSerializer(exam)
        return Response(response_serializer.data)

    @swagger_auto_schema(
        operation_summary="部分更新考卷",
        operation_description="部分更新考卷資訊",
        request_body=ExamCreateUpdateSerializer,
        responses={200: ExamDetailSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="刪除考卷",
        operation_description="刪除指定的考卷",
        responses={204: "刪除成功"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='post',
        operation_summary="新增題目到考卷",
        operation_description="將一個題目新增到考卷中",
        request_body=ExamQuestionCreateSerializer,
        responses={201: ExamQuestionSerializer()}
    )
    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        """新增題目到考卷"""
        exam = self.get_object()
        serializer = ExamQuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 建立考卷-題目關聯
        exam_question = ExamQuestion.objects.create(
            exam=exam,
            **serializer.validated_data
        )

        response_serializer = ExamQuestionSerializer(exam_question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='delete',
        operation_summary="從考卷移除題目",
        operation_description="從考卷中移除指定的題目",
        manual_parameters=[
            openapi.Parameter(
                'exam_question_id',
                openapi.IN_QUERY,
                description="考卷題目關聯 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={204: "刪除成功"}
    )
    @action(detail=True, methods=['delete'])
    def remove_question(self, request, pk=None):
        """從考卷移除題目"""
        exam = self.get_object()
        exam_question_id = request.query_params.get('exam_question_id')

        if not exam_question_id:
            return Response(
                {"error": "需要提供 exam_question_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            exam_question = ExamQuestion.objects.get(id=exam_question_id, exam=exam)
            exam_question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ExamQuestion.DoesNotExist:
            return Response(
                {"error": "考卷題目不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        method='patch',
        operation_summary="更新考卷中的題目資訊",
        operation_description="更新考卷中題目的順序或配分",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'exam_question_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='考卷題目關聯 ID'),
                'order': openapi.Schema(type=openapi.TYPE_INTEGER, description='題目順序'),
                'points': openapi.Schema(type=openapi.TYPE_NUMBER, description='配分'),
            },
            required=['exam_question_id']
        ),
        responses={200: ExamQuestionSerializer()}
    )
    @action(detail=True, methods=['patch'])
    def update_question(self, request, pk=None):
        """更新考卷中的題目資訊（順序、配分）"""
        from django.db import transaction

        exam = self.get_object()
        exam_question_id = request.data.get('exam_question_id')

        if not exam_question_id:
            return Response(
                {"error": "需要提供 exam_question_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            exam_question = ExamQuestion.objects.get(id=exam_question_id, exam=exam)

            # 如果要更新順序，需要處理 unique constraint
            if 'order' in request.data:
                new_order = request.data['order']
                old_order = exam_question.order

                if new_order != old_order:
                    with transaction.atomic():
                        # 策略：先將所有題目的 order 設為負數以避免 unique constraint 衝突
                        all_questions = list(ExamQuestion.objects.filter(exam=exam).select_for_update().order_by('order'))

                        # 步驟1：先將所有題目設為負數（臨時占位，避免衝突）
                        for eq in all_questions:
                            eq.order = -eq.order
                            eq.save()

                        # 步驟2：重新計算並設置新的順序
                        for eq in all_questions:
                            current_order = -eq.order  # 轉回正數

                            if eq.id == exam_question_id:
                                # 當前要修改的題目
                                eq.order = new_order
                            elif new_order < old_order:
                                # 向前移動：[new_order, old_order) 之間的題目 +1
                                if current_order >= new_order and current_order < old_order:
                                    eq.order = current_order + 1
                                else:
                                    eq.order = current_order
                            else:
                                # 向後移動：(old_order, new_order] 之間的題目 -1
                                if current_order > old_order and current_order <= new_order:
                                    eq.order = current_order - 1
                                else:
                                    eq.order = current_order

                            eq.save()

            # 更新配分
            if 'points' in request.data:
                exam_question.refresh_from_db()
                exam_question.points = request.data['points']
                exam_question.save()

            exam_question.refresh_from_db()
            response_serializer = ExamQuestionSerializer(exam_question)
            return Response(response_serializer.data)
        except ExamQuestion.DoesNotExist:
            return Response(
                {"error": "考卷題目不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
