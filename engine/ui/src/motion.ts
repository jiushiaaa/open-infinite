import { useEffect, useState } from "react";

// 强反馈动效开关：写入 <html data-motion>，CSS 据此降级。
// "auto"：跟随 prefers-reduced-motion；"full"：强制开；"reduced"：强制关。
export type MotionPref = "auto" | "full" | "reduced";

const KEY = "lne.motion";

export function readMotionPref(): MotionPref {
  const v = localStorage.getItem(KEY);
  return v === "full" || v === "reduced" ? v : "auto";
}

function apply(pref: MotionPref): void {
  const root = document.documentElement;
  if (pref === "auto") root.removeAttribute("data-motion");
  else root.setAttribute("data-motion", pref);
}

export function useMotionPref(): [MotionPref, (p: MotionPref) => void] {
  const [pref, setPref] = useState<MotionPref>(readMotionPref);
  useEffect(() => {
    apply(pref);
    localStorage.setItem(KEY, pref);
  }, [pref]);
  return [pref, setPref];
}
