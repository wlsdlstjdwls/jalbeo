-- 훈령 충돌 감사 2차: 폐가전 무상수거 조건 정정.
-- 근거: 별표1 대형 전기전자제품 해당품목 예시가 PDF 페이지 넘김에서 12개
-- 잘려 있었다(러닝머신부터 데스크탑PC세트까지). 파서를 고쳐 복원하고,
-- E-순환거버넌스 단일수거/다량배출 목록과 대조해 verdict_line을 맞춘다.
-- 상세는 docs/25.

update items set
  verdict_line = '훈령과 무상수거 단일수거 목록에 이름이 있습니다. 1대부터 무료입니다.',
  updated_at = now()
where slug = 'jeonjareinji';

update items set
  verdict_line = '단일수거 품목이라 한 대만 있어도 무료로 가져갑니다.',
  updated_at = now()
where slug = 'jeseupgi';

update items set
  verdict_line = '다량배출 품목입니다. 형태와 상관없이 5개를 모아야 합니다.',
  updated_at = now()
where slug = 'cheongsogi';

update items set
  verdict = '무상수거',
  verdict_line = '운동기구 중 유일한 예외입니다. 한 대만 있어도 무료 수거됩니다.',
  updated_at = now()
where slug = 'reoningmeosin';

-- 은박지: 훈령은 종량제봉투를 "지정"한 게 아니라 금속캔 재활용에서 빼고
-- 처리를 조례로 넘겼다("종량제봉투 등 지자체 조례에 따라 제출").
update items set
  verdict_line = '알루미늄인데 캔이 아닙니다. 훈령이 금속캔에서 빼고 조례로 넘겼습니다.',
  updated_at = now()
where slug = 'eunbakji';
