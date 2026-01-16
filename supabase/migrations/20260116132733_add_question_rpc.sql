-- =============================================================================
-- Supabase RPC: add_question
-- =============================================================================

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
