import { useEffect } from "react";
import { useAppStore } from "../store/appStore";

export function useTheme() {
  const { isDark, toggleTheme } = useAppStore();

  useEffect(() => {
    // Dark = no class, Light = "light" class on <html>
    document.documentElement.classList.toggle("light", !isDark);
  }, [isDark]);

  return { isDark, toggleTheme };
}
