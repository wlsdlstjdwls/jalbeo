# 잘버려 (jalbeo)

쓰레기 배출 안내 사이트. 프로그래매틱 SEO 기반.

**현재 상태: 게이트 1 통과 (2026-09-03) / 파일럿 구축 전**

## 빠른 요약

- 품목별 "이거 어디에 버려요?" 정보 사이트
- 원안의 "품목 × 지자체 3,000페이지"는 조사 결과 **폐기** — 해당 검색어가 실재하지 않음
- 품목 페이지 500~800개에 집중, 지역은 페이지 내부 컴포넌트로 처리
- 기술 스택: Astro SSG + 정적 호스팅 (원안의 Spring Boot + EC2에서 변경)

## 문서

읽는 순서: `docs/01` → `02` → `03`·`04`·`05` → `06`

| 파일 | 내용 |
|---|---|
| [docs/01-original-plan.md](docs/01-original-plan.md) | 최초 기획안 (원문 보존) |
| [docs/02-review.md](docs/02-review.md) | 비판적 검토 — 리스크 5개, 스택 재검토 |
| [docs/03-research-datasource.md](docs/03-research-datasource.md) | 공공데이터 조사 (78건, 서울 3개구뿐) |
| [docs/04-research-demand.md](docs/04-research-demand.md) | 검색 수요 조사 — B층 가설 반증 |
| [docs/05-naming-domain.md](docs/05-naming-domain.md) | 프로젝트명 + 도메인 가용성 |
| [docs/06-action-plan.md](docs/06-action-plan.md) | 실행 계획 · 체크리스트 |
| [docs/07-keyword-seed.md](docs/07-keyword-seed.md) | 품목 시드 325개 수집 결과 · 수식어 분포 |
| [docs/08-guideline-data.md](docs/08-guideline-data.md) | 환경부 분리배출 근거 데이터 · 커버리지 18% |
| [docs/09-gate1-result.md](docs/09-gate1-result.md) | **게이트 1 실측 결과 — 통과 (219,310)** |
| [data/raw/](data/raw/) | 조사 원본 데이터 |

## 다음 작업

`docs/06-action-plan.md`의 6·7번 — Astro 뼈대 구축 후 **파일럿 20페이지** 배포,
Search Console 색인 확인(**게이트 2**). 색인 실패 시 확장 금지.
