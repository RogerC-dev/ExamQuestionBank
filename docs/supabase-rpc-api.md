# Supabase RPC API

This document describes the Postgres RPC function exposed in Supabase for
creating questions with options and tags.

## Function: public.add_question

Creates a question in `public.question`, then inserts related options in
`public.question_option` and tag links in `public.question_tag`.

### Auth

`EXECUTE` is granted to the `authenticated` role. The function runs as
`SECURITY DEFINER` and sets `creator` to `auth.uid()` when available.

### Parameters

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| content | text | yes | Trimmed; empty content raises error. |
| explanation | text | no | Empty string becomes NULL. |
| question_type | text | no | Accepts `essay` or `multipleChoice`. If not provided or invalid, the function picks `multipleChoice` when options exist, otherwise `essay`. |
| difficulty | text | no | Accepts `easy`, `normal`, `hard`, `insane`. If `medium`, it is mapped to `normal`. Anything else falls back to `normal`. |
| subject | text | no | Empty string becomes NULL. |
| category | text | no | Empty string becomes NULL. |
| year | smallint | no | Stored on the question row. |
| source | text | no | Empty string becomes NULL. |
| options | jsonb | no | JSON array of option objects. Non-array or empty array means no options. |
| tag_ids | bigint[] | no | Tag IDs to insert into `public.question_tag`. |
| creator | uuid | no | Used only when `auth.uid()` is NULL (e.g., service role). |
| status | text | no | Accepted for compatibility but ignored (no column in Supabase schema). |

### options format

Each option item accepts:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| content | text | yes | Empty content is skipped. |
| is_correct | boolean | no | Defaults to `false`. |
| order | smallint | no | Defaults to the array order (1..n). |

If you provide duplicate `order` values, the insert will fail due to the
`question_option` unique constraint on `(question_id, order)`.

### Returns

`bigint` - the newly created `question.id`.

### Example (SQL)

```sql
select public.add_question(
  content => 'Sample question?',
  question_type => 'multipleChoice',
  difficulty => 'normal',
  options => '[{"content":"A","is_correct":true},{"content":"B","is_correct":false}]'::jsonb,
  tag_ids => '{1,2}'::bigint[]
);
```

### Example (Supabase JS)

```ts
const { data, error } = await supabase.rpc('add_question', {
  content: 'Sample question?',
  question_type: 'multipleChoice',
  difficulty: 'normal',
  options: [
    { content: 'A', is_correct: true },
    { content: 'B', is_correct: false }
  ],
  tag_ids: [1, 2]
})
```

### Notes

- `public.question.type` is stored as `public.question_type` enum.
- `public.question.difficulty` is stored as `public.question_difficulty` enum.
- The function trims text fields and converts empty strings to NULL where
  applicable.
