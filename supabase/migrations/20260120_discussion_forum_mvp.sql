-- Discussion Forum MVP Migration (Updated)
-- Creates 5 tables, 5 RPC functions, triggers, and RLS policies

-- Enable UUID extension (required for uuid_generate_v4)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLES
-- ============================================

-- 1. Discussions table
CREATE TABLE discussions_mvp (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL CHECK (char_length(title) >= 10),
  body TEXT NOT NULL CHECK (char_length(body) >= 20),
  view_count INTEGER DEFAULT 0,
  answer_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_discussions_mvp_created ON discussions_mvp(created_at DESC);
CREATE INDEX idx_discussions_mvp_user ON discussions_mvp(user_id);

-- 2. Answers table
CREATE TABLE answers_mvp (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  discussion_id UUID REFERENCES discussions_mvp(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  body TEXT NOT NULL CHECK (char_length(body) >= 50),
  vote_count INTEGER DEFAULT 0,
  unlock_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_answers_mvp_discussion ON answers_mvp(discussion_id);
CREATE INDEX idx_answers_mvp_user ON answers_mvp(user_id);
CREATE INDEX idx_answers_mvp_votes ON answers_mvp(vote_count DESC);

-- 3. User credits table
CREATE TABLE user_credits_mvp (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  credits INTEGER DEFAULT 100 CHECK (credits >= 0),
  total_earned INTEGER DEFAULT 100,
  total_spent INTEGER DEFAULT 0,
  last_daily_claim TIMESTAMPTZ,
  reputation INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Unlocks table
CREATE TABLE unlocks_mvp (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  answer_id UUID REFERENCES answers_mvp(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, answer_id)
);

CREATE INDEX idx_unlocks_mvp_user ON unlocks_mvp(user_id);
CREATE INDEX idx_unlocks_mvp_answer ON unlocks_mvp(answer_id);

-- 5. Votes table
CREATE TABLE votes_mvp (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  answer_id UUID REFERENCES answers_mvp(id) ON DELETE CASCADE,
  vote_value INTEGER NOT NULL CHECK (vote_value IN (-1, 1)),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, answer_id)
);

CREATE INDEX idx_votes_mvp_user ON votes_mvp(user_id);
CREATE INDEX idx_votes_mvp_answer ON votes_mvp(answer_id);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Initialize user credits on registration
CREATE OR REPLACE FUNCTION initialize_user_credits_mvp()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (NEW.id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_initialize_user_credits_mvp
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION initialize_user_credits_mvp();

-- Trigger: Update answer count on discussions
CREATE OR REPLACE FUNCTION update_answer_count_mvp()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE discussions_mvp 
    SET answer_count = answer_count + 1
    WHERE id = NEW.discussion_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE discussions_mvp 
    SET answer_count = answer_count - 1
    WHERE id = OLD.discussion_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_update_answer_count_mvp
AFTER INSERT OR DELETE ON answers_mvp
FOR EACH ROW EXECUTE FUNCTION update_answer_count_mvp();

-- ============================================
-- RPC FUNCTIONS
-- ============================================

-- Function 1: Get discussions list with pagination
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
    d.view_count::INTEGER,
    d.answer_count::INTEGER,
    d.created_at
  FROM discussions_mvp d
  LEFT JOIN auth.users u ON d.user_id = u.id
  ORDER BY d.created_at DESC
  LIMIT p_limit
  OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function 2: Get discussion detail with answers
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
        'view_count', d.view_count,
        'answer_count', d.answer_count,
        'created_at', d.created_at
      )
      FROM discussions_mvp d
      LEFT JOIN auth.users u ON d.user_id = u.id
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
      WHERE a.discussion_id = p_discussion_id
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function 3: Unlock answer
CREATE OR REPLACE FUNCTION unlock_answer_mvp(
  p_user_id UUID,
  p_answer_id UUID
)
RETURNS JSON AS $$
DECLARE
  v_credits INTEGER;
  v_answer_body TEXT;
  v_unlock_cost INTEGER := 20;
  v_discussion_user_id UUID;
  v_answer_user_id UUID;
BEGIN
  -- Get answer info
  SELECT a.body, a.user_id, d.user_id 
  INTO v_answer_body, v_answer_user_id, v_discussion_user_id
  FROM answers_mvp a
  JOIN discussions_mvp d ON a.discussion_id = d.id
  WHERE a.id = p_answer_id;

  -- Check if user is the answer author or discussion owner (free access)
  IF v_answer_user_id = p_user_id OR v_discussion_user_id = p_user_id THEN
    RETURN json_build_object(
      'success', TRUE,
      'answer_body', v_answer_body,
      'credits_spent', 0,
      'message', 'Free access - no credits needed'
    );
  END IF;

  -- Check if already unlocked
  IF EXISTS (
    SELECT 1 FROM unlocks_mvp 
    WHERE user_id = p_user_id AND answer_id = p_answer_id
  ) THEN
    RETURN json_build_object(
      'success', TRUE,
      'answer_body', v_answer_body,
      'credits_spent', 0,
      'message', 'Already unlocked'
    );
  END IF;
  
  -- Ensure user has credits record
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (p_user_id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  
  -- Get user credits
  SELECT credits INTO v_credits
  FROM user_credits_mvp WHERE user_id = p_user_id;
  
  -- Check sufficient credits
  IF v_credits < v_unlock_cost THEN
    RETURN json_build_object(
      'success', FALSE,
      'error', '點數不足。您有 ' || v_credits || ' 點數，但需要 ' || v_unlock_cost || ' 點數',
      'credits_required', v_unlock_cost,
      'credits_available', v_credits
    );
  END IF;
  
  -- Deduct credits
  UPDATE user_credits_mvp 
  SET 
    credits = credits - v_unlock_cost,
    total_spent = total_spent + v_unlock_cost,
    updated_at = NOW()
  WHERE user_id = p_user_id;
  
  -- Create unlock record
  INSERT INTO unlocks_mvp (user_id, answer_id)
  VALUES (p_user_id, p_answer_id);
  
  -- Increment unlock count on answer
  UPDATE answers_mvp SET unlock_count = unlock_count + 1
  WHERE id = p_answer_id;
  
  -- Return result
  RETURN json_build_object(
    'success', TRUE,
    'answer_body', v_answer_body,
    'credits_spent', v_unlock_cost,
    'remaining_credits', v_credits - v_unlock_cost
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function 4: Cast vote
CREATE OR REPLACE FUNCTION cast_vote_mvp(
  p_user_id UUID,
  p_answer_id UUID,
  p_vote_value INTEGER
)
RETURNS JSON AS $$
DECLARE
  v_old_vote INTEGER := 0;
  v_vote_delta INTEGER;
  v_answer_user_id UUID;
  v_new_vote_count INTEGER;
  v_reputation_delta INTEGER := 0;
BEGIN
  -- Validate vote value
  IF p_vote_value NOT IN (-1, 1) THEN
    RETURN json_build_object(
      'success', FALSE,
      'error', 'Invalid vote value'
    );
  END IF;
  
  -- Get existing vote
  SELECT vote_value INTO v_old_vote
  FROM votes_mvp
  WHERE user_id = p_user_id AND answer_id = p_answer_id;
  
  -- Calculate delta
  v_vote_delta := p_vote_value - COALESCE(v_old_vote, 0);
  
  -- Upsert vote
  INSERT INTO votes_mvp (user_id, answer_id, vote_value)
  VALUES (p_user_id, p_answer_id, p_vote_value)
  ON CONFLICT (user_id, answer_id)
  DO UPDATE SET vote_value = p_vote_value;
  
  -- Update vote count on answer and get answer author
  UPDATE answers_mvp 
  SET vote_count = vote_count + v_vote_delta
  WHERE id = p_answer_id
  RETURNING user_id, vote_count INTO v_answer_user_id, v_new_vote_count;
  
  -- Ensure answer author has credits record
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (v_answer_user_id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  
  -- Award credits and reputation for new upvote
  IF p_vote_value = 1 AND COALESCE(v_old_vote, 0) != 1 THEN
    UPDATE user_credits_mvp
    SET 
      credits = credits + 10,
      total_earned = total_earned + 10,
      reputation = reputation + 10,
      updated_at = NOW()
    WHERE user_id = v_answer_user_id;
    v_reputation_delta := 10;
  -- Remove credits/reputation if changing from upvote
  ELSIF COALESCE(v_old_vote, 0) = 1 AND p_vote_value != 1 THEN
    UPDATE user_credits_mvp
    SET 
      credits = GREATEST(0, credits - 10),
      reputation = reputation - 10,
      updated_at = NOW()
    WHERE user_id = v_answer_user_id;
    v_reputation_delta := -10;
  END IF;
  
  -- Decrease reputation for downvote
  IF p_vote_value = -1 AND COALESCE(v_old_vote, 0) != -1 THEN
    UPDATE user_credits_mvp
    SET 
      reputation = reputation - 5,
      updated_at = NOW()
    WHERE user_id = v_answer_user_id;
    v_reputation_delta := v_reputation_delta - 5;
  -- Restore reputation if changing from downvote
  ELSIF COALESCE(v_old_vote, 0) = -1 AND p_vote_value != -1 THEN
    UPDATE user_credits_mvp
    SET 
      reputation = reputation + 5,
      updated_at = NOW()
    WHERE user_id = v_answer_user_id;
    v_reputation_delta := v_reputation_delta + 5;
  END IF;
  
  RETURN json_build_object(
    'success', TRUE,
    'new_vote_count', v_new_vote_count,
    'reputation_delta', v_reputation_delta
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function 5: Claim daily credits
CREATE OR REPLACE FUNCTION claim_daily_credits_mvp(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_last_claim TIMESTAMPTZ;
  v_new_balance INTEGER;
  v_credits_awarded INTEGER := 20;
BEGIN
  -- Ensure user has credits record
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (p_user_id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  
  -- Get last claim time
  SELECT last_daily_claim INTO v_last_claim
  FROM user_credits_mvp
  WHERE user_id = p_user_id;
  
  -- Check if 24 hours passed
  IF v_last_claim IS NOT NULL AND 
     v_last_claim > NOW() - INTERVAL '24 hours' THEN
    RETURN json_build_object(
      'success', FALSE,
      'error', '每日獎勵已領取。下次可領取時間：' || to_char(v_last_claim + INTERVAL '24 hours', 'YYYY-MM-DD HH24:MI'),
      'next_claim_at', v_last_claim + INTERVAL '24 hours'
    );
  END IF;
  
  -- Award credits
  UPDATE user_credits_mvp
  SET 
    credits = credits + v_credits_awarded,
    total_earned = total_earned + v_credits_awarded,
    last_daily_claim = NOW(),
    updated_at = NOW()
  WHERE user_id = p_user_id
  RETURNING credits INTO v_new_balance;
  
  RETURN json_build_object(
    'success', TRUE,
    'credits_earned', v_credits_awarded,
    'new_balance', v_new_balance,
    'next_claim_at', NOW() + INTERVAL '24 hours'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function 6: Get user credits
CREATE OR REPLACE FUNCTION get_user_credits_mvp(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
BEGIN
  -- Ensure user has credits record
  INSERT INTO user_credits_mvp (user_id, credits, total_earned)
  VALUES (p_user_id, 100, 100)
  ON CONFLICT (user_id) DO NOTHING;
  
  SELECT json_build_object(
    'credits', credits,
    'total_earned', total_earned,
    'total_spent', total_spent,
    'reputation', reputation,
    'last_daily_claim', last_daily_claim,
    'can_claim_daily', (last_daily_claim IS NULL OR last_daily_claim < NOW() - INTERVAL '24 hours')
  ) INTO v_result
  FROM user_credits_mvp
  WHERE user_id = p_user_id;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Discussions: Public read, authenticated write
ALTER TABLE discussions_mvp ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view discussions"
  ON discussions_mvp FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can create discussions"
  ON discussions_mvp FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own discussions"
  ON discussions_mvp FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own discussions"
  ON discussions_mvp FOR DELETE
  USING (auth.uid() = user_id);

-- Answers: Public metadata read, authenticated write
ALTER TABLE answers_mvp ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view answer metadata"
  ON answers_mvp FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can create answers"
  ON answers_mvp FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own answers"
  ON answers_mvp FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own answers"
  ON answers_mvp FOR DELETE
  USING (auth.uid() = user_id);

-- User credits: Users can only see their own
ALTER TABLE user_credits_mvp ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own credits"
  ON user_credits_mvp FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own credits"
  ON user_credits_mvp FOR UPDATE
  USING (auth.uid() = user_id);

-- Votes: Users can manage their own votes
ALTER TABLE votes_mvp ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view votes"
  ON votes_mvp FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can vote"
  ON votes_mvp FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own votes"
  ON votes_mvp FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own votes"
  ON votes_mvp FOR DELETE
  USING (auth.uid() = user_id);

-- Unlocks: Users can only see their own unlocks
ALTER TABLE unlocks_mvp ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own unlocks"
  ON unlocks_mvp FOR SELECT
  USING (auth.uid() = user_id);
