// 28개 점포 영상 일괄 렌더링
// 사용: node render-all.mjs            (전체)
//       node render-all.mjs 001 013    (특정 점포만)
import { execSync } from "node:child_process";
import { readFileSync, mkdirSync } from "node:fs";

const ts = readFileSync(new URL("./src/data.ts", import.meta.url), "utf-8");
const ids = [...ts.matchAll(/"id":\s*"(\d{3})"/g)].map((m) => m[1]);
const names = Object.fromEntries(
  [...ts.matchAll(/"id":\s*"(\d{3})",\s*\n\s*"name":\s*"([^"]+)"/g)].map((m) => [m[1], m[2]]),
);

const want = process.argv.slice(2);
const targets = want.length ? ids.filter((id) => want.includes(id)) : ids;

mkdirSync(new URL("./out", import.meta.url), { recursive: true });
console.log(`렌더 대상: ${targets.length}개 점포\n`);

let done = 0;
for (const id of targets) {
  const name = names[id] ?? id;
  const out = `out/${id}_${name}.mp4`;
  console.log(`▶ [${++done}/${targets.length}] Store-${id} (${name}) 렌더 중…`);
  execSync(`npx remotion render Store-${id} "${out}" --concurrency=1 --log=error`, { stdio: "inherit" });
}
console.log(`\n✅ 완료: ${targets.length}개 영상 → out/`);
