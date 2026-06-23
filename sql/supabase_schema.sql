-- Execute este script no SQL Editor do Supabase antes de sincronizar o app.
--
-- ATENÇÃO (repositório público / portfólio):
-- Este schema deixa RLS desabilitado para facilitar o uso single-user com anon key.
-- Para dados reais em produção, habilite Row Level Security e autenticação por usuário.
-- Use um projeto Supabase dedicado para testes — nunca exponha dados pessoais.

create table if not exists public.lancamentos (
  id bigint primary key,
  mes text not null,
  categoria text not null,
  valor double precision not null,
  observacao text default '',
  status_lancamento text default 'Pago',
  updated_at text default current_timestamp
);

create unique index if not exists lancamentos_mes_categoria_idx
on public.lancamentos (mes, categoria);

create table if not exists public.receitas (
  id bigint primary key,
  mes text not null,
  descricao text not null,
  valor double precision not null,
  observacao text default '',
  updated_at text default current_timestamp
);

create table if not exists public.metas (
  id bigint primary key,
  nome text not null,
  valor_alvo double precision not null,
  valor_atual double precision default 0,
  observacao text default '',
  updated_at text default current_timestamp
);

create table if not exists public.categorias (
  id bigint primary key,
  nome text not null unique,
  dia_vencimento integer,
  tipo text default 'manual',
  recorrente integer default 0,
  ativa integer default 1,
  updated_at text default current_timestamp
);

create table if not exists public.pendencias_ignoradas (
  id bigint primary key,
  mes text not null,
  categoria text not null,
  vencimento text not null,
  motivo text default 'regularizado',
  criado_em text default current_timestamp,
  updated_at text default current_timestamp
);

create unique index if not exists pendencias_ignoradas_unique_idx
on public.pendencias_ignoradas (mes, categoria, vencimento);

-- Para uso pessoal, a forma mais simples é deixar RLS desabilitado nessas tabelas.
-- Se quiser habilitar RLS no futuro, será necessário criar autenticação/login no app.
