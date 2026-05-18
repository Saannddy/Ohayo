import { useAppStore } from "../store/appStore";

interface ChipProps {
  label: string;
  value: string;
  colorClass: string;
}

function StatChip({ label, value, colorClass }: ChipProps) {
  return (
    <div className="flex-1 min-w-0 bg-input-bg border border-border rounded-xl px-4 py-3">
      <div className={`text-xs font-semibold mb-1 ${colorClass}`}>{label}</div>
      <div className={`text-2xl font-bold tabular-nums truncate ${colorClass}`}>{value}</div>
    </div>
  );
}

export function StatsRow() {
  const { stats } = useAppStore();

  const chips: ChipProps[] = [
    {
      label: "Total",
      value: stats.total === 0 ? "—" : String(stats.total),
      colorClass: "text-accent",
    },
    {
      label: "Success",
      value: stats.total === 0 ? "—%" : `${stats.successPct.toFixed(1)}%`,
      colorClass: "text-success",
    },
    {
      label: "Avg ms",
      value: stats.total === 0 ? "—ms" : `${stats.avgMs.toFixed(0)}ms`,
      colorClass: "text-warning",
    },
    {
      label: "Status",
      value: stats.lastStatus != null ? String(stats.lastStatus) : "—",
      colorClass: "text-text-secondary",
    },
  ];

  return (
    <div className="flex gap-2">
      {chips.map((c) => <StatChip key={c.label} {...c} />)}
    </div>
  );
}
