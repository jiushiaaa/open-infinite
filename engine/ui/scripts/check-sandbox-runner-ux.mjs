import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const pagePath = resolve("src/components/WorldSandboxPage.tsx");
const cssPath = resolve("src/components/worldSandbox.css");
const page = readFileSync(pagePath, "utf8");
const css = readFileSync(cssPath, "utf8");

const failures = [];

const requiredPageMarkers = [
  ['className="sandbox-panel sandbox-runner"', "runner panel should have a dedicated product shell"],
  ["sandbox-runner__steps", "runner should explain event, optional intervention, and launch steps"],
  ["sandbox-runner__advanced", "optional intervention controls should be grouped separately"],
  ["启动一轮推演", "primary action should describe the product outcome"],
];

for (const [marker, message] of requiredPageMarkers) {
  if (!page.includes(marker)) {
    failures.push(message);
  }
}

const requiredCssMarkers = [
  [".sandbox-runner__head", "runner header styling is missing"],
  [".sandbox-runner__steps", "runner step track styling is missing"],
  [".sandbox-runner__advanced summary", "optional intervention summary styling is missing"],
  [".sandbox-runner__submit", "runner primary action styling is missing"],
];

for (const [marker, message] of requiredCssMarkers) {
  if (!css.includes(marker)) {
    failures.push(message);
  }
}

if (failures.length > 0) {
  console.error("Sandbox runner UX check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("sandbox runner ux structure ok");
