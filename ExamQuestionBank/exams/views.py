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

from .models import Exam, ExamResult, WrongQuestion
from question_bank.models import ExamQuestion, Question, QuestionOption, Subject, Bookmark
from .serializers import (
    ExamListSerializer,
    ExamDetailSerializer,
    ExamCreateUpdateSerializer,
    ExamQuestionCreateSerializer,
    ExamQuestionSerializer,
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """一般使用者只能看到自己的考卷,管理員可以看到所有"""
        user = self.request.user
        if user.is_staff:
            return Exam.objects.all().prefetch_related('exam_questions__question')
            
        # 若是 list 動作 (查詢我的考卷)，僅回傳自己建立的
        if self.action == 'list':
            return Exam.objects.filter(created_by=user).prefetch_related('exam_questions__question')

        # 其他動作 (retrieve, update, destroy 等)
        # 允許查詢管理員建立的公開考卷 (權限控制由 _has_permission 處理修改/刪除)
        from django.db.models import Q
        return Exam.objects.filter(
            Q(created_by=user) | Q(created_by_admin=True)
        ).prefetch_related('exam_questions__question')

    def get_serializer_class(self):
        """根據不同的動作回傳不同的序列化器"""
        if self.action == 'list':
            return ExamListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ExamCreateUpdateSerializer
        return ExamDetailSerializer
    
    def get_serializer_context(self):
        """添加 request 到序列化器 context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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
        
        # 自動設定 created_by 和 created_by_admin
        is_admin = request.user.is_staff or request.user.is_superuser
        exam = serializer.save(
            created_by=request.user,
            created_by_admin=is_admin
        )

        # 使用 ExamDetailSerializer 回傳完整資訊
        response_serializer = ExamDetailSerializer(exam, context={'request': request})
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
        
        # 檢查權限
        if not self._has_permission(instance):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限修改此考卷")
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()

        # 使用 ExamDetailSerializer 回傳完整資訊
        response_serializer = ExamDetailSerializer(exam, context={'request': request})
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
        instance = self.get_object()
        
        # 檢查權限
        if not self._has_permission(instance):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限刪除此考卷")
        
        return super().destroy(request, *args, **kwargs)
    
    def _has_permission(self, exam):
        """檢查使用者是否有權限操作此考卷"""
        user = self.request.user
        return user.is_staff or exam.created_by == user

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

    @action(detail=False, methods=['get'], url_path='practice-list')
    def practice_list(self, request):
        """獲取練習模式的考卷列表：管理員建立的考卷 + 使用者自己的考卷"""
        from django.db.models import Q
        user = request.user
        
        # 查詢條件：管理員建立的考卷 OR 使用者自己建立的考卷
        exams = Exam.objects.filter(
            Q(created_by_admin=True) | Q(created_by=user)
        ).prefetch_related('exam_questions__question').order_by('-created_at')
        
        page = self.paginate_queryset(exams)
        serializer = ExamListSerializer(
            page if page is not None else exams, 
            many=True, 
            context={'request': request}
        )
        
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

    @action(detail=False, methods=['get'])
    def by_question(self, request):
        """Get all exams that contain a specific question"""
        question_id = request.query_params.get('question_id')
        
        if not question_id:
            return Response(
                {"error": "question_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from question_bank.models import ExamQuestion
            exam_questions = ExamQuestion.objects.filter(question_id=question_id)
            exam_ids = exam_questions.values_list('exam_id', flat=True).distinct()
            exams = self.filter_queryset(self.get_queryset()).filter(id__in=exam_ids)
            serializer = ExamListSerializer(exams, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_questions(self, request):
        """Get all exams that contain any of the specified questions"""
        question_ids_str = request.query_params.get('question_ids')
        
        if not question_ids_str:
            return Response(
                {"error": "question_ids parameter is required (comma-separated IDs)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse comma-separated question IDs
            question_ids = [int(qid.strip()) for qid in question_ids_str.split(',') if qid.strip()]
            
            if not question_ids:
                return Response([])
            
            from question_bank.models import ExamQuestion
            exam_questions = ExamQuestion.objects.filter(question_id__in=question_ids)
            exam_ids = exam_questions.values_list('exam_id', flat=True).distinct()
            exams = self.filter_queryset(self.get_queryset()).filter(id__in=exam_ids)
            serializer = ExamListSerializer(exams, many=True)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {"error": "Invalid question_ids format. Expected comma-separated integers."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        from flashcards.models import Flashcard
        from question_bank.models import Note, Bookmark
        
        user = request.user
        
        # 預先查詢所有相關資料，避免 N+1
        wrong_qs = WrongQuestion.objects.filter(user=user).select_related('question').order_by('-wrong_count', '-last_wrong_at')
        
        # 取得所有錯題的 question_id
        question_ids = list(wrong_qs.values_list('question_id', flat=True))
        
        # 批次查詢使用者的 flashcard、bookmark、note
        flashcard_question_ids = set(Flashcard.objects.filter(user=user, question_id__in=question_ids).values_list('question_id', flat=True))
        bookmark_question_ids = set(Bookmark.objects.filter(user=user, question_id__in=question_ids).values_list('question_id', flat=True))
        notes_dict = {n.question_id: n.content for n in Note.objects.filter(user=user, question_id__in=question_ids)}
        
        # 傳遞預查詢的資料給 serializer
        context = {
            'request': request,
            'flashcard_question_ids': flashcard_question_ids,
            'bookmark_question_ids': bookmark_question_ids,
            'notes_dict': notes_dict
        }
        return Response(WrongQuestionSerializer(wrong_qs, many=True, context=context).data)

    def patch(self, request, pk):
        """標記錯題為已複習"""
        try:
            wq = WrongQuestion.objects.get(pk=pk, user=request.user)
            wq.reviewed = request.data.get('reviewed', True)
            wq.save()
            return Response(WrongQuestionSerializer(wq, context={'request': request}).data)
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
        from flashcards.models import Flashcard
        from question_bank.models import Note
        
        user = request.user
        bookmarks = Bookmark.objects.filter(user=user).select_related('question')
        
        # 取得所有收藏的 question_id
        question_ids = list(bookmarks.values_list('question_id', flat=True))
        
        # 批次查詢使用者的 flashcard 和 note，避免 N+1
        flashcard_question_ids = set(Flashcard.objects.filter(user=user, question_id__in=question_ids).values_list('question_id', flat=True))
        notes_dict = {n.question_id: n.content for n in Note.objects.filter(user=user, question_id__in=question_ids)}
        
        data = []
        for b in bookmarks:
            data.append({
                'id': b.id,
                'question': b.question.id,
                'question_content': b.question.content,
                'question_subject': b.question.subject,
                'created_at': b.created_at,
                'is_in_flashcard': b.question_id in flashcard_question_ids,
                'is_bookmarked': True,  # 在收藏列表中的題目一定是已收藏的
                'user_note': notes_dict.get(b.question_id)
            })
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

        total_bank = Question.objects.count()
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


class CustomExamView(APIView):
    """從任意題目 ID 列表生成考卷 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="從題目 ID 列表生成考卷",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['question_ids'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='考卷名稱'),
                'question_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description='題目 ID 列表'),
                'time_limit': openapi.Schema(type=openapi.TYPE_INTEGER, description='時間限制（分鐘）'),
            }
        ),
        responses={201: ExamDetailSerializer()}
    )
    def post(self, request):
        name = request.data.get('name', '自訂測驗')
        question_ids = request.data.get('question_ids', [])
        time_limit = request.data.get('time_limit')

        if not question_ids:
            return Response({"error": "請提供題目 ID 列表"}, status=status.HTTP_400_BAD_REQUEST)

        questions = list(Question.objects.filter(id__in=question_ids))
        
        if not questions:
            return Response({"error": "找不到指定的題目"}, status=status.HTTP_404_NOT_FOUND)

        # 保持原始順序
        id_to_question = {q.id: q for q in questions}
        ordered_questions = [id_to_question[qid] for qid in question_ids if qid in id_to_question]

        # 建立考卷並自動設定建立者
        exam = Exam.objects.create(
            name=name,
            description=f"包含 {len(ordered_questions)} 道題目的自訂測驗",
            time_limit=time_limit,
            created_by=request.user
        )

        with transaction.atomic():
            for index, question in enumerate(ordered_questions, start=1):
                ExamQuestion.objects.create(exam=exam, question=question, order=index)

        # 直接回傳 Exam 資料
        serializer = ExamDetailSerializer(exam, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
