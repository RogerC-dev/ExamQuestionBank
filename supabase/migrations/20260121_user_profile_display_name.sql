-- =============================================================================
-- User Profile Feature Migration
-- Created: 2026-01-21
-- Description: Add display_name column and update discussion RPC functions
-- =============================================================================

-- ============================================
-- SCHEMA UPDATE: Add display_name to user_credits_mvp
-- ============================================

-- Add display_name column for user-customizable display names
ALTER TABLE user_credits_mvp 
ADD COLUMN IF NOT EXISTS display_name VARCHAR(50) DEFAULT NULL;

-- Create index for display_name lookups (useful for future features)
CREATE INDEX IF NOT EXISTS idx_user_credits_display_name 
ON user_credits_mvp(display_name) WHERE display_name IS NOT NULL;

-- Add constraint for display_name length (only if not exists)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'check_display_name_length'
  ) THEN
    ALTER TABLE user_credits_mvp
    ADD CONSTRAINT check_display_name_length 
    CHECK (display_name IS NULL OR (char_length(display_name) >= 2 AND char_length(display_name) <= 50));
  END IF;
END $$;

-- ============================================
-- UPDATE RPC FUNCTION: get_discussions_mvp
-- Now returns display_name with fallback chain
-- ============================================

-- Must drop first because we're adding a new column to the return type
DROP FUNCTION IF EXISTS get_discussions_mvp(INTEGER, INTEGER);

CREATE OR REPLACE FUNCTION get_discussions_mvp(
  p_limit INTEGER DEFAULT 20,
  p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  body TEXT,
  user_id UUID,
  user_email TEXT,
  display_name TEXT,
  view_count INTEGER,
  answer_count INTEGER,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.id,
    d.title::TEXT,
    d.body::TEXT,
    d.user_id,
    u.email::TEXT as user_email,
    COALESCE(
      uc.display_name,
      u.raw_user_meta_data->>'full_name',
      SPLIT_PART(u.email, '@', 1)
    )::TEXT as display_name,
    d.view_count::INTEGER,
    d.answer_count::INTEGER,
    d.created_at
  FROM discussions_mvp d
  LEFT JOIN auth.users u ON d.user_id = u.id
  LEFT JOIN user_credits_mvp uc ON d.user_id = uc.user_id
  ORDER BY d.created_at DESC
  LIMIT p_limit
  OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- UPDATE RPC FUNCTION: get_discussion_detail_mvp
-- Now returns display_name for discussion author and answer authors
-- ============================================

CREATE OR REPLACE FUNCTION get_discussion_detail_mvp(
  p_discussion_id UUID,
  p_user_id UUID DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
  v_discussion_user_id UUID;
BEGIN
  -- Get discussion owner
  SELECT user_id INTO v_discussion_user_id
  FROM discussions_mvp WHERE id = p_discussion_id;

  -- Increment view count
  UPDATE discussions_mvp SET view_count = view_count + 1 
  WHERE id = p_discussion_id;
  
  -- Build result with discussion and answers
  SELECT json_build_object(
    'discussion', (
      SELECT json_build_object(
        'id', d.id,
        'title', d.title,
        'body', d.body,
        'user_id', d.user_id,
        'user_email', u.email,
        'display_name', COALESCE(
          uc.display_name,
          u.raw_user_meta_data->>'full_name',
          SPLIT_PART(u.email, '@', 1)
        ),
        'view_count', d.view_count,
        'answer_count', d.answer_count,
        'created_at', d.created_at
      )
      FROM discussions_mvp d
      LEFT JOIN auth.users u ON d.user_id = u.id
      LEFT JOIN user_credits_mvp uc ON d.user_id = uc.user_id
      WHERE d.id = p_discussion_id
    ),
    'answers', (
      SELECT COALESCE(json_agg(
        json_build_object(
          'id', a.id,
          'body', CASE 
            WHEN p_user_id IS NULL THEN NULL
            WHEN EXISTS (
              SELECT 1 FROM unlocks_mvp 
              WHERE user_id = p_user_id AND answer_id = a.id
            ) THEN a.body
            WHEN a.user_id = p_user_id THEN a.body
            WHEN v_discussion_user_id = p_user_id THEN a.body
            ELSE NULL
          END,
          'is_locked', CASE
            WHEN p_user_id IS NULL THEN TRUE
            WHEN EXISTS (
              SELECT 1 FROM unlocks_mvp 
              WHERE user_id = p_user_id AND answer_id = a.id
            ) THEN FALSE
            WHEN a.user_id = p_user_id THEN FALSE
            WHEN v_discussion_user_id = p_user_id THEN FALSE
            ELSE TRUE
          END,
          'user_id', a.user_id,
          'user_email', au.email,
          'display_name', COALESCE(
            auc.display_name,
            au.raw_user_meta_data->>'full_name',
            SPLIT_PART(au.email, '@', 1)
          ),
          'vote_count', a.vote_count,
          'unlock_count', a.unlock_count,
          'created_at', a.created_at,
          'user_vote', (
            SELECT vote_value FROM votes_mvp 
            WHERE user_id = p_user_id AND answer_id = a.id
          )
        )
        ORDER BY a.vote_count DESC, a.created_at ASC
      ), '[]'::json)
      FROM answers_mvp a
      LEFT JOIN auth.users au ON a.user_id = au.id
      LEFT JOIN user_credits_mvp auc ON a.user_id = auc.user_id
      WHERE a.discussion_id = p_discussion_id
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- NEW RPC FUNCTION: update_user_display_name
-- Allows users to update their display name
-- ============================================

CREATE OR REPLACE FUNCTION update_user_display_name(
  p_user_id UUID,
  p_display_name TEXT
)
RETURNS JSON AS $$
DECLARE
  v_trimmed_name TEXT;
BEGIN
  -- Trim and validate display name
  v_trimmed_name := TRIM(p_display_name);
  
  -- Validate length
  IF v_trimmed_name IS NULL OR char_length(v_trimmed_name) < 2 THEN
    RETURN json_build_object(
      'success', FALSE,
      'error', '名稱至少需要 2 個字元'
    );
  END IF;
  
  IF char_length(v_trimmed_name) > 50 THEN
    RETURN json_build_object(
      'success', FALSE,
      'error', '名稱不能超過 50 個字元'
    );
  END IF;
  
  -- Ensure user has credits record
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (p_user_id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  
  -- Update display name
  UPDATE user_credits_mvp
  SET 
    display_name = v_trimmed_name,
    updated_at = NOW()
  WHERE user_id = p_user_id;
  
  RETURN json_build_object(
    'success', TRUE,
    'display_name', v_trimmed_name,
    'message', '名稱已更新'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- NEW RPC FUNCTION: get_user_profile
-- Returns user profile data including display name
-- ============================================

CREATE OR REPLACE FUNCTION get_user_profile(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
BEGIN
  -- Ensure user has credits record
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (p_user_id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  
  SELECT json_build_object(
    'user_id', uc.user_id,
    'display_name', uc.display_name,
    'google_name', u.raw_user_meta_data->>'full_name',
    'email', u.email,
    'credits', uc.credits,
    'total_earned', uc.total_earned,
    'total_spent', uc.total_spent,
    'reputation', uc.reputation,
    'effective_display_name', COALESCE(
      uc.display_name,
      u.raw_user_meta_data->>'full_name',
      SPLIT_PART(u.email, '@', 1)
    )
  ) INTO v_result
  FROM user_credits_mvp uc
  LEFT JOIN auth.users u ON uc.user_id = u.id
  WHERE uc.user_id = p_user_id;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
