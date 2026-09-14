-- 실측 19차(`docs/49`) 200 미만 52주제 판정. 26차 자리인데 **발행이 없다.**
-- 지식iN 씨앗은 사람이 상태로 묻는 목록이라(판단 67) 하위 구간이 통째로
-- 기존 페이지의 다른 표기다. 200 이상 10주제에서는 발행 3, 개명 1이 나왔다.
--
-- 별칭을 붙인 뒤 `build_fee_stats.py`를 돌려 본체 중앙값이 움직이는지 본다
-- (판단 42, 44, 47). 움직이면 같은 물건이 아니다.

update items set aliases = array['사과껍질','과일 껍질','배껍질','감껍질','멜론껍질','파인애플껍질','키위껍질','키위 껍질','포도껍질','복숭아껍질','사과심지','사과심','사과 심','과일심','배심','파인애플 심지'], updated_at = now() where slug = 'gwailkkeopjil';  -- 과일껍질
update items set aliases = array['화장품 공병','남은 화장품','선크림','썬크림','화장품 용기','클렌징오일','클렌징 오일','바디오일','마사지오일','페이스오일','립밤','클렌징폼'], updated_at = now() where slug = 'hwajangpum';  -- 화장품
update items set aliases = array['생선가시','생선내장','생선 대가리','생선대가리','생선머리','통고등어','굴비 대가리','생선비늘','동태뼈'], updated_at = now() where slug = 'saengseonppyeo';  -- 생선뼈
update items set aliases = array['바나나 껍질','바나나','상한 바나나'], updated_at = now() where slug = 'bananakkeopjil';  -- 바나나껍질
update items set aliases = array['닭뼈','돼지뼈','돼지 뼈','감자탕뼈','등뼈','족발뼈','갈비뼈','소뼈','사골뼈','닭발뼈','뼈다귀','치킨','남은 치킨','닭고기','닭껍질'], updated_at = now() where slug = 'chikinppyeo';  -- 치킨뼈
update items set aliases = array['주방칼','부엌칼','과도','중식도','칼','채칼','감자칼','강판','슬라이서','바늘','재봉바늘','옷핀','압정','손톱깎이','손톱깍이'], updated_at = now() where slug = 'sikkal';  -- 식칼
update items set aliases = array['컵라면 용기','라면국물','생라면','라면사리','봉지라면'], updated_at = now() where slug = 'keopramyeon';  -- 컵라면
update items set aliases = array['귤 껍질','감귤껍질','말린 귤껍질','한라봉 껍질','오렌지 껍질','귤 상자','귤껍데기','귤 껍데기','자몽껍질','자몽 껍질'], updated_at = now() where slug = 'gyulkkeopjil';  -- 귤껍질
update items set aliases = array['고철류','쇠','철','스테인리스','스텐','알루미늄','비철금속','금속','쇠붙이','휴대용 가스버너','가스버너','부루스타','버너','삼각대','카메라 삼각대'], updated_at = now() where slug = 'gocheol';  -- 고철
update items set aliases = array['복숭아 씨','과일씨','망고씨','아보카도씨','살구씨','자두씨','감씨','체리씨','대추씨','씨앗','아보카도','아보카도 씨','아보카도 과육','수박씨','단호박씨','해바라기씨','포도씨','호박씨'], updated_at = now() where slug = 'boksungassi';  -- 복숭아씨
update items set aliases = array['감자 껍질','고구마껍질','고구마 껍질','채소껍질','채소 껍질','당근껍질','무껍질','싹난 감자','썩은 감자','썩은 고구마','대파','대파 뿌리','파뿌리','쪽파','쪽파 뿌리','토마토꼭지','토마토 꼭지','방울토마토 꼭지','딸기꼭지','딸기 꼭지','고추꼭지','마늘','상추','멕시코감자','얌빈','오이껍질'], updated_at = now() where slug = 'gamjakkeopjil';  -- 감자껍질
update items set aliases = array['페트병 뚜껑','페트병 고리','라벨','페트병 라벨','라벨스티커','비닐 라벨','수분리성 라벨','병뚜껑','소주뚜껑'], updated_at = now() where slug = 'peteubyeong';  -- 페트병
update items set aliases = array['강화유리','깨진유리','깨진 유리병','식탁유리','판유리','깨진 유리컵','스노우볼'], updated_at = now() where slug = 'yuri';  -- 유리
update items set aliases = array['큰 인형','애착인형','대형인형','봉제인형','솜인형','마네킹'], updated_at = now() where slug = 'inhyeong';  -- 인형
update items set aliases = array['화장지심','키친타올심','키친타올','키친타월','휴지 심','두루마리 휴지심','휴지','화장지','두루마리 휴지'], updated_at = now() where slug = 'hyujisim';  -- 휴지심
update items set aliases = array['생 크림','휘핑크림','상한 우유','남은 우유','요구르트','유제품','크림치즈','상한 두유','케이크','남은 케이크'], updated_at = now() where slug = 'saengkeurim';  -- 생크림
update items set aliases = array['인화사진','사진액자','인생네컷','네컷사진','즉석사진'], updated_at = now() where slug = 'sajin';  -- 사진
update items set aliases = array['장우산','고장난 우산','양산','부채'], updated_at = now() where slug = 'usan';  -- 우산
update items set aliases = array['유아욕조','아기 욕조','신생아욕조','욕조','좌욕기','세수대야'], updated_at = now() where slug = 'agiyokjo';  -- 아기욕조
update items set aliases = array['헌책','중고책','도서','단행본','양장본','만화책','동화책','전공서적','참고서','문제집','다이어리','수첩','플래너'], updated_at = now() where slug = 'chaek';  -- 책
update items set aliases = array['신문','잡지','노트','스프링노트','상장','교과서','명함','쇼핑백','종이 쇼핑백','종이가방','종이봉투','스티커','이형지','마스킹테이프','마스킹 테이프','종이테이프','택배 송장','송장 스티커','아트지 스티커','포스트잇'], updated_at = now() where slug = 'jongi';  -- 종이
update items set aliases = array['인슐린주사기','주사바늘','펜니들','자가주사','위고비주사기','란셋','임신테스트기','임테기'], updated_at = now() where slug = 'jusagi';  -- 주사기
update items set aliases = array['펜','샤프','샤프펜슬','형광펜','사인펜','볼펜심','보드마카','화이트보드마카','유성매직'], updated_at = now() where slug = 'bolpen';  -- 볼펜
update items set aliases = array['고무장갑','고무패킹','고무호스','고무줄','라텍스장갑','니트릴장갑','차량매트','자동차매트','자동차 매트','차량 매트','카매트','풍선'], updated_at = now() where slug = 'gomu';  -- 고무
update items set aliases = array['고춧가루','고추가루','설탕','부침가루','튀김가루','미숫가루','카레가루','후추','분유가루','밀가루 반죽','반죽','녹차가루','호떡','만두','냉동만두'], updated_at = now() where slug = 'milgaru';  -- 밀가루
update items set aliases = array['옥수수심','옥수수 껍질','죽순'], updated_at = now() where slug = 'oksusudae';  -- 옥수수대
update items set aliases = array['헌 옷','한복','가죽옷','가죽자켓','가죽재킷'], updated_at = now() where slug = 'heonot';  -- 헌옷
update items set aliases = array['선글라스','안경테','돋보기','확대경'], updated_at = now() where slug = 'angyeong';  -- 안경
update items set aliases = array['도자기 그릇','사기그릇','사기 그릇','백자','청자','도자기 접시','도자기 인형','도자기 장식품','깨진 도자기','도자기 컵','사기 컵','질그릇','옹기그릇','도기','저금통','돼지저금통'], updated_at = now() where slug = 'dojagi';  -- 도자기
update items set aliases = array['석고깁스','캐스트','깁스붕대','압박붕대','붕대'], updated_at = now() where slug = 'gibseu';  -- 깁스
update items set aliases = array['아이 장난감','플라스틱 장난감','완구','나무장난감','블록','레고','레고블럭','조립블록','피규어','클레이','아이클레이','슬라임','점토','찰흙','액체괴물'], updated_at = now() where slug = 'jangnangam';  -- 장난감
update items set aliases = array['햇반용기','햇반그릇','즉석밥그릇','컵밥용기','오뚜기밥용기','컵밥'], updated_at = now() where slug = 'jeukseokbapyonggi';  -- 즉석밥 용기
