-- 판정에 '무상수거' 추가.
-- 폐가전은 종량제도 대형폐기물 스티커도 아닌 별도 경로(E-순환거버넌스 무상방문수거)를 탄다.
-- 게이트 1에서 '폐가전무료수거' 51,830으로 확인된 수요이기도 하다 (docs/09).
alter table items drop constraint if exists items_verdict_check;
alter table items add constraint items_verdict_check
  check (verdict in ('재활용','일반쓰레기','대형폐기물','전용수거함','무상수거','조건부'));
