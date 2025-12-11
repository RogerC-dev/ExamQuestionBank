import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from django.db.models import Sum, Count, Avg

from .models import Exam, MockExam, ExamResult, WrongQuestion
from question_bank.models import ExamQuestion, Question, QuestionOption, Subject, Bookmark
from question_bank.services.ai_service import ai_service
from question_bank.services.rag_service import rag_service
from .serializers import (
    ExamListSerializer,
    ExamDetailSerializer,
    ExamCreateUpdateSerializer,
    ExamQuestionCreateSerializer,
    ExamQuestionSerializer,
    MockExamSerializer,
    MockExamGenerateSerializer,
    ExamResultSerializer,
    ExamResultCreateSerializer,
    WrongQuestionSerializer
)

logger = logging.getLogger(__name__)


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

    @action(detail=False, methods=['get'], url_path='historical')
    def historical(self, request):
        exams = self.filter_queryset(self.get_queryset()).order_by('-created_at')
        page = self.paginate_queryset(exams)
        serializer = ExamListSerializer(page, many=True) if page is not None else ExamListSerializer(exams, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        exam = self.get_object()
        return Response({
            'exam_id': exam.id,
            'name': exam.name,
            'question_count': exam.exam_questions.count()
        })


class MockExamView(APIView):
    """模擬測驗生成與列表 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="產生模擬測驗",
        operation_description="透過 AI/題庫生成模擬測驗",
        request_body=MockExamGenerateSerializer,
        responses={201: MockExamSerializer()}
    )
    def post(self, request):
        serializer = MockExamGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        subject = data['subject']
        requested_question_count = data['question_count']
        difficulty = data['difficulty']
        reuse_question_bank = data['reuse_question_bank']
        topic = data.get('topic')
        exam_year = data.get('exam_year')
        time_limit = data.get('time_limit')
        name = data['name']

        exam = None

        if reuse_question_bank:
            selected_questions = self._select_questions_from_bank(subject, requested_question_count, difficulty, topic)
            if not selected_questions:
                return Response({"error": "題庫中沒有符合條件的題目"}, status=status.HTTP_404_NOT_FOUND)
            exam = self._create_exam_from_existing_questions(name, subject, selected_questions)
            question_count = len(selected_questions)
        else:
            generated_questions = self._generate_questions_with_ai(subject, requested_question_count, difficulty, exam_year, topic)
            if not generated_questions:
                return Response({"error": "無法生成題目，請稍後再試"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            exam = self._persist_generated_exam(name, subject, generated_questions)
            question_count = len(generated_questions)

        mock_exam = MockExam.objects.create(
            user=request.user,
            exam=exam,
            name=name,
            subject=subject,
            question_count=question_count,
            time_limit=time_limit,
            ai_generated=not reuse_question_bank
        )

        return Response(MockExamSerializer(mock_exam).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="取得模擬測驗列表",
        responses={200: MockExamSerializer(many=True)}
    )
    def get(self, request):
        mock_exams = MockExam.objects.filter(user=request.user).select_related('subject', 'exam').order_by('-generated_at')
        serializer = MockExamSerializer(mock_exams, many=True)
        return Response(serializer.data)

    def _generate_questions_with_ai(self, subject, question_count, difficulty, exam_year=None, topic=None):
        rag_context = rag_service.get_context_for_question_generation(subject.name, topic) if rag_service.is_configured() else None
        ai_result = ai_service.generate_mock_exam(
            subject=subject.name,
            question_count=question_count,
            difficulty=difficulty,
            exam_year=exam_year,
            rag_context=rag_context
        )
        return ai_result.get('questions', [])

    def _select_questions_from_bank(self, subject, question_count, difficulty, topic=None):
        filters = {
            'subject': subject,
            'question_type': '選擇題'
        }
        if difficulty:
            filters['difficulty'] = difficulty
        if topic:
            filters['content__icontains'] = topic

        return list(
            Question.objects.filter(**filters)
            .prefetch_related('options')
            .order_by('?')[:question_count]
        )

    def _create_exam_from_existing_questions(self, name, subject, questions):
        exam = Exam.objects.create(
            name=name,
            description=f"題庫抽選的 {subject.name} 模擬測驗",
            time_limit=None
        )

        with transaction.atomic():
            for index, question in enumerate(questions, start=1):
                ExamQuestion.objects.create(
                    exam=exam,
                    question=question,
                    order=index
                )
        return exam

    def _persist_generated_exam(self, name, subject, generated_questions):
        exam = Exam.objects.create(
            name=name,
            description=f"AI 生成的 {subject.name} 模擬測驗",
            time_limit=None
        )

        with transaction.atomic():
            for index, question_data in enumerate(generated_questions, start=1):
                question = Question.objects.create(
                    subject=subject,
                    content=question_data['content'],
                    question_type='選擇題',
                    difficulty='medium'
                )
                options = question_data.get('options', [])
                for opt in options:
                    QuestionOption.objects.create(
                        question=question,
                        content=opt['text'],
                        is_correct=opt.get('label') == question_data.get('correct_answer'),
                        order=ord(opt.get('label', 'A')) - 64
                    )

                ExamQuestion.objects.create(
                    exam=exam,
                    question=question,
                    order=index
                )
        return exam


class MockExamDetailView(APIView):
    """模擬測驗詳細 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得模擬測驗詳細資訊",
        responses={200: MockExamSerializer()}
    )
    def get(self, request, pk):
        mock_exam = self._get_mock_exam(pk, request.user)
        return Response(MockExamSerializer(mock_exam).data)

    @swagger_auto_schema(operation_summary="刪除模擬測驗")
    def delete(self, request, pk):
        mock_exam = self._get_mock_exam(pk, request.user)
        mock_exam.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_mock_exam(self, pk, user):
        try:
            mock_exam = MockExam.objects.select_related('subject', 'exam').get(pk=pk, user=user)
            return mock_exam
        except MockExam.DoesNotExist:
            raise NotFound({"error": "模擬測驗不存在"})


