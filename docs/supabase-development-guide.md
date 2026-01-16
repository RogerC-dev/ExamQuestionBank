# Supabase RPC-Led Development Guide

## Overview

This project uses **Supabase** as the backend with a **RPC-first architecture**. This guide explains the development patterns and best practices for the team.

---

## Architecture Tiers

| Tier | Use Case | Technology |
|------|----------|------------|
| **Tier 1: RPC Functions** | All database operations | PostgreSQL functions via `supabase.rpc()` |
| **Tier 2: Direct Client** | Simple single-table reads only | `supabase.from('table').select()` |
| **Tier 3: Edge Functions** | External API calls (AI, payments) | Deno TypeScript functions |

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vue.js)                     │
│            import { supabase } from '@/lib/supabase'     │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────┐ ┌───────────────────┐
│  RPC Functions  │ │Direct Client│ │  Edge Functions   │
│ (90% of calls)  │ │ (simple     │ │ (external APIs)   │
│                 │ │  reads)     │ │                   │
│ supabase.rpc()  │ │supabase     │ │ supabase.functions│
│                 │ │.from()      │ │ .invoke()         │
└─────────────────┘ └─────────────┘ └───────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│               PostgreSQL Database                        │
│           (Supabase hosted, Row Level Security)          │
└─────────────────────────────────────────────────────────┘
```

---

## Tier 1: RPC Functions (Primary)

### When to Use
- **All** database operations (CRUD)
- Multi-table JOINs
- Complex queries with filters/pagination
- Business logic (e.g., SM2 algorithm for flashcards)
- Atomic transactions

### Benefits
- ✅ Best performance (single round-trip)
- ✅ Business logic in database
- ✅ Atomic transactions
- ✅ SECURITY DEFINER for controlled access
- ✅ Consistent pattern across codebase

### Creating an RPC Function

```sql
-- In supabase/migrations/YYYYMMDD_your_migration.sql
CREATE OR REPLACE FUNCTION get_questions(
  p_subject TEXT DEFAULT NULL,
  p_difficulty TEXT DEFAULT NULL,
  p_page INTEGER DEFAULT 1,
  p_page_size INTEGER DEFAULT 20
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER  -- Bypasses RLS, use auth.uid() inside
AS $$
DECLARE
  result JSON;
  offset_val INTEGER;
BEGIN
  offset_val := (p_page - 1) * p_page_size;
  
  SELECT json_build_object(
    'results', COALESCE(json_agg(q), '[]'::json),
    'count', (SELECT COUNT(*) FROM question WHERE ...)
  ) INTO result
  FROM (
    SELECT * FROM question
    WHERE (p_subject IS NULL OR subject = p_subject)
      AND (p_difficulty IS NULL OR difficulty = p_difficulty)
    ORDER BY created_at DESC
    LIMIT p_page_size OFFSET offset_val
  ) q;
  
  RETURN result;
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION get_questions TO authenticated;
GRANT EXECUTE ON FUNCTION get_questions TO anon;  -- If public access needed
```

### Calling from Frontend

```javascript
// In services/questionService.js
import { supabase } from '@/lib/supabase'

async getQuestions(params = {}) {
  const { data, error } = await supabase.rpc('get_questions', {
    p_subject: params.subject || null,
    p_difficulty: params.difficulty || null,
    p_page: params.page || 1,
    p_page_size: params.page_size || 20
  })
  
  if (error) throw new Error(error.message)
  return { data }
}
```

---

## Tier 2: Direct Client (Simple Reads Only)

### When to Use
- Simple single-table SELECT with no complex logic
- Example: Fetching all tags for a dropdown

### Example

```javascript
// Only for very simple reads
async getTags() {
  const { data, error } = await supabase
    .from('tag')
    .select('*')
    .order('name')
  
  if (error) throw new Error(error.message)
  return { data }
}
```

### ⚠️ Avoid Direct Client For
- INSERT/UPDATE/DELETE (use RPC for consistency)
- Multi-table operations
- Any business logic

---

## Tier 3: Edge Functions (External APIs Only)

### When to Use
- **Only** for external API calls that require:
  - API keys (OpenAI, Stripe, etc.)
  - Complex external service integration
  - Server-side secrets

### Architecture Pattern

```
Frontend → Edge Function → External API → Edge Function → RPC → Database
```

### Example: AI Chat Edge Function

```typescript
// supabase/functions/ai-chat/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Get user from auth header
    const authHeader = req.headers.get('Authorization')
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      { global: { headers: { Authorization: authHeader! } } }
    )
    
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Get request body
    const { message, context_type, context_id } = await req.json()

    // Call external LLM API (OpenAI, Claude, etc.)
    const OPENAI_API_KEY = Deno.env.get('OPENAI_API_KEY')
    const aiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [{ role: 'user', content: message }]
      })
    })

    const aiData = await aiResponse.json()
    const reply = aiData.choices[0].message.content

    // Save to database via RPC
    await supabase.rpc('save_ai_conversation', {
      p_user_id: user.id,
      p_message: message,
      p_reply: reply,
      p_context_type: context_type,
      p_context_id: context_id
    })

    return new Response(JSON.stringify({ reply }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
```

### Calling Edge Function from Frontend

```javascript
// In services/aiService.js
async sendMessage(message, contextType, contextId) {
  const { data, error } = await supabase.functions.invoke('ai-chat', {
    body: { message, context_type: contextType, context_id: contextId }
  })
  
  if (error) throw new Error(error.message)
  return data
}
```

---

## Current RPC Functions

| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_questions` | List questions with filters | `p_subject`, `p_difficulty`, `p_type`, `p_year`, `p_keyword`, `p_page`, `p_page_size` |
| `get_question_detail` | Single question with options | `p_id` |
| `get_user_exams` | User's own exams | none |
| `get_practice_exams` | All available exams | none |
| `get_exam_detail` | Exam with nested questions | `p_id` |
| `get_exam_results` | User's exam history | none |
| `save_exam_result` | Save result + track wrong | `p_exam_id`, `p_exam_name`, `p_score`, `p_correct_count`, `p_total_count`, `p_duration_seconds`, `p_answers_json`, `p_wrong_question_ids` |
| `get_wrong_questions` | User's incorrect answers | none |
| `get_bookmarks` | User's bookmarked questions | none |
| `get_flashcards` | User's flashcards | none |
| `get_due_flashcards` | Cards due for review | `p_limit` |
| `get_flashcard_stats` | Flashcard statistics | none |
| `review_flashcard` | SM2 algorithm update | `p_flashcard_id`, `p_rating` |
| `get_user_analytics` | Dashboard statistics | none |

---

## Development Workflow

### 1. Adding a New Feature

```bash
# 1. Create migration file
touch supabase/migrations/YYYYMMDDHHMMSS_feature_name.sql

# 2. Write RPC function in migration file
# 3. Test locally
supabase db push

# 4. Deploy
supabase db push --linked
```

### 2. Frontend Service Pattern

```javascript
// services/yourService.js
import { supabase } from '@/lib/supabase'

const yourService = {
  async getData(params) {
    const { data, error } = await supabase.rpc('your_rpc_function', {
      p_param1: params.param1,
      p_param2: params.param2
    })
    if (error) throw new Error(error.message)
    return { data }
  },

  async createData(payload) {
    const { data, error } = await supabase.rpc('create_your_data', {
      p_field1: payload.field1,
      p_field2: payload.field2
    })
    if (error) throw new Error(error.message)
    return { data }
  }
}

export default yourService
```

---

## Security Notes

1. **SECURITY DEFINER**: RPC functions bypass RLS, so always use `auth.uid()` inside to check user
2. **GRANT EXECUTE**: Only grant to roles that need access (`authenticated`, `anon`)
3. **Input Validation**: Validate all inputs in the function
4. **Edge Function Secrets**: Store API keys in Supabase Dashboard → Edge Functions → Secrets

---

## File Structure

```
project/
├── frontend/
│   └── src/
│       ├── lib/
│       │   └── supabase.js          # Supabase client
│       └── services/
│           ├── examService.js       # Uses RPC
│           ├── questionService.js   # Uses RPC
│           ├── flashcardService.js  # Uses RPC
│           ├── aiService.js         # Uses Edge Function
│           └── tagService.js        # Simple reads, can use direct
│
└── supabase/
    ├── functions/
    │   ├── _shared/                  # Utilities
    │   └── ai-chat/                  # AI Edge Function
    └── migrations/
        ├── YYYYMMDD_schema.sql       # Tables
        └── YYYYMMDD_rpc_functions.sql # RPC functions
```

---

## Summary

| ❌ Don't | ✅ Do |
|----------|-------|
| Use Edge Functions for CRUD | Use RPC for all database ops |
| Mix patterns inconsistently | Use RPC-first consistently |
| Put business logic in frontend | Put logic in RPC functions |
| Call external APIs from frontend | Use Edge Functions with secrets |

**Remember: RPC functions are your primary tool. Edge Functions are only for external APIs that need server-side secrets.**
