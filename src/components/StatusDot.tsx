import { useAppStore } from "../store/appStore";

export function StatusDot() {
  const { isRunning, statusColor } = useAppStore();

  const color =
    isRunning ? "bg-success shadow-glow-success"
    : statusColor === "danger" ? "bg-danger"
    : "bg-text-muted";

  const pulse = isRunning
    ? "before:absolute before:inset-0 before:rounded-full before:bg-success before:animate-ping before:opacity-60"
    : "";

  return (
    <span className={`relative inline-flex items-center justify-center w-3 h-3 ${pulse}`}>
      <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 transition-colors duration-300 ${color}`} />
    </span>
  );
}
