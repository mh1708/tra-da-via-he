-- Sổ ghi nợ chung của quán Trà Đá Vỉa Hè.
-- Chạy một lần trong Supabase: SQL Editor -> New query -> dán toàn bộ -> Run.
-- Mỗi khách (đăng nhập ẩn danh) chỉ ghi và sửa được dòng của chính mình; ai cũng xem được sổ.

create table if not exists public.cups (
  id uuid primary key default auth.uid() references auth.users on delete cascade,
  name text not null check (char_length(name) between 1 and 18),
  n integer not null default 0 check (n between 0 and 100000),
  updated_at timestamptz not null default now()
);

alter table public.cups enable row level security;

drop policy if exists "ai cung xem so" on public.cups;
create policy "ai cung xem so" on public.cups
  for select using (true);

drop policy if exists "tu ghi dong cua minh" on public.cups;
create policy "tu ghi dong cua minh" on public.cups
  for insert with check (auth.uid() = id);

drop policy if exists "tu sua dong cua minh" on public.cups;
create policy "tu sua dong cua minh" on public.cups
  for update using (auth.uid() = id) with check (auth.uid() = id);
