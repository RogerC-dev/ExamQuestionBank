-- ============================================
-- RPC Functions Migration
-- ExamQuestionBank - Supabase
-- Created: 2026-01-16
-- ============================================

-- ============================================
-- QUESTIONS
-- ============================================

-- Get questions with filters, pagination, and related data
CREATE OR REPLACE FUNCTION get_questions(
  p_subject TEXT DEFAULT NULL,
  p_difficulty TEXT DEFAULT NULL,
  p_type TEXT DEFAULT NULL,
  p_year INTEGER DEFAULT NULL,
  p_keyword TEXT DEFAULT NULL,
  p_page INTEGER DEFAULT 1,
  p_page_size INTEGER DEFAULT 20
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  offset_val INTEGER;
  total_count INTEGER;
BEGIN
  offset_val := (p_page - 1) * p_page_size;
  
  -- Get total count
  SELECT COUNT(*) INTO total_count
  FROM question q
  WHERE (p_subject IS NULL OR q.subject = p_subject)
    AND (p_difficulty IS NULL OR q.difficulty::TEXT = p_difficulty)
    AND (p_type IS NULL OR q.type::TEXT = p_type)
    AND (p_year IS NULL OR q.year = p_year)
    AND (p_keyword IS NULL OR q.content ILIKE '%' || p_keyword || '%');

  -- Get questions with options and tags
  SELECT json_build_object(
    'results', COALESCE(json_agg(q_data), '[]'::json),
    'count', total_count,
    'page', p_page,
    'page_size', p_page_size
  ) INTO result
  FROM (
    SELECT json_build_object(
      'id', q.id,
      'content', q.content,
      'explanation', q.explanation,
      'type', q.type,
      'difficulty', q.difficulty,
      'subject', q.subject,
      'category', q.category,
      'year', q.year,
      'source', q.source,
      'created_at', q.created_at,
      'options', (
        SELECT COALESCE(json_agg(
          json_build_object(
            'id', o.id,
            'content', o.content,
            'is_correct', o.is_correct,
            'order', o."order"
          ) ORDER BY o."order"
        ), '[]'::json)
        FROM question_option o
        WHERE o.question_id = q.id
      ),
      'tags', (
        SELECT COALESCE(json_agg(
          json_build_object('id', t.id, 'name', t.name)
        ), '[]'::json)
        FROM question_tag qt
        JOIN tag t ON t.id = qt.tag_id
        WHERE qt.question_id = q.id
      )
    ) AS q_data
    FROM question q
    WHERE (p_subject IS NULL OR q.subject = p_subject)
      AND (p_difficulty IS NULL OR q.difficulty::TEXT = p_difficulty)
      AND (p_type IS NULL OR q.type::TEXT = p_type)
      AND (p_year IS NULL OR q.year = p_year)
      AND (p_keyword IS NULL OR q.content ILIKE '%' || p_keyword || '%')
    ORDER BY q.created_at DESC
    LIMIT p_page_size
    OFFSET offset_val
  ) sub;

  RETURN result;
END;
$$;

-- Get single question with full details
CREATE OR REPLACE FUNCTION get_question_detail(p_id BIGINT)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'id', q.id,
    'content', q.content,
    'explanation', q.explanation,
    'type', q.type,
    'difficulty', q.difficulty,
    'subject', q.subject,
    'category', q.category,
    'year', q.year,
    'source', q.source,
    'created_at', q.created_at,
    'options', (
      SELECT COALESCE(json_agg(
        json_build_object(
          'id', o.id,
          'content', o.content,
          'is_correct', o.is_correct,
          'order', o."order"
        ) ORDER BY o."order"
      ), '[]'::json)
      FROM question_option o
      WHERE o.question_id = q.id
    ),
    'tags', (
      SELECT COALESCE(json_agg(
        json_build_object('id', t.id, 'name', t.name)
      ), '[]'::json)
      FROM question_tag qt
      JOIN tag t ON t.id = qt.tag_id
      WHERE qt.question_id = q.id
    )
  ) INTO result
  FROM question q
  WHERE q.id = p_id;

  RETURN result;
END;
$$;

-- ============================================
-- EXAMS
-- ============================================

-- Get exam detail with all questions
CREATE OR REPLACE FUNCTION get_exam_detail(p_id BIGINT)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'id', e.id,
    'name', e.name,
    'description', e.description,
    'time_limit', e.time_limit,
    'publish', e.publish,
    'created_at', e.created_at,
    'questions', (
      SELECT COALESCE(json_agg(
        json_build_object(
          'exam_question_id', eq.id,
          'order', eq."order",
          'points', eq.points,
          'id', q.id,
          'content', q.content,
          'explanation', q.explanation,
          'type', q.type,
          'difficulty', q.difficulty,
          'options', (
            SELECT COALESCE(json_agg(
              json_build_object(
                'id', o.id,
                'content', o.content,
                'is_correct', o.is_correct,
                'order', o."order"
              ) ORDER BY o."order"
            ), '[]'::json)
            FROM question_option o
            WHERE o.question_id = q.id
          )
        ) ORDER BY eq."order"
      ), '[]'::json)
      FROM exam_question eq
      JOIN question q ON q.id = eq.question_id
      WHERE eq.exam_id = e.id
    )
  ) INTO result
  FROM exam e
  WHERE e.id = p_id;

  RETURN result;
