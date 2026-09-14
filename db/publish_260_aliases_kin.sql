-- 지식iN 씨앗 1차(`docs/49`)에서 나온 표기 차이. 답이 같은데 우리가 그
-- 표기를 안 받고 있었다. 같은 물건의 다른 표기는 페이지가 아니라 별칭이다
-- (판단 8). 홍합껍질은 조개껍질 페이지에 '홍합껍데기'만 있어서 '껍질'로
-- 적은 사람을 못 받았고, 귤껍데기, 우유곽, 계란곽, 약봉투도 같다.

update items set aliases = array['굴껍질','소라껍질','홍합껍데기','게껍데기','게 껍데기','꽃게 껍데기','새우껍질','갑각류 껍데기','랍스터 껍데기','홍합껍질','꽃게껍질','조개껍데기'], updated_at = now() where slug = 'jogaekkeopjil';  -- 조개껍질
update items set aliases = array['귤 껍질','감귤껍질','말린 귤껍질','한라봉 껍질','오렌지 껍질','귤 상자','귤껍데기','귤 껍데기'], updated_at = now() where slug = 'gyulkkeopjil';  -- 귤껍질
update items set aliases = array['두유팩','종이팩','주스팩','살균팩','우유곽','우유 곽'], updated_at = now() where slug = 'uyupaek';  -- 우유팩
update items set aliases = array['영양제','폐의약품','조제약','알약','약봉지','인공눈물','안약','점안액','물약','약봉투'], updated_at = now() where slug = 'yak';  -- 약
update items set aliases = array['일회용전자담배','궐련형전자담배','액상전자담배','전담기기','전자담배액상','전자담배카트리지','전담','일회용 전담','버블몬','뷰즈고'], updated_at = now() where slug = 'jeonjadambae';  -- 전자담배
update items set aliases = array['달걀판','계란포장','에그트레이','계란트레이','계란곽','계란 곽'], updated_at = now() where slug = 'gyeranpan';  -- 계란판
