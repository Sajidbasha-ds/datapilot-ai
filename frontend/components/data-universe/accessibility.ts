import { useEffect, useState } from "react";
import { PerformanceMode } from "./types";

export function useReducedMotion(): boolean {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updatePreference = () => setReducedMotion(mediaQuery.matches);
    updatePreference();
    mediaQuery.addEventListener("change", updatePreference);
    return () => mediaQuery.removeEventListener("change", updatePreference);
  }, []);

  return reducedMotion;
}

export function getEffectivePerformanceMode(
  requestedMode: PerformanceMode,
  reducedMotion: boolean,
): PerformanceMode {
  if (requestedMode === "off") return "off";
  if (reducedMotion) return "reduced";
  return requestedMode;
}