class ExamResultView(APIView):
    """考試結果 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="儲存考試結果",
        request_body=ExamResultCreateSerializer,
        responses={201: ExamResultSerializer()}
    )
    def post(self, request):
        serializer = ExamResultCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            exam = Exam.objects.get(pk=data['exam_id'])
        except Exam.DoesNotExist:
            return Response({"error": "考卷不存在"}, status=status.HTTP_404_NOT_FOUND)

        result = ExamResult.objects.create(
            user=request.user,
            exam=exam,
            score=data['score'],
            correct_count=data['correct_count'],
            total_count=data['total_count'],
            duration_seconds=data.get('duration_seconds')
        )

        # Save wrong questions
        for q_id in data.get('wrong_question_ids', []):
            wq, created = WrongQuestion.objects.get_or_create(
                user=request.user, question_id=q_id,
                defaults={'exam_result': result}
            )
            if not created:
                wq.wrong_count += 1
                wq.exam_result = result
                wq.reviewed = False
                wq.save()

        return Response(ExamResultSerializer(result).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="取得考試結果列表",
        responses={200: ExamResultSerializer(many=True)}
    )
    def get(self, request):
        results = ExamResult.objects.filter(user=request.user).select_related('exam').order_by('-completed_at')
        return Response(ExamResultSerializer(results, many=True).data)


class WrongQuestionView(APIView):
    """錯題本 API"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """取得錯題列表"""
        wrong_qs = WrongQuestion.objects.filter(user=request.user).select_related('question').order_by('-wrong_count', '-last_wrong_at')
        return Response(WrongQuestionSerializer(wrong_qs, many=True).data)

    def patch(self, request, pk):
        """標記錯題為已複習"""
        try:
            wq = WrongQuestion.objects.get(pk=pk, user=request.user)
            wq.reviewed = request.data.get('reviewed', True)
            wq.save()
            return Response(WrongQuestionSerializer(wq).data)
        except WrongQuestion.DoesNotExist:
            return Response({"error": "錯題不存在"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """刪除錯題記錄"""
        WrongQuestion.objects.filter(pk=pk, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookmarkView(APIView):
    """收藏題目 API"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """取得收藏列表"""
        bookmarks = Bookmark.objects.filter(user=request.user).select_related('question')
        data = [{
            'id': b.id,
            'question': b.question.id,
            'question_content': b.question.content,
            'question_subject': b.question.subject,
            'created_at': b.created_at
        } for b in bookmarks]
        return Response(data)

    def post(self, request):
        """收藏題目"""
        question_ids = request.data.get('question_ids', [])
        if isinstance(question_ids, int):
            question_ids = [question_ids]
        created = []
        for q_id in question_ids:
            obj, is_new = Bookmark.objects.get_or_create(user=request.user, question_id=q_id)
            if is_new:
                created.append(q_id)
        return Response({'bookmarked': created}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        """取消收藏"""
        q_id = pk or request.data.get('question_id')
        Bookmark.objects.filter(user=request.user, question_id=q_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExamStatsView(APIView):
    """考試統計 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="取得學習統計數據")
    def get(self, request):
        user = request.user
        results = ExamResult.objects.filter(user=user)

        total_questions = results.aggregate(total=Sum('total_count'))['total'] or 0
        correct_questions = results.aggregate(total=Sum('correct_count'))['total'] or 0
        exam_count = results.count()
        avg_score = results.aggregate(avg=Avg('score'))['avg'] or 0

        # 最近10次考試的正確率趨勢
        recent_results = results.order_by('-completed_at')[:10]
        accuracy_trend = [
            {
                'date': r.completed_at.strftime('%Y-%m-%d'),
                'accuracy': round(r.correct_count / r.total_count * 100, 1) if r.total_count > 0 else 0,
                'exam_name': r.exam.name,
                'exam_id': r.exam.id
            }
            for r in reversed(list(recent_results))
        ]

        total_bank = ExamQuestion.objects.count()
        wrong_count = WrongQuestion.objects.filter(user=user, reviewed=False).count()
        bookmark_count = Bookmark.objects.filter(user=user).count()

        # 常錯題目統計 - 取錯誤次數最多的前10題
        top_wrong_questions = WrongQuestion.objects.filter(
            user=user
        ).select_related('question').order_by('-wrong_count')[:10]

        top_wrong = [
            {
                'question_id': wq.question.id,
                'question_content': wq.question.content[:50] + '...' if len(wq.question.content) > 50 else wq.question.content,
                'question_subject': wq.question.subject,
                'wrong_count': wq.wrong_count,
                'reviewed': wq.reviewed
            }
            for wq in top_wrong_questions
        ]

        return Response({
            'total_answered': total_questions,
            'correct_answered': correct_questions,
            'total_bank': total_bank,
            'exam_count': exam_count,
            'average_score': round(avg_score, 1),
            'accuracy': round(correct_questions / total_questions * 100, 1) if total_questions > 0 else 0,
            'accuracy_trend': accuracy_trend,
            'wrong_count': wrong_count,
            'bookmark_count': bookmark_count,
            'top_wrong': top_wrong
        })
