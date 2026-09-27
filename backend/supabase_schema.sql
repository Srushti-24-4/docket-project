-- Run this in the Supabase SQL editor before first use.

create table if not exists documents (
  id uuid primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  filename text not null,
  route text not null check (route in (
    'normal_pdf', 'scanned_pdf', 'table_heavy', 'image', 'docx', 'plain_text'
  )),
  page_count integer not null default 0,
  storage_path text not null,
  created_at timestamptz not null default now()
);

create index if not exists documents_user_id_idx on documents(user_id);

alter table documents enable row level security;

-- The backend calls Supabase with the service role key, which bypasses RLS
-- entirely — these policies matter if you ever query Supabase directly from
-- the frontend with the user's own session instead of going through the API.
create policy "users can view their own documents"
  on documents for select
  using (auth.uid() = user_id);

create policy "users can insert their own documents"
  on documents for insert
  with check (auth.uid() = user_id);

create policy "users can delete their own documents"
  on documents for delete
  using (auth.uid() = user_id);

-- Storage bucket: create it from the Supabase dashboard (Storage -> New
-- bucket), named to match SUPABASE_STORAGE_BUCKET in your .env (default
-- "documents"). Files are stored under {user_id}/{document_id}/{filename},
-- so a matching storage policy keeps each user's files private:
--
-- Storage -> your bucket -> Policies -> New policy -> "Custom":
--   USING: (storage.foldername(name))[1] = auth.uid()::text

-- --- Auth settings (do this in the dashboard, not SQL) ---
-- Authentication -> Providers -> Email:
--   - Enable "Confirm email" so new signups must verify their address
--     before they can log in. Supabase sends the confirmation email
--     automatically when the frontend calls supabase.auth.signUp().
-- Authentication -> URL Configuration:
--   - Set "Site URL" to your frontend's URL (e.g. http://localhost:3000
--     for local dev, your Vercel URL in production).
--   - Add http://localhost:3000/reset-password (and your prod equivalent)
--     to "Redirect URLs" so the password-reset email link works.