END;
$$;

-- Get exams list with question count (for current user)
CREATE OR REPLACE FUNCTION get_user_exams()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', e.id,
      'name', e.name,
      'description', e.description,
      'time_limit', e.time_limit,
      'publish', e.publish,
      'created_at', e.created_at,
      'question_count', (
        SELECT COUNT(*) FROM exam_question eq WHERE eq.exam_id = e.id
      )
    ) ORDER BY e.created_at DESC
  ), '[]'::json) INTO result
  FROM exam e
  WHERE e.creator = current_user_id;

  RETURN result;
END;
$$;

-- Get practice exams (published + user's own)
CREATE OR REPLACE FUNCTION get_practice_exams()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', e.id,
      'name', e.name,
      'description', e.description,
      'time_limit', e.time_limit,
      'publish', e.publish,
      'created_at', e.created_at,
      'question_count', (
        SELECT COUNT(*) FROM exam_question eq WHERE eq.exam_id = e.id
      )
    ) ORDER BY e.created_at DESC
  ), '[]'::json) INTO result
  FROM exam e
  WHERE e.publish = TRUE OR e.creator = current_user_id;

  RETURN result;
END;
$$;

-- ============================================
-- EXAM RESULTS
-- ============================================

-- Save exam result and track wrong questions
CREATE OR REPLACE FUNCTION save_exam_result(
  p_exam_id BIGINT DEFAULT NULL,
  p_exam_name TEXT DEFAULT '',
  p_score DECIMAL DEFAULT 0,
  p_correct_count INTEGER DEFAULT 0,
  p_total_count INTEGER DEFAULT 0,
  p_duration_seconds INTEGER DEFAULT NULL,
  p_answers_json JSONB DEFAULT NULL,
  p_wrong_question_ids BIGINT[] DEFAULT NULL
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result_id BIGINT;
  current_user_id UUID;
  wq_id BIGINT;
  result JSON;
BEGIN
  current_user_id := auth.uid();
  
  IF current_user_id IS NULL THEN
    RAISE EXCEPTION 'Authentication required';
  END IF;

  -- Insert exam result
  INSERT INTO exam_result (
    user_id, exam_id, exam_name, score, correct_count, 
    total_count, duration_seconds, answers_json
  )
  VALUES (
    current_user_id, p_exam_id, p_exam_name, p_score, p_correct_count,
    p_total_count, p_duration_seconds, p_answers_json
  )
  RETURNING id INTO result_id;

  -- Track wrong questions
  IF p_wrong_question_ids IS NOT NULL THEN
    FOREACH wq_id IN ARRAY p_wrong_question_ids
    LOOP
      INSERT INTO wrong_question (user_id, question_id, wrong_count, last_wrong_at)
      VALUES (current_user_id, wq_id, 1, NOW())
      ON CONFLICT (user_id, question_id)
      DO UPDATE SET 
        wrong_count = wrong_question.wrong_count + 1,
        last_wrong_at = NOW(),
        reviewed = FALSE;
    END LOOP;
  END IF;

  SELECT json_build_object(
    'id', result_id,
    'success', TRUE
  ) INTO result;

  RETURN result;
END;
$$;

-- Get exam results for current user
CREATE OR REPLACE FUNCTION get_exam_results()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', er.id,
      'exam_id', er.exam_id,
      'exam_name', er.exam_name,
      'score', er.score,
      'correct_count', er.correct_count,
      'total_count', er.total_count,
      'duration_seconds', er.duration_seconds,
      'completed_at', er.completed_at
    ) ORDER BY er.completed_at DESC
  ), '[]'::json) INTO result
  FROM exam_result er
  WHERE er.user_id = current_user_id;

  RETURN result;
END;
$$;

-- ============================================
-- WRONG QUESTIONS
-- ============================================

-- Get wrong questions with question details
CREATE OR REPLACE FUNCTION get_wrong_questions()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', wq.id,
      'wrong_count', wq.wrong_count,
      'last_wrong_at', wq.last_wrong_at,
      'reviewed', wq.reviewed,
      'question_id', q.id,
      'content', q.content,
      'type', q.type,
      'difficulty', q.difficulty,
      'subject', q.subject,
      'category', q.category,
      'options', (
        SELECT COALESCE(json_agg(
          json_build_object(
            'id', o.id,
            'content', o.content,
            'is_correct', o.is_correct,
            'order', o."order"
          ) ORDER BY o."order"
        ), '[]'::json)
        FROM question_option o
        WHERE o.question_id = q.id
      )
    ) ORDER BY wq.wrong_count DESC
  ), '[]'::json) INTO result
  FROM wrong_question wq
  JOIN question q ON q.id = wq.question_id
  WHERE wq.user_id = current_user_id;

  RETURN result;
