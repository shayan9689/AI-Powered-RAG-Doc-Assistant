-- Run this in the Supabase SQL editor if you want hosted application tables.
-- Local development currently uses data/app_store.json.

create table if not exists documents (
  id uuid primary key,
  user_id text not null,
  filename text not null,
  file_type text not null,
  size_bytes integer not null,
  status text not null,
  page_count integer not null,
  chunk_count integer not null,
  created_at timestamptz not null default now()
);

create table if not exists conversations (
  id uuid primary key,
  user_id text not null,
  title text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists messages (
  id uuid primary key,
  conversation_id uuid not null references conversations(id) on delete cascade,
  role text not null,
  content text not null,
  sources jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

alter table documents enable row level security;
alter table conversations enable row level security;
alter table messages enable row level security;

create policy "documents_owner" on documents
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

create policy "conversations_owner" on conversations
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

create policy "messages_owner" on messages
  for all using (
    exists (
      select 1 from conversations c
      where c.id = messages.conversation_id and c.user_id = auth.uid()::text
    )
  );
