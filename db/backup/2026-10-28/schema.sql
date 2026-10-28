--
-- PostgreSQL database dump
--

\restrict WXAUoa6HzF2kURAMB1dPlCvFn0sxtijYq740EHkwcuuIFsiLb5FpgiJNBnfGka9

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.11 (Debian 17.11-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: admin_search_misses(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.admin_search_misses(p_days integer DEFAULT 90) RETURNS TABLE(term text, visitor_id uuid, created_at timestamp with time zone, decision text)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;
  return query
    select q.term, q.visitor_id, q.created_at, d.decision
      from search_queries q
      left join search_term_decisions d on d.term = q.term
     where q.hit_count = 0
       and char_length(q.term) >= 2
       and q.created_at >= now() - make_interval(days => greatest(p_days, 1))
     order by q.created_at;
end;
$$;


--
-- Name: admin_set_search_decision(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.admin_set_search_decision(p_term text, p_decision text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;
  if p_decision is null then
    delete from search_term_decisions where term = p_term;
  else
    insert into search_term_decisions (term, decision) values (p_term, p_decision)
    on conflict (term) do update set decision = excluded.decision, decided_at = now();
  end if;
end;
$$;


--
-- Name: admin_visitor_breakdown(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.admin_visitor_breakdown(p_since_days integer DEFAULT 7) RETURNS TABLE(kind text, label text, visitors bigint, views bigint)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
declare
  since timestamptz;
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  since := case when p_since_days is null
                then '-infinity'::timestamptz
                else now() - make_interval(days => greatest(least(p_since_days, 365), 1)) end;
  since := greatest(since, stats_since());

  return query
  (select 'path'::text, pv.path,
          count(distinct pv.visitor_id), count(*)
     from page_views_human pv where pv.created_at >= since
     group by pv.path order by count(*) desc limit 20)
  union all
  (select 'referrer'::text, coalesce(pv.referrer_host, '(직접 유입)'),
          count(distinct pv.visitor_id), count(*)
     from page_views_human pv where pv.created_at >= since
     group by 2 order by count(*) desc limit 20);
end;
$$;


--
-- Name: admin_visitor_breakdown_page(text, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.admin_visitor_breakdown_page(p_kind text, p_since_days integer DEFAULT 7, p_limit integer DEFAULT 30, p_offset integer DEFAULT 0) RETURNS TABLE(label text, visitors bigint, views bigint, total_rows bigint)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
declare
  since timestamptz;
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  if p_kind is null or p_kind not in ('path', 'referrer') then
    raise exception 'unknown kind: %', p_kind;
  end if;

  since := case when p_since_days is null
                then '-infinity'::timestamptz
                else now() - make_interval(days => greatest(least(p_since_days, 365), 1)) end;
  since := greatest(since, stats_since());

  return query
  with base as (
    select case when p_kind = 'path'
                then pv.path
                else coalesce(pv.referrer_host, '(직접 유입)') end as label,
           pv.visitor_id
      from page_views_human pv
     where pv.created_at >= since
  ),
  agg as (
    select b.label, count(distinct b.visitor_id) as visitors, count(*) as views
      from base b
     group by b.label
  )
  select a.label, a.visitors, a.views, count(*) over () as total_rows
    from agg a
   order by a.views desc, a.label
   limit greatest(least(p_limit, 100), 1)
  offset greatest(coalesce(p_offset, 0), 0);
end;
$$;


--
-- Name: admin_visitor_daily(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.admin_visitor_daily(p_days integer DEFAULT 14) RETURNS TABLE(day date, visitors bigint, views bigint)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
declare
  floor_at timestamptz := stats_since();
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  return query
  with span as (
    select generate_series(
      greatest(
        (now() at time zone 'Asia/Seoul')::date - (greatest(least(p_days, 90), 1) - 1),
        (floor_at at time zone 'Asia/Seoul')::date),
      (now() at time zone 'Asia/Seoul')::date,
      interval '1 day'
    )::date as day
  ),
  agg as (
    select (pv.created_at at time zone 'Asia/Seoul')::date as day,
           count(distinct pv.visitor_id) as visitors,
           count(*) as views
    from page_views_human pv
    where pv.created_at >= floor_at
    group by 1
  )
  select s.day, coalesce(a.visitors, 0), coalesce(a.views, 0)
  from span s left join agg a on a.day = s.day
  order by s.day;
end;
$$;


--
-- Name: admin_visitor_stats(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.admin_visitor_stats() RETURNS TABLE(concurrent_visitors bigint, today_visitors bigint, total_visitors bigint, today_views bigint, total_views bigint, first_view_at timestamp with time zone, since_at timestamp with time zone)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
declare
  kst_midnight timestamptz;
  floor_at timestamptz := stats_since();
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  kst_midnight := greatest(
    date_trunc('day', now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul',
    floor_at);

  return query select
    (select count(distinct pv.visitor_id) from page_views_human pv
      where pv.created_at > now() - interval '5 minutes' and pv.created_at >= floor_at),
    (select count(distinct pv.visitor_id) from page_views_human pv
      where pv.created_at >= kst_midnight),
    (select count(distinct pv.visitor_id) from page_views_human pv
      where pv.created_at >= floor_at),
    (select count(*) from page_views_human pv where pv.created_at >= kst_midnight),
    (select count(*) from page_views_human pv where pv.created_at >= floor_at),
    (select min(pv.created_at) from page_views_human pv where pv.created_at >= floor_at),
    floor_at;
end;
$$;


--
-- Name: is_admin(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_admin() RETURNS boolean
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
  select exists (
    select 1 from admins a
    where a.email = lower(nullif(auth.jwt() ->> 'email', ''))
  );
$$;


--
-- Name: is_bot_ua(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_bot_ua() RETURNS boolean
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
declare
  ua text;
begin
  begin
    ua := lower(coalesce(current_setting('request.headers', true)::json ->> 'user-agent', ''));
  exception when others then
    return false;
  end;
  if ua = '' then
    return false;
  end if;
  return ua ~ '(bot|crawl|spider|slurp|headless|preview|monitor|lighthouse|curl|wget|python-requests|axios|node-fetch|facebookexternalhit|embedly|yeti|daum)';
end;
$$;


--
-- Name: purge_old_logs(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.purge_old_logs() RETURNS TABLE(purged_page_views bigint, purged_search_queries bigint)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
declare
  v_pv bigint;
  v_sq bigint;
begin
  delete from page_views where created_at < now() - interval '12 months';
  get diagnostics v_pv = row_count;
  delete from search_queries where created_at < now() - interval '24 months';
  get diagnostics v_sq = row_count;
  return query select v_pv, v_sq;
end;
$$;


--
-- Name: rls_auto_enable(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.rls_auto_enable() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


--
-- Name: stats_since(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.stats_since() RETURNS timestamp with time zone
    LANGUAGE sql IMMUTABLE
    AS $$
  select '2026-09-08 00:00:00+09'::timestamptz;
$$;


--
-- Name: track_page_view(uuid, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.track_page_view(p_visitor_id uuid, p_path text, p_referrer_host text DEFAULT NULL::text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
begin
  if p_path is null or char_length(p_path) = 0 then
    return;
  end if;
  if p_path like '/admin%' then
    return;
  end if;
  if is_bot_ua() then
    return;
  end if;
  insert into page_views (visitor_id, path, referrer_host)
  values (p_visitor_id, left(p_path, 200), left(nullif(p_referrer_host, ''), 100));
end;
$$;


--
-- Name: track_search_query(text, integer, uuid); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.track_search_query(p_term text, p_hit_count integer, p_visitor_id uuid DEFAULT NULL::uuid) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
begin
  if p_term is null or char_length(trim(p_term)) < 2 then
    return;
  end if;
  if is_bot_ua() then
    return;
  end if;
  insert into search_queries (term, hit_count, visitor_id)
  values (left(trim(p_term), 60), greatest(coalesce(p_hit_count, 0), 0), p_visitor_id);
end;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admins (
    email text NOT NULL,
    label text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: bulky_fees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bulky_fees (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    region_code text NOT NULL,
    item_name text NOT NULL,
    item_slug text,
    spec text,
    fee integer NOT NULL,
    source_url text NOT NULL,
    as_of date NOT NULL
);


--
-- Name: guideline_verdicts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.guideline_verdicts (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    item_name text NOT NULL,
    verdict text NOT NULL,
    category text,
    subitem text,
    basis text,
    source_url text NOT NULL,
    as_of date NOT NULL,
    CONSTRAINT guideline_verdicts_verdict_check CHECK ((verdict = ANY (ARRAY['O'::text, 'X'::text])))
);


--
-- Name: item_region_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.item_region_rules (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    item_slug text NOT NULL,
    region_code text NOT NULL,
    verdict text NOT NULL,
    note text,
    source_url text NOT NULL,
    as_of date NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.items (
    slug text NOT NULL,
    name text NOT NULL,
    aliases text[] DEFAULT '{}'::text[] NOT NULL,
    verdict text,
    verdict_line text,
    category text,
    housing_split boolean DEFAULT false NOT NULL,
    region_varies boolean DEFAULT false NOT NULL,
    monthly_volume integer,
    competitor_has boolean DEFAULT false NOT NULL,
    published boolean DEFAULT false NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT items_published_needs_verdict CHECK (((NOT published) OR ((verdict IS NOT NULL) AND (verdict_line IS NOT NULL)))),
    CONSTRAINT items_verdict_check CHECK ((verdict = ANY (ARRAY['재활용'::text, '일반쓰레기'::text, '대형폐기물'::text, '전용수거함'::text, '무상수거'::text, '음식물'::text, '조건부'::text])))
);


--
-- Name: page_views; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.page_views (
    id bigint NOT NULL,
    visitor_id uuid NOT NULL,
    path text NOT NULL,
    referrer_host text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: page_views_human; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.page_views_human WITH (security_invoker='true') AS
 WITH single AS (
         SELECT page_views.visitor_id
           FROM public.page_views
          GROUP BY page_views.visitor_id
         HAVING (count(*) = 1)
        ), lone AS (
         SELECT pv_1.id,
            count(*) OVER (ORDER BY pv_1.created_at RANGE BETWEEN '00:10:00'::interval PRECEDING AND '00:10:00'::interval FOLLOWING) AS crowd
           FROM (public.page_views pv_1
             JOIN single s USING (visitor_id))
          WHERE (pv_1.referrer_host IS NULL)
        )
 SELECT id,
    visitor_id,
    path,
    referrer_host,
    created_at
   FROM public.page_views pv
  WHERE (NOT (id IN ( SELECT l.id
           FROM lone l
          WHERE (l.crowd >= 5))));


--
-- Name: page_views_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.page_views ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.page_views_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: regions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.regions (
    code text NOT NULL,
    sido text NOT NULL,
    sigungu text,
    name text NOT NULL
);


--
-- Name: search_queries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_queries (
    id bigint NOT NULL,
    term text NOT NULL,
    hit_count integer NOT NULL,
    visitor_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: search_queries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.search_queries ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.search_queries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: search_term_decisions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_term_decisions (
    term text NOT NULL,
    decision text NOT NULL,
    decided_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT search_term_decisions_decision_check CHECK ((decision = ANY (ARRAY['보류'::text, '노이즈'::text])))
);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (email);


--
-- Name: bulky_fees bulky_fees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bulky_fees
    ADD CONSTRAINT bulky_fees_pkey PRIMARY KEY (id);


--
-- Name: bulky_fees bulky_fees_region_code_item_name_spec_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bulky_fees
    ADD CONSTRAINT bulky_fees_region_code_item_name_spec_key UNIQUE (region_code, item_name, spec);


--
-- Name: guideline_verdicts guideline_verdicts_item_name_category_subitem_verdict_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guideline_verdicts
    ADD CONSTRAINT guideline_verdicts_item_name_category_subitem_verdict_key UNIQUE (item_name, category, subitem, verdict);


--
-- Name: guideline_verdicts guideline_verdicts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guideline_verdicts
    ADD CONSTRAINT guideline_verdicts_pkey PRIMARY KEY (id);


--
-- Name: item_region_rules item_region_rules_item_slug_region_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_region_rules
    ADD CONSTRAINT item_region_rules_item_slug_region_code_key UNIQUE (item_slug, region_code);


--
-- Name: item_region_rules item_region_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_region_rules
    ADD CONSTRAINT item_region_rules_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (slug);


--
-- Name: page_views page_views_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.page_views
    ADD CONSTRAINT page_views_pkey PRIMARY KEY (id);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (code);


--
-- Name: search_queries search_queries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_queries
    ADD CONSTRAINT search_queries_pkey PRIMARY KEY (id);


--
-- Name: search_term_decisions search_term_decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_term_decisions
    ADD CONSTRAINT search_term_decisions_pkey PRIMARY KEY (term);


--
-- Name: bulky_region_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bulky_region_idx ON public.bulky_fees USING btree (region_code);


--
-- Name: bulky_slug_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bulky_slug_idx ON public.bulky_fees USING btree (item_slug);


--
-- Name: irr_item_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX irr_item_idx ON public.item_region_rules USING btree (item_slug);


--
-- Name: items_volume_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX items_volume_idx ON public.items USING btree (monthly_volume DESC NULLS LAST);


--
-- Name: page_views_created_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX page_views_created_idx ON public.page_views USING btree (created_at DESC);


--
-- Name: page_views_visitor_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX page_views_visitor_idx ON public.page_views USING btree (visitor_id, created_at DESC);


--
-- Name: regions_sido_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX regions_sido_idx ON public.regions USING btree (sido);


--
-- Name: search_queries_created_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX search_queries_created_idx ON public.search_queries USING btree (created_at DESC);


--
-- Name: search_queries_miss_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX search_queries_miss_idx ON public.search_queries USING btree (term) WHERE (hit_count = 0);


--
-- Name: bulky_fees bulky_fees_item_slug_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bulky_fees
    ADD CONSTRAINT bulky_fees_item_slug_fkey FOREIGN KEY (item_slug) REFERENCES public.items(slug) ON DELETE SET NULL;


--
-- Name: bulky_fees bulky_fees_region_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bulky_fees
    ADD CONSTRAINT bulky_fees_region_code_fkey FOREIGN KEY (region_code) REFERENCES public.regions(code) ON DELETE CASCADE;


--
-- Name: item_region_rules item_region_rules_item_slug_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_region_rules
    ADD CONSTRAINT item_region_rules_item_slug_fkey FOREIGN KEY (item_slug) REFERENCES public.items(slug) ON DELETE CASCADE;


--
-- Name: item_region_rules item_region_rules_region_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_region_rules
    ADD CONSTRAINT item_region_rules_region_code_fkey FOREIGN KEY (region_code) REFERENCES public.regions(code) ON DELETE CASCADE;


--
-- Name: admins; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.admins ENABLE ROW LEVEL SECURITY;

--
-- Name: bulky_fees; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.bulky_fees ENABLE ROW LEVEL SECURITY;

--
-- Name: bulky_fees bulky_fees_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY bulky_fees_read ON public.bulky_fees FOR SELECT TO authenticated, anon USING (true);


--
-- Name: guideline_verdicts; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.guideline_verdicts ENABLE ROW LEVEL SECURITY;

--
-- Name: guideline_verdicts guideline_verdicts_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY guideline_verdicts_read ON public.guideline_verdicts FOR SELECT TO authenticated, anon USING (true);


--
-- Name: item_region_rules; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.item_region_rules ENABLE ROW LEVEL SECURITY;

--
-- Name: item_region_rules item_region_rules_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY item_region_rules_read ON public.item_region_rules FOR SELECT TO authenticated, anon USING (true);


--
-- Name: items; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.items ENABLE ROW LEVEL SECURITY;

--
-- Name: items items_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY items_read ON public.items FOR SELECT TO authenticated, anon USING (true);


--
-- Name: page_views; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.page_views ENABLE ROW LEVEL SECURITY;

--
-- Name: regions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.regions ENABLE ROW LEVEL SECURITY;

--
-- Name: regions regions_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY regions_read ON public.regions FOR SELECT TO authenticated, anon USING (true);


--
-- Name: search_queries; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.search_queries ENABLE ROW LEVEL SECURITY;

--
-- Name: search_term_decisions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.search_term_decisions ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict WXAUoa6HzF2kURAMB1dPlCvFn0sxtijYq740EHkwcuuIFsiLb5FpgiJNBnfGka9

