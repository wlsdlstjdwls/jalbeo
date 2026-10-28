# 65. 휴면 전환

2026-10-28.

## 왜 재우나

`jalbeo.com`을 사용자의 모바일 청첩장 주소로 쓴다. 화면은 별도 프로젝트로 띄우고
도메인만 옮긴다. Supabase 무료 플랜이 활성 프로젝트 2개까지라 이 프로젝트의 칸도
비워야 한다.

결정 시점의 숫자(`scripts/inflow_report.py`, 판단 99):

- 품목/가이드 검색 착지 38건. 9/19~9/29에 몰렸고(9/22 하루 8건) 9/30 이후
  한 달 동안 1건(10/27)
- 사이트 내 검색 45건. 10/24 '양은솥', 10/27 '주물'이 마지막 못 찾은 검색이다

지우지 않고 재운다. 코드, 본문, 수수료 데이터는 저장소에 다 있고, DB는 아래
덤프로 되살린다.

## 한 것

### 1. DB 덤프

`db/backup/2026-10-28/`. postgres:17 컨테이너의 `pg_dump`로 세션 풀러에 붙어
`public` 스키마만 떴다. 행 수는 덤프 직전 `count(*)`와 INSERT 수가 전부 같다.

| 파일 | 내용 | 행 | 커밋 |
|---|---|---|---|
| `schema.sql` | 테이블, 뷰(`page_views_human`), 함수 13개, RLS | - | 함 |
| `data_content.sql` | `items` 279, `guideline_verdicts` 88 (`item_region_rules`, `regions`, `bulky_fees`는 0행) | 367 | 함 |
| `private/data_logs.sql` | `page_views` 1,435, `search_queries` 65, `search_term_decisions` 5, `admins` 1 | 1,506 | **안 함** |

저장소가 public이라 방문 기록, 검색어, 관리자 이메일은 `.gitignore`
(`db/backup/*/private/`)로 뺐다. 이 파일은 이 PC에만 있다. 따로 한 벌 보관해야 한다.

`auth` 스키마는 안 떴다. `admins`는 이메일로 대조하므로(`auth.jwt() ->> 'email'`)
되살릴 때 같은 이메일로 Supabase Auth 계정만 새로 만들면 된다.

### 2. GitHub Actions 끄기

`gh workflow disable`로 둘 다 껐다. 파일은 그대로다.

| 워크플로 | 상태 |
|---|---|
| 데이터 최신성 체크 | `disabled_manually` |
| IndexNow 제출 | `disabled_manually` |

IndexNow를 켜 둔 채 도메인을 옮기면 청첩장 도메인으로 잘버려 URL을 계속 제출한다.
최신성 이슈 #7(2026-10-12 감지)은 열린 채로 둔다. 되살릴 때 그 diff부터 본다.

### 3. vercel.app 리다이렉트 (사용자 몫)

코드에는 없다. `site/vercel.json`의 `redirects`는 개명 slug와 `/sitemap.xml`뿐이고,
`jalbeo.vercel.app -> jalbeo.com` 301은 `docs/30`에서 Vercel 대시보드 도메인 설정으로
걸었다. 도메인 설정이라 사용자가 Settings > Domains에서 지운다. 안 지우면 미리보기
주소로 온 사람이 청첩장으로 넘어간다.

리다이렉트를 지운 뒤 `jalbeo.vercel.app`은 `isProductionHost`가 거짓이라 `noindex`,
robots 차단, RSS 404로 뜬다. 휴면 상태에서는 그게 맞다.

## 휴면 중 주의

- `site/.env.public`이 `SUPABASE_URL`을 커밋으로 들고 있어서 `pull-data.mjs`는
  자격증명이 "있다"고 보고 DB를 읽는다. **Supabase를 정지한 뒤 재배포하면 빌드가
  실패한다.** 휴면 중 배포가 필요하면 두 값을 비우고 돌린다. 그러면 커밋된
  `site/src/data/*.json`으로 빌드한다
- 정지 뒤에도 이미 떠 있는 페이지는 멀쩡하다. 방문 기록 전송은 `.catch`로 삼켜서
  화면에 오류가 안 난다. `/admin/`과 검색어 적재만 멈춘다

## 되살리는 절차

1. 새 Supabase 프로젝트(또는 정지한 것을 복원)에 `schema.sql`, `data_content.sql`,
   `private/data_logs.sql` 순서로 넣는다
2. `site/.env`(DB 접속), `site/.env.public`(URL, anon key), Vercel 환경변수를 새
   값으로 바꾼다. `SITE_URL`은 넣지 않는다(판단 29)
3. 같은 이메일로 Auth 계정을 만들고 `python scripts/admin_admins.py`로 명단을 확인한다
4. 도메인을 새로 붙이면 `site/src/lib/site.ts`와 `astro.config.mjs` 기본값을 그
   도메인으로 바꾸고, vercel.app 301과 서치어드바이저, 서치콘솔 등록을 다시 한다
   (`docs/30`)
5. `gh workflow enable "데이터 최신성 체크"`, `gh workflow enable "IndexNow 제출"`
6. `vercel deploy --prod` 뒤 `gh workflow run "IndexNow 제출"` (자동배포 꺼져 있음)
