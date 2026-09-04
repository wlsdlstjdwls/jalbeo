/**
 * 브라우저에서 쓰는 Supabase 공개 설정 (주소 + anon 키).
 *
 * anon 키는 설계상 공개용이다. 정적 사이트에 박혀 나가는 값이고 접근 제어는
 * RLS와 SECURITY DEFINER 함수가 한다 (`.env.public` 주석 참고).
 *
 * 값은 빌드 때 한 번만 읽는다. `npm run build`는 prebuild에만 env 파일을 넘기고
 * astro 자신에게는 안 넘기므로 process.env가 비어 있다. 그때는 커밋된
 * `.env.public`을 직접 읽는다. 번들 위치가 바뀌어도 안전하도록 경로는
 * import.meta.url이 아니라 실행 디렉터리 기준으로 잡는다.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

// astro는 site/ 에서 돌지만, 저장소 루트에서 부르는 경우도 받아 둔다.
const CANDIDATES = ['.env.public', join('site', '.env.public')];

function fromEnvPublic(key: string): string {
  for (const rel of CANDIDATES) {
    let text: string;
    try {
      text = readFileSync(join(process.cwd(), rel), 'utf8');
    } catch {
      continue; // 파일이 없으면 다음 후보
    }
    for (const line of text.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
      const [name, ...rest] = trimmed.split('=');
      if (name.trim() === key) return rest.join('=').trim();
    }
  }
  return ''; // 못 찾으면 빈 값 -> 호출부가 안내 문구를 띄운다
}

function read(key: string): string {
  return process.env[key] || fromEnvPublic(key);
}

export const SUPABASE_URL = read('SUPABASE_URL');
export const SUPABASE_ANON_KEY = read('SUPABASE_ANON_KEY');
