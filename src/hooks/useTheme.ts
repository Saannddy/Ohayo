import { useEffect } from "react";
import { useAppStore } from "../store/appStore";

export function useTheme() {
  const { isDark, toggleTheme } = useAppStore();

  useEffect(() => {
    document.documentElement.dataset.theme = isDark ? "dark" : "light";
  }, [isDark]);

  return { isDark, toggleTheme };
}