END;
$$;

-- ============================================
-- FLASHCARDS
-- ============================================

-- Get all flashcards for current user
CREATE OR REPLACE FUNCTION get_flashcards()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', f.id,
      'status', f.status,
      'ease_factor', f.ease_factor,
      'interval_days', f.interval_days,
      'repetition', f.repetition,
      'next_review_date', f.next_review_date,
      'last_reviewed_at', f.last_reviewed_at,
      'review_count', f.review_count,
      'created_at', f.created_at,
      'question', json_build_object(
        'id', q.id,
        'content', q.content,
        'explanation', q.explanation,
        'options', (
          SELECT COALESCE(json_agg(
            json_build_object(
              'id', o.id,
              'content', o.content,
              'is_correct', o.is_correct,
              'order', o."order"
            ) ORDER BY o."order"
          ), '[]'::json)
          FROM question_option o
          WHERE o.question_id = q.id
        )
      )
    ) ORDER BY f.created_at DESC
  ), '[]'::json) INTO result
  FROM flashcard f
  JOIN question q ON q.id = f.question_id
  WHERE f.user_id = current_user_id;

  RETURN result;
END;
$$;

-- Get due flashcards
CREATE OR REPLACE FUNCTION get_due_flashcards(p_limit INTEGER DEFAULT 20)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', f.id,
      'status', f.status,
      'ease_factor', f.ease_factor,
      'interval_days', f.interval_days,
      'repetition', f.repetition,
      'next_review_date', f.next_review_date,
      'question', json_build_object(
        'id', q.id,
        'content', q.content,
        'explanation', q.explanation,
        'options', (
          SELECT COALESCE(json_agg(
            json_build_object(
              'id', o.id,
              'content', o.content,
              'is_correct', o.is_correct,
              'order', o."order"
            ) ORDER BY o."order"
          ), '[]'::json)
          FROM question_option o
          WHERE o.question_id = q.id
        )
      )
    ) ORDER BY f.next_review_date
  ), '[]'::json) INTO result
  FROM flashcard f
  JOIN question q ON q.id = f.question_id
  WHERE f.user_id = current_user_id
    AND f.next_review_date <= CURRENT_DATE
  LIMIT p_limit;

  RETURN result;
END;
$$;

