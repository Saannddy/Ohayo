import { useEffect } from "react";
import { useAppStore } from "../store/appStore";

export function useTheme() {
  const { isDark, toggleTheme } = useAppStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  return { isDark, toggleTheme };
}
