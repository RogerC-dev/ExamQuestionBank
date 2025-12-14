from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services.pdf_parser import PDFParser
from .models import Question, Subject, Tag
from .serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateUpdateSerializer,
    SubjectSerializer,
    TagSerializer,
)


class SubjectListView(APIView):
    """取得科目列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all().order_by('name')
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)


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


class QuestionPagination(PageNumberPagination):
    """自訂分頁類別，支援前端動態設定 page_size"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 500


class QuestionViewSet(viewsets.ModelViewSet):
    """
    題目的 CRUD API

    list: 取得題目列表（簡化版）
    retrieve: 取得單一題目詳細資訊（包含選項、標籤）
    create: 建立新題目
    update: 更新題目
    partial_update: 部分更新題目
    destroy: 刪除題目
    
    支援的查詢參數：
    - keyword: 搜尋題目內容
    - tags: 依標籤 ID 篩選（逗號分隔，如 tags=1,2,3）
    - page_size: 每頁數量（預設 20，最大 500）
    """
    queryset = (
        Question.objects.all()
        .prefetch_related('options', 'tags')
        .select_related('created_by')
        .order_by('id')  # 明確排序以避免分頁警告
    )
    permission_classes = [IsAuthenticated]
    pagination_class = QuestionPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'subject', 'category']

    def get_queryset(self):
        """支援 keyword 和 tags 篩選"""
        queryset = super().get_queryset()
        
        # keyword 篩選（搜尋題目內容、科目、分類，以及選項內容）
        keyword = self.request.query_params.get('keyword', '').strip()
        if keyword:
            # Include search across content, subject, category and option content
            q_filter = (
                Q(content__icontains=keyword) |
                Q(subject__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(options__content__icontains=keyword)
            )
            queryset = queryset.filter(q_filter).distinct()
        
        # tags 篩選（依標籤 ID，逗號分隔）
        # tag_mode: 'or' (預設) = 符合任一標籤, 'and' = 必須符合所有標籤
        tags_param = self.request.query_params.get('tags', '').strip()
        tag_mode = self.request.query_params.get('tag_mode', 'or').strip().lower()
        if tags_param:
            tag_ids = [int(tid) for tid in tags_param.split(',') if tid.isdigit()]
            if tag_ids:
                if tag_mode == 'and':
                    # AND 模式：題目必須包含所有指定的標籤
                    for tag_id in tag_ids:
                        queryset = queryset.filter(tags__id=tag_id)
                    queryset = queryset.distinct()
                else:
                    # OR 模式（預設）：題目包含任一指定的標籤
                    queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        
        return queryset

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
        operation_summary="批量建立題目",
        operation_description="一次建立多題；接收一個題目物件的陣列，每個題目同 create API 欄位相同",
        request_body=QuestionCreateUpdateSerializer(many=True),
        responses={200: QuestionDetailSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({'detail': 'A list of question objects is required.'}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        for idx, item in enumerate(request.data):
            serializer = QuestionCreateUpdateSerializer(data=item, context={'request': request})
            try:
                with transaction.atomic():
                    serializer.is_valid(raise_exception=True)
                    q = serializer.save()
                    results.append({'success': True, 'id': q.id, 'data': QuestionDetailSerializer(q).data})
            except Exception as exc:
                # Collect validation errors or other exceptions per item
                err = exc
                # If it's a serializer error, get its detail
                try:
                    msg = exc.detail
                except Exception:
                    msg = str(exc)
                results.append({'success': False, 'index': idx, 'errors': msg})

        return Response({'results': results}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="批量更新題目",
        operation_description="一次更新多題；接收一個題目物件的陣列，每個物件需包含 id，並可為 partial 更新",
        request_body=QuestionCreateUpdateSerializer(many=True),
        responses={200: QuestionDetailSerializer(many=True)}
    )
    @action(detail=False, methods=['patch'], url_path='bulk-update')
    def bulk_update(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({'detail': 'A list of question objects is required.'}, status=status.HTTP_400_BAD_REQUEST)

        partial_flag = request.query_params.get('partial', 'true').lower() == 'true'
        results = []
        for idx, item in enumerate(request.data):
            qid = item.get('id')
            if not qid:
                results.append({'success': False, 'index': idx, 'errors': 'id is required for update'})
                continue

            try:
                instance = Question.objects.get(id=qid)
            except Question.DoesNotExist:
                results.append({'success': False, 'index': idx, 'errors': f'Question with id {qid} not found'})
                continue

            serializer = QuestionCreateUpdateSerializer(instance, data=item, partial=partial_flag, context={'request': request})
            try:
                with transaction.atomic():
                    serializer.is_valid(raise_exception=True)
                    q = serializer.save()
                    results.append({'success': True, 'id': q.id, 'data': QuestionDetailSerializer(q).data})
            except Exception as exc:
                try:
                    msg = exc.detail
                except Exception:
                    msg = str(exc)
                results.append({'success': False, 'index': idx, 'errors': msg})

        return Response({'results': results}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="刪除題目",
        operation_description="刪除指定的題目",
        responses={204: "刪除成功"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    """Tag CRUD API (mostly read + create for admin/editor)"""
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def create(self, request, *args, **kwargs):
        # Prevent duplicate names and return existing tag when name exists
        name = request.data.get('name')
        if not name:
            return Response({'detail': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        tag, created = Tag.objects.get_or_create(name=name)
        serializer = self.get_serializer(tag)
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_200_OK)