import type { ItemRow } from './items';

/**
 * 품목 검색 키. 화면(index.astro)이 data-key 한 줄로 읽어 부분일치만 한다.
 *
 * 한 품목을 여러 이름으로 찾는다. '쇼파'로 쳐도 소파가, 'ㅅㅍ'로 쳐도 소파가,
 * 'sopa'로 쳐도 소파가 나와야 한다. 중복 페이지를 별칭으로 흡수했기 때문에
 * (쇼파 -> 소파, 장농 -> 장롱) 검색이 그 부담을 대신 진다.
 *
 * 키는 두 덩어리를 공백으로 이어 붙인 문자열이다.
 *   1. 표기 — 이름, 별칭, 판정, 분류, slug (공백 제거본도 함께)
 *   2. 초성 — 이름과 별칭의 초성열
 *
 * slug가 곧 로마자 표기라(sopa, bojobaeteori) 영문 입력은 1번이 받는다.
 */

const CHO = [
  'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
  'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
];

const HANGUL_BASE = 0xac00;
const HANGUL_LAST = 0xd7a3;
const CHO_SPAN = 588;  // 초성 하나가 차지하는 음절 수 (중성 21 * 종성 28)

/** '소파' -> 'ㅅㅍ'. 한글이 아닌 글자는 그대로 남긴다. */
export function chosung(text: string): string {
  let out = '';
  for (const ch of text) {
    const code = ch.charCodeAt(0);
    if (code >= HANGUL_BASE && code <= HANGUL_LAST) {
      out += CHO[Math.floor((code - HANGUL_BASE) / CHO_SPAN)];
    } else if (ch !== ' ') {
      out += ch;
    }
  }
  return out;
}

/** 검색어 정규화. 공백과 대소문자를 없앤다. */
export function normalize(term: string): string {
  return term.replace(/\s+/g, '').toLowerCase();
}

/**
 * 품목 하나의 검색 키.
 *
 * 공백을 지운 형태를 함께 넣는 이유: 질의도 공백을 지워서 들어오므로
 * '보조 배터리'로 쳐도 '보조배터리'에 걸려야 한다.
 */
export function searchKey(row: ItemRow): string {
  const aliases = row.aliases ?? [];
  const words = [row.name, ...aliases, row.verdict, row.category ?? '', row.slug];
  const plain = words.filter(Boolean).join(' ');
  const packed = words.map(normalize).join(' ');
  const cho = [row.name, ...aliases].map(chosung).join(' ');
  return `${plain} ${packed} ${cho}`.toLowerCase();
}

const JUNG = [
  'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ',
  'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ',
];

const JONG = [
  '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ',
  'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ',
  'ㅌ', 'ㅍ', 'ㅎ',
];

const JUNG_SPAN = 28;  // 중성 하나가 차지하는 음절 수 (종성 28)

/**
 * '공기청덩' -> 'ㄱㅗㅇㄱㅣㅊㅓㅇㄷㅓㅇ'. 오타를 재려고 음절을 자모로 푼다.
 *
 * 음절째로 재면 '정'과 '덩'이 그냥 다른 글자라 거리가 1이고, '정'과 '청'도
 * 거리가 1이다. 초성 하나만 어긋난 오타와 아예 다른 품목이 같은 값이 된다.
 * 자모로 풀면 앞은 11자 중 1자, 뒤도 11자 중 1자지만 길이가 길어져
 * 임계값을 글자수에 비례해 줄 수 있다.
 */
export function jamo(text: string): string {
  let out = '';
  for (const ch of text) {
    const code = ch.charCodeAt(0);
    if (code >= HANGUL_BASE && code <= HANGUL_LAST) {
      const at = code - HANGUL_BASE;
      out += CHO[Math.floor(at / CHO_SPAN)];
      out += JUNG[Math.floor((at % CHO_SPAN) / JUNG_SPAN)];
      out += JONG[at % JUNG_SPAN];
    } else if (ch !== ' ') {
      out += ch;
    }
  }
  return out;
}

/**
 * 오타 검색용 키. 이름과 별칭만 자모로 풀어 공백으로 잇는다.
 *
 * searchKey와 달리 판정, 분류, 초성열을 빼는 이유: 오타 비교는 토막마다
 * 편집거리를 재는데, '전용수거함' 같은 공용 낱말이 섞여 있으면 아무 오타나
 * 그 낱말에 걸려 전 품목이 다 뜬다.
 */
export function fuzzyKey(row: ItemRow): string {
  const aliases = row.aliases ?? [];
  return [row.name, ...aliases].map((w) => jamo(normalize(w))).join(' ');
}
