-- =============================================================================
-- ExamQuestionBank: Redesigned Supabase Schema
-- Created: 2026-01-15
-- Description: Clean, efficient schema based on actual frontend usage
-- =============================================================================

-- ============================================
-- ENUM TYPES
-- ============================================

CREATE TYPE public.question_type AS ENUM (
    'essay',
    'multipleChoice'
);

CREATE TYPE public.question_difficulty AS ENUM (
    'easy',
    'normal',
    'hard',
    'insane'
);

CREATE TYPE public.conversation_role AS ENUM (
    'user',
    'assistant'
);

-- ============================================
-- TABLE 1: tag (Subject/Topic Tags)
-- ============================================

CREATE TABLE IF NOT EXISTS public.tag (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    
    CONSTRAINT tag_name_unique UNIQUE (name)
);

CREATE INDEX idx_tag_name ON public.tag(name);
CREATE INDEX idx_tag_category ON public.tag(category);

ALTER TABLE public.tag ENABLE ROW LEVEL SECURITY;

-- Tags are readable by all authenticated users, writable by admins only
CREATE POLICY "Authenticated users can read tags" ON public.tag
    FOR SELECT TO authenticated USING (true);

-- ============================================
-- TABLE 2: question (Core Question Content)
-- ============================================

CREATE TABLE IF NOT EXISTS public.question (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    explanation TEXT,
    type public.question_type DEFAULT 'multipleChoice' NOT NULL,
    difficulty public.question_difficulty DEFAULT 'normal' NOT NULL,
    -- Denormalized fields for query efficiency
    subject VARCHAR(100),
    category VARCHAR(50),
    year SMALLINT,
    source VARCHAR(200),
    creator UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for common query patterns
CREATE INDEX idx_question_subject ON public.question(subject);
CREATE INDEX idx_question_type ON public.question(type);
CREATE INDEX idx_question_difficulty ON public.question(difficulty);
CREATE INDEX idx_question_year ON public.question(year);
CREATE INDEX idx_question_creator ON public.question(creator);
CREATE INDEX idx_question_created_at ON public.question(created_at DESC);

ALTER TABLE public.question ENABLE ROW LEVEL SECURITY;

-- Questions are readable by all authenticated users
CREATE POLICY "Authenticated users can read questions" ON public.question
    FOR SELECT TO authenticated USING (true);

-- ============================================
-- TABLE 3: question_option (Answer Choices)
-- ============================================

CREATE TABLE IF NOT EXISTS public.question_option (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT false,
    "order" SMALLINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    
    CONSTRAINT question_option_order_unique UNIQUE (question_id, "order")
);

CREATE INDEX idx_option_question ON public.question_option(question_id);

ALTER TABLE public.question_option ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read question options" ON public.question_option
    FOR SELECT TO authenticated USING (true);

-- ============================================
-- TABLE 4: question_tag (Many-to-Many)
-- ============================================

CREATE TABLE IF NOT EXISTS public.question_tag (
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES public.tag(id) ON DELETE CASCADE,
    PRIMARY KEY (question_id, tag_id)
);

CREATE INDEX idx_qtag_tag ON public.question_tag(tag_id);

ALTER TABLE public.question_tag ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read question tags" ON public.question_tag
    FOR SELECT TO authenticated USING (true);

-- ============================================
-- TABLE 5: exam (User-Created Exams)
-- ============================================

CREATE TABLE IF NOT EXISTS public.exam (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    time_limit SMALLINT DEFAULT 60 NOT NULL,
    publish BOOLEAN DEFAULT false NOT NULL,
    creator UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_exam_creator ON public.exam(creator);
CREATE INDEX idx_exam_publish ON public.exam(publish) WHERE publish = true;
CREATE INDEX idx_exam_created_at ON public.exam(created_at DESC);

ALTER TABLE public.exam ENABLE ROW LEVEL SECURITY;

-- Users can manage their own exams
CREATE POLICY "Users can manage own exams" ON public.exam
    FOR ALL TO authenticated
    USING (auth.uid() = creator)
    WITH CHECK (auth.uid() = creator);

-- Anyone can view published exams
CREATE POLICY "Anyone can view published exams" ON public.exam
    FOR SELECT TO authenticated
    USING (publish = true);

-- ============================================
-- TABLE 6: exam_tag (Exam-Tag Junction)
-- ============================================

CREATE TABLE IF NOT EXISTS public.exam_tag (
    exam_id BIGINT NOT NULL REFERENCES public.exam(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES public.tag(id) ON DELETE CASCADE,
    PRIMARY KEY (exam_id, tag_id)
);

CREATE INDEX idx_etag_tag ON public.exam_tag(tag_id);

ALTER TABLE public.exam_tag ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own exam tags" ON public.exam_tag
    FOR ALL TO authenticated
    USING (
        EXISTS (SELECT 1 FROM public.exam WHERE id = exam_id AND creator = auth.uid())
    );

CREATE POLICY "Anyone can view published exam tags" ON public.exam_tag
    FOR SELECT TO authenticated
    USING (
        EXISTS (SELECT 1 FROM public.exam WHERE id = exam_id AND publish = true)
    );

-- ============================================
-- TABLE 7: exam_question (Exam-Question Junction)
-- ============================================

CREATE TABLE IF NOT EXISTS public.exam_question (
    id BIGSERIAL PRIMARY KEY,
    exam_id BIGINT NOT NULL REFERENCES public.exam(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    "order" SMALLINT NOT NULL,
    points DECIMAL(5,2) DEFAULT 1.0,
    
    CONSTRAINT exam_question_unique UNIQUE (exam_id, question_id),
    CONSTRAINT exam_question_order_unique UNIQUE (exam_id, "order")
);

CREATE INDEX idx_eq_exam ON public.exam_question(exam_id);
CREATE INDEX idx_eq_question ON public.exam_question(question_id);

ALTER TABLE public.exam_question ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own exam questions" ON public.exam_question
    FOR ALL TO authenticated
    USING (
        EXISTS (SELECT 1 FROM public.exam WHERE id = exam_id AND creator = auth.uid())
    );

CREATE POLICY "Anyone can view published exam questions" ON public.exam_question
    FOR SELECT TO authenticated
    USING (
        EXISTS (SELECT 1 FROM public.exam WHERE id = exam_id AND publish = true)
    );

-- ============================================
-- TABLE 8: exam_result (Completed Tests)
-- ============================================

CREATE TABLE IF NOT EXISTS public.exam_result (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    exam_id BIGINT REFERENCES public.exam(id) ON DELETE SET NULL,
    exam_name VARCHAR(200),
    score DECIMAL(5,2) NOT NULL,
    correct_count SMALLINT NOT NULL,
    total_count SMALLINT NOT NULL,
    duration_seconds INTEGER,
    answers_json JSONB,
    completed_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_result_user ON public.exam_result(user_id);
CREATE INDEX idx_result_exam ON public.exam_result(exam_id);
CREATE INDEX idx_result_date ON public.exam_result(completed_at DESC);
CREATE INDEX idx_result_user_date ON public.exam_result(user_id, completed_at DESC);

ALTER TABLE public.exam_result ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own exam results" ON public.exam_result
    FOR ALL TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- TABLE 9: bookmark (Saved Questions)
-- ============================================

CREATE TABLE IF NOT EXISTS public.bookmark (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    PRIMARY KEY (user_id, question_id)
);

CREATE INDEX idx_bookmark_user ON public.bookmark(user_id);
CREATE INDEX idx_bookmark_question ON public.bookmark(question_id);

ALTER TABLE public.bookmark ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own bookmarks" ON public.bookmark
    FOR ALL TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- TABLE 10: wrong_question (Error Tracking)
-- ============================================

CREATE TABLE IF NOT EXISTS public.wrong_question (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    wrong_count SMALLINT DEFAULT 1 NOT NULL,
    last_wrong_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    reviewed BOOLEAN DEFAULT false NOT NULL,
    
    CONSTRAINT wrong_question_unique UNIQUE (user_id, question_id)
);

CREATE INDEX idx_wrong_user ON public.wrong_question(user_id);
CREATE INDEX idx_wrong_question ON public.wrong_question(question_id);
CREATE INDEX idx_wrong_reviewed ON public.wrong_question(user_id, reviewed);
CREATE INDEX idx_wrong_count ON public.wrong_question(user_id, wrong_count DESC);

ALTER TABLE public.wrong_question ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own wrong questions" ON public.wrong_question
    FOR ALL TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- TABLE 11: flashcard (Spaced Repetition)
-- ============================================

CREATE TABLE IF NOT EXISTS public.flashcard (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    -- SM2 Algorithm fields
    ease_factor REAL DEFAULT 2.5 NOT NULL,
    interval_days SMALLINT DEFAULT 1 NOT NULL,
    repetition SMALLINT DEFAULT 0 NOT NULL,
    status VARCHAR(20) DEFAULT 'new' NOT NULL,
    next_review_date DATE DEFAULT CURRENT_DATE NOT NULL,
    last_reviewed_at TIMESTAMPTZ,
    review_count SMALLINT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    
    CONSTRAINT flashcard_unique UNIQUE (user_id, question_id),
    CONSTRAINT flashcard_status_check CHECK (status IN ('new', 'learning', 'review', 'mastered'))
);

CREATE INDEX idx_flashcard_user ON public.flashcard(user_id);
CREATE INDEX idx_flashcard_question ON public.flashcard(question_id);
CREATE INDEX idx_flashcard_due ON public.flashcard(user_id, next_review_date);
CREATE INDEX idx_flashcard_status ON public.flashcard(user_id, status);

ALTER TABLE public.flashcard ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own flashcards" ON public.flashcard
    FOR ALL TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- TABLE 12: question_note (User Notes)
-- ============================================

CREATE TABLE IF NOT EXISTS public.question_note (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES public.question(id) ON DELETE CASCADE,
    content TEXT DEFAULT '' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, question_id)
);

CREATE INDEX idx_note_user ON public.question_note(user_id);
CREATE INDEX idx_note_question ON public.question_note(question_id);

ALTER TABLE public.question_note ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own notes" ON public.question_note
    FOR ALL TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- TABLE 13: conversation (AI Chat Sessions)
-- ============================================

CREATE TABLE IF NOT EXISTS public.conversation (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_conv_user ON public.conversation(user_id);
CREATE INDEX idx_conv_updated ON public.conversation(user_id, updated_at DESC);

ALTER TABLE public.conversation ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own conversations" ON public.conversation
    FOR ALL TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- TABLE 14: conversation_message (AI Chat Messages)
-- ============================================

CREATE TABLE IF NOT EXISTS public.conversation_message (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES public.conversation(id) ON DELETE CASCADE,
    role public.conversation_role NOT NULL,
    content TEXT NOT NULL,
    reply_to_message_id BIGINT REFERENCES public.conversation_message(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_msg_conv ON public.conversation_message(conversation_id);
CREATE INDEX idx_msg_created ON public.conversation_message(conversation_id, created_at);

ALTER TABLE public.conversation_message ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own conversation messages" ON public.conversation_message
    FOR ALL TO authenticated
    USING (
        EXISTS (SELECT 1 FROM public.conversation WHERE id = conversation_id AND user_id = auth.uid())
    )
    WITH CHECK (
        EXISTS (SELECT 1 FROM public.conversation WHERE id = conversation_id AND user_id = auth.uid())
    );

-- ============================================
-- GRANTS (Supabase Standard)
-- ============================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;

-- Grant access to sequences
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;

-- Grant access to tables
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO postgres, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres, anon, authenticated, service_role;

-- ============================================
-- HELPER FUNCTIONS (Optional)
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER set_question_updated_at
    BEFORE UPDATE ON public.question
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_exam_updated_at
    BEFORE UPDATE ON public.exam
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_note_updated_at
    BEFORE UPDATE ON public.question_note
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_conversation_updated_at
    BEFORE UPDATE ON public.conversation
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- ============================================
-- RPC FUNCTIONS
-- ============================================

CREATE OR REPLACE FUNCTION public.add_question(
    content TEXT,
    explanation TEXT DEFAULT NULL,
    question_type TEXT DEFAULT NULL,
    difficulty TEXT DEFAULT NULL,
    subject TEXT DEFAULT NULL,
    category TEXT DEFAULT NULL,
    year SMALLINT DEFAULT NULL,
    source TEXT DEFAULT NULL,
    options JSONB DEFAULT '[]'::jsonb,
    tag_ids BIGINT[] DEFAULT NULL,
    creator UUID DEFAULT NULL,
    status TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_question_id BIGINT;
    v_type public.question_type;
    v_difficulty public.question_difficulty;
    v_creator UUID;
    v_options JSONB;
    v_has_options BOOLEAN;
BEGIN
    IF content IS NULL OR btrim(content) = '' THEN
        RAISE EXCEPTION 'content is required';
    END IF;

    v_options := COALESCE(options, '[]'::jsonb);
    v_has_options := CASE
        WHEN jsonb_typeof(v_options) = 'array' THEN jsonb_array_length(v_options) > 0
        ELSE false
    END;

    IF question_type IN ('essay', 'multipleChoice') THEN
        v_type := question_type::public.question_type;
    ELSE
        v_type := CASE WHEN v_has_options THEN 'multipleChoice' ELSE 'essay' END;
    END IF;

    IF difficulty = 'medium' THEN
        v_difficulty := 'normal';
    ELSIF difficulty IN ('easy', 'normal', 'hard', 'insane') THEN
        v_difficulty := difficulty::public.question_difficulty;
    ELSE
        v_difficulty := 'normal';
    END IF;

    v_creator := auth.uid();
    IF v_creator IS NULL THEN
        v_creator := creator;
    END IF;

    INSERT INTO public.question (
        content,
        explanation,
        type,
        difficulty,
        subject,
        category,
        year,
        source,
        creator
    )
    VALUES (
        btrim(content),
        NULLIF(btrim(explanation), ''),
        v_type,
        v_difficulty,
        NULLIF(btrim(subject), ''),
        NULLIF(btrim(category), ''),
        year,
        NULLIF(btrim(source), ''),
        v_creator
    )
    RETURNING id INTO v_question_id;

    IF v_has_options THEN
        INSERT INTO public.question_option (question_id, content, is_correct, "order")
        SELECT
            v_question_id,
            btrim(COALESCE(opt->>'content', '')),
            COALESCE((opt->>'is_correct')::boolean, false),
            COALESCE((opt->>'order')::smallint, ord::smallint)
        FROM jsonb_array_elements(v_options) WITH ORDINALITY AS t(opt, ord)
        WHERE btrim(COALESCE(opt->>'content', '')) <> '';
    END IF;

    IF tag_ids IS NOT NULL AND array_length(tag_ids, 1) > 0 THEN
        INSERT INTO public.question_tag (question_id, tag_id)
        SELECT v_question_id, unnest(tag_ids)
        ON CONFLICT DO NOTHING;
    END IF;

    RETURN v_question_id;
END;
$$;

GRANT EXECUTE ON FUNCTION public.add_question(
    TEXT,
    TEXT,
    TEXT,
    TEXT,
    TEXT,
    TEXT,
    SMALLINT,
    TEXT,
    JSONB,
    BIGINT[],
    UUID,
    TEXT
) TO authenticated;

-- ============================================
-- COMMENTS (Documentation)
-- ============================================

COMMENT ON TABLE public.question IS 'Core question content for the exam question bank';
COMMENT ON TABLE public.question_option IS 'Answer choices for multiple choice questions';
COMMENT ON TABLE public.tag IS 'Tags for categorizing questions and exams';
COMMENT ON TABLE public.exam IS 'User-created practice exams';
COMMENT ON TABLE public.exam_result IS 'Records of completed exam attempts';
COMMENT ON TABLE public.bookmark IS 'User bookmarked questions';
COMMENT ON TABLE public.wrong_question IS 'Tracks questions user answered incorrectly';
COMMENT ON TABLE public.flashcard IS 'Spaced repetition flashcards using SM2 algorithm';
COMMENT ON TABLE public.question_note IS 'User notes on specific questions';
COMMENT ON TABLE public.conversation IS 'AI chat conversation sessions';
COMMENT ON TABLE public.conversation_message IS 'Individual messages in AI conversations';

COMMENT ON COLUMN public.flashcard.ease_factor IS 'SM2 ease factor, starts at 2.5';
COMMENT ON COLUMN public.flashcard.interval_days IS 'Days until next review';
COMMENT ON COLUMN public.flashcard.repetition IS 'Number of successful repetitions';
COMMENT ON COLUMN public.exam_result.answers_json IS 'JSONB storing per-question answers and correctness';