-- Review flashcard with SM2 algorithm
CREATE OR REPLACE FUNCTION review_flashcard(
  p_flashcard_id BIGINT,
  p_rating INTEGER  -- 0=Again, 1=Hard, 2=Good, 3=Easy
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_user_id UUID;
  fc RECORD;
  new_ease DECIMAL;
  new_interval INTEGER;
  new_rep INTEGER;
  new_status TEXT;
  result JSON;
BEGIN
  current_user_id := auth.uid();
  
  -- Get current flashcard
  SELECT * INTO fc
  FROM flashcard
  WHERE id = p_flashcard_id AND user_id = current_user_id;
  
  IF fc IS NULL THEN
    RAISE EXCEPTION 'Flashcard not found';
  END IF;

  -- SM2 Algorithm
  IF p_rating < 2 THEN
    -- Failed
    new_rep := 0;
    new_interval := 1;
    new_ease := fc.ease_factor;
  ELSE
    -- Success
    new_rep := fc.repetition + 1;
    
    IF new_rep = 1 THEN
      new_interval := 1;
    ELSIF new_rep = 2 THEN
      new_interval := 6;
    ELSE
      new_interval := ROUND(fc.interval_days * fc.ease_factor);
    END IF;
    
    -- Adjust ease factor
    new_ease := GREATEST(1.3, fc.ease_factor + (0.1 - (3 - p_rating) * (0.08 + (3 - p_rating) * 0.02)));
  END IF;

  -- Determine status
  IF new_rep >= 3 AND new_interval >= 21 THEN
    new_status := 'mastered';
  ELSIF new_rep >= 1 THEN
    new_status := 'review';
  ELSE
    new_status := 'learning';
  END IF;

  -- Update flashcard
  UPDATE flashcard
  SET 
    ease_factor = new_ease,
    interval_days = new_interval,
    repetition = new_rep,
    status = new_status,
    next_review_date = CURRENT_DATE + new_interval,
    last_reviewed_at = NOW(),
    review_count = review_count + 1
  WHERE id = p_flashcard_id;

  SELECT json_build_object(
    'id', p_flashcard_id,
    'ease_factor', new_ease,
    'interval_days', new_interval,
    'repetition', new_rep,
    'status', new_status,
    'next_review_date', CURRENT_DATE + new_interval
  ) INTO result;

  RETURN result;
END;
$$;

-- Get flashcard statistics
CREATE OR REPLACE FUNCTION get_flashcard_stats()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT json_build_object(
    'total', (SELECT COUNT(*) FROM flashcard WHERE user_id = current_user_id),
    'due', (SELECT COUNT(*) FROM flashcard WHERE user_id = current_user_id AND next_review_date <= CURRENT_DATE),
    'mastered', (SELECT COUNT(*) FROM flashcard WHERE user_id = current_user_id AND status = 'mastered'),
    'learning', (SELECT COUNT(*) FROM flashcard WHERE user_id = current_user_id AND status != 'mastered')
  ) INTO result;

  RETURN result;
END;
$$;

-- ============================================
-- BOOKMARKS
-- ============================================

-- Get bookmarks with question details
CREATE OR REPLACE FUNCTION get_bookmarks()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT COALESCE(json_agg(
    json_build_object(
      'id', b.question_id,
      'bookmarked_at', b.created_at,
      'content', q.content,
      'type', q.type,
      'difficulty', q.difficulty,
      'subject', q.subject,
      'category', q.category,
      'options', (
        SELECT COALESCE(json_agg(
          json_build_object(
            'id', o.id,
            'content', o.content,
            'is_correct', o.is_correct,
            'order', o."order"
          ) ORDER BY o."order"
        ), '[]'::json)
        FROM question_option o
        WHERE o.question_id = q.id
      )
    ) ORDER BY b.created_at DESC
  ), '[]'::json) INTO result
  FROM bookmark b
  JOIN question q ON q.id = b.question_id
  WHERE b.user_id = current_user_id;

  RETURN result;
END;
$$;

-- ============================================
-- ANALYTICS
-- ============================================

-- Get user analytics/stats
CREATE OR REPLACE FUNCTION get_user_analytics()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  current_user_id UUID;
BEGIN
  current_user_id := auth.uid();
  
  SELECT json_build_object(
    'total_exams', (
      SELECT COUNT(*) FROM exam_result WHERE user_id = current_user_id
    ),
    'total_questions_answered', (
      SELECT COALESCE(SUM(total_count), 0) FROM exam_result WHERE user_id = current_user_id
    ),
    'total_correct', (
      SELECT COALESCE(SUM(correct_count), 0) FROM exam_result WHERE user_id = current_user_id
    ),
    'average_score', (
      SELECT COALESCE(ROUND(AVG(score)::numeric, 1), 0) FROM exam_result WHERE user_id = current_user_id
    ),
    'wrong_questions_count', (
      SELECT COUNT(*) FROM wrong_question WHERE user_id = current_user_id
    ),
    'flashcard_count', (
      SELECT COUNT(*) FROM flashcard WHERE user_id = current_user_id
    ),
    'bookmark_count', (
      SELECT COUNT(*) FROM bookmark WHERE user_id = current_user_id
    ),
    'recent_results', (
      SELECT COALESCE(json_agg(
        json_build_object(
          'id', er.id,
          'exam_name', er.exam_name,
          'score', er.score,
          'completed_at', er.completed_at
        ) ORDER BY er.completed_at DESC
      ), '[]'::json)
      FROM (
        SELECT * FROM exam_result WHERE user_id = current_user_id ORDER BY completed_at DESC LIMIT 5
      ) er
    )
  ) INTO result;

  RETURN result;
END;
$$;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION get_questions TO authenticated;
GRANT EXECUTE ON FUNCTION get_question_detail TO authenticated;
GRANT EXECUTE ON FUNCTION get_exam_detail TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_exams TO authenticated;
GRANT EXECUTE ON FUNCTION get_practice_exams TO authenticated;
GRANT EXECUTE ON FUNCTION save_exam_result TO authenticated;
GRANT EXECUTE ON FUNCTION get_exam_results TO authenticated;
GRANT EXECUTE ON FUNCTION get_wrong_questions TO authenticated;
GRANT EXECUTE ON FUNCTION get_flashcards TO authenticated;
GRANT EXECUTE ON FUNCTION get_due_flashcards TO authenticated;
GRANT EXECUTE ON FUNCTION review_flashcard TO authenticated;
GRANT EXECUTE ON FUNCTION get_flashcard_stats TO authenticated;
GRANT EXECUTE ON FUNCTION get_bookmarks TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_analytics TO authenticated;

-- Grant to anon for public functions
GRANT EXECUTE ON FUNCTION get_questions TO anon;
GRANT EXECUTE ON FUNCTION get_question_detail TO anon;
GRANT EXECUTE ON FUNCTION get_practice_exams TO anon;
