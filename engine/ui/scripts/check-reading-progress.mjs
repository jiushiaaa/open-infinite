import assert from "node:assert/strict";
import {
  READING_PROGRESS_STORAGE_KEY,
  describeReadingRoute,
  isReadableRoute,
  readRecentReading,
  writeRecentReading,
} from "../.tmp-reading-progress/readingProgress.js";

function storage() {
  const data = new Map();
  return {
    getItem(key) {
      return data.has(key) ? data.get(key) : null;
    },
    setItem(key, value) {
      data.set(key, value);
    },
    removeItem(key) {
      data.delete(key);
    },
  };
}

const dossier = {
  name: "dossierReading",
  slug: "my-story",
  worldlineId: "main",
  tab: "character_volume",
};
const longline = {
  name: "longlineReading",
  slug: "my-story",
  worldlineId: "main",
};
const character = {
  name: "characterVolume",
  slug: "my-story",
  worldlineId: "main",
  characterId: "zhao_xuan",
};
const anchor = { name: "anchor", slug: "my-story" };

assert.equal(isReadableRoute(dossier), true);
assert.equal(isReadableRoute(longline), true);
assert.equal(isReadableRoute(character), true);
assert.equal(isReadableRoute(anchor), false);

assert.deepEqual(describeReadingRoute(dossier), {
  slug: "my-story",
  label: "角色个人卷",
  title: "继续读角色个人卷",
  action: "回到角色个人卷",
  worldlineId: "main",
  hash: "#/world/my-story/worldlines/main/reading/character_volume",
});
assert.equal(describeReadingRoute(longline).title, "继续读长线卷");
assert.equal(describeReadingRoute(character).label, "角色卷 · zhao_xuan");

const fakeStorage = storage();
assert.equal(readRecentReading(fakeStorage, "my-story"), null);
writeRecentReading(fakeStorage, dossier, 1700000000000);
assert.equal(
  JSON.parse(fakeStorage.getItem(READING_PROGRESS_STORAGE_KEY))["my-story"].hash,
  "#/world/my-story/worldlines/main/reading/character_volume",
);
assert.equal(readRecentReading(fakeStorage, "my-story").title, "继续读角色个人卷");

writeRecentReading(fakeStorage, anchor, 1700000001000);
assert.equal(readRecentReading(fakeStorage, "my-story").title, "继续读角色个人卷");

fakeStorage.setItem(READING_PROGRESS_STORAGE_KEY, "{broken");
assert.equal(readRecentReading(fakeStorage, "my-story"), null);

console.log("reading progress helper ok");
