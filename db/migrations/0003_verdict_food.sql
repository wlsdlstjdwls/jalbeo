-- 판정에 '음식물' 추가.
-- 수박껍질·바나나껍질은 음식물쓰레기인데 기존 6개 판정으로는 표현할 축이 없었다.
-- 일반쓰레기로 두면 틀린 안내가 되고, 조건부로 두면 답을 회피하는 셈이다.
-- 게이트 1에서 음식물 축 수요는 8,970으로 작지만(docs/09) 답이 틀리면 안 되는 영역이다.
alter table items drop constraint if exists items_verdict_check;
alter table items add constraint items_verdict_check
  check (verdict in ('재활용','일반쓰레기','대형폐기물','전용수거함','무상수거','음식물','조건부'));
