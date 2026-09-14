-- 실측 21차 하위 구간 처분 (`docs/54`).
--
-- 66주제 중 100 미만 56개. 판단 69번대로 상태 씨앗의 하위 구간은 발행이
-- 아니라 별칭이다 - 사람이 상태로 물은 말은 대개 이미 가진 페이지의 다른
-- 표기다. 30개가 두 어미 합계 20(조회 하한)이라 순위도 못 매긴다.
--
-- 붙일 본체가 없는 것은 붙이지 않는다. 숯(70), 망원경(25), 족욕기(20),
-- 거치대(20), 파쇄기(20), 배수망(20), 글러브(25), 얼음컵(20),
-- 우레탄폼(65)은 축 자체가 우리에게 없어서 별칭으로 접으면 엉뚱한
-- 페이지가 그 검색을 받는다. 보류로 둔다.
--
-- 붙인 뒤 반드시 build_fee_stats.py 전후 diff를 뜬다 (판단 70).

-- 가전
update items set aliases = array_cat(aliases, '{"온풍기","히터","전기히터"}')
 where slug = 'jeongijangpan';
update items set aliases = array_cat(aliases, '{"찜질팩","충전식 찜질팩","온열팩"}')
 where slug = 'jeongijangpan';
update items set aliases = array_cat(aliases, '{"태블릿","아이패드","갤럭시탭","고장난 태블릿"}')
 where slug = 'noteubuk';
update items set aliases = array_cat(aliases, '{"메인보드","그래픽카드","램","CPU","파워서플라이"}')
 where slug = 'keompyuteo';
update items set aliases = array_cat(aliases, '{"스마트키","차키","자동차 키"}')
 where slug = 'doeorak';

-- 생활화학. 액체 축은 새로 낸 샴푸 페이지가 받는다
update items set aliases = array_cat(aliases, '{"클렌징크림","제모크림","데오드란트","오래된 화장품"}')
 where slug = 'hwajangpum';
update items set aliases = array_cat(aliases, '{"소독액","알코올","에탄올","소독용 에탄올"}')
 where slug = 'sonsodokje';
update items set aliases = array_cat(aliases, '{"과탄산소다","베이킹소다","구연산","가루세제","워셔액"}')
 where slug = 'seje';
update items set aliases = array_cat(aliases, '{"페브리즈","섬유탈취제","탈취제"}')
 where slug = 'seupgijegeoje';

-- 일반
update items set aliases = array_cat(aliases, '{"연탄재","연탄","재"}')
 where slug = 'tail';
update items set aliases = array_cat(aliases, '{"물감","포스터물감","아크릴물감","물풀","목공풀"}')
 where slug = 'peinteu';
update items set aliases = array_cat(aliases, '{"잉크","만년필 잉크","프린터 잉크"}')
 where slug = 'ingkeukateuriji';
update items set aliases = array_cat(aliases, '{"그릴","미니그릴","전기그릴 판"}')
 where slug = 'huraipaen';
update items set aliases = array_cat(aliases, '{"헤어밴드","고무줄","머리끈"}')
 where slug = 'gomu';
update items set aliases = array_cat(aliases, '{"머리핀","실핀","집게핀"}')
 where slug = 'gocheol';
update items set aliases = array_cat(aliases, '{"대변","사람 대변","인분"}')
 where slug = 'gangajittong';
update items set aliases = array_cat(aliases, '{"행운목","죽은 화초","시든 화초","화초"}')
 where slug = 'hwabun';
update items set aliases = array_cat(aliases, '{"장작","땔감","나무토막"}')
 where slug = 'pyemokjae';

-- 음식물
update items set aliases = array_cat(aliases, '{"생선","통생선","말린 생선","멸치뼈","멸치"}')
 where slug = 'saengseonppyeo';
update items set aliases = array_cat(aliases, '{"닭발","닭껍질","닭연골"}')
 where slug = 'chikinppyeo';
update items set aliases = array_cat(aliases, '{"킹크랩","꽃게 껍질","게딱지","새우껍질"}')
 where slug = 'jogaekkeopjil';
update items set aliases = array_cat(aliases, '{"차잎","녹차잎","티백 속","우린 찻잎"}')
 where slug = 'keopijjikkeogi';
update items set aliases = array_cat(aliases, '{"은행","은행알","은행 껍질"}')
 where slug = 'boksungassi';
update items set aliases = array_cat(aliases, '{"매실","매실씨","담고 난 매실"}')
 where slug = 'ganjang';
update items set aliases = array_cat(aliases, '{"깻잎","상추","시든 채소","토마토","썩은 토마토","비트"}')
 where slug = 'gamjakkeopjil';
update items set aliases = array_cat(aliases, '{"콩껍질","완두콩 껍질","콩깍지"}')
 where slug = 'gyerankkeopjil';
update items set aliases = array_cat(aliases, '{"국수","소면","마른 면","안 삶은 국수"}')
 where slug = 'milgaru';

-- 종이
update items set aliases = array_cat(aliases, '{"처방전","상품권","다 쓴 상품권","진료 영수증"}')
 where slug = 'tongjang';
update items set aliases = array_cat(aliases, '{"공책","노트","스프링 노트","다이어리"}')
 where slug = 'chaek';

-- 재활용
update items set aliases = array_cat(aliases, '{"빈병","소주병","맥주병","양주병","위스키병"}')
 where slug = 'yuribyeong';
update items set aliases = array_cat(aliases, '{"요거트통","요구르트병","떠먹는 요거트 용기"}')
 where slug = 'banchantong';
