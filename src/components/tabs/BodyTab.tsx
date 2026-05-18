import { useAppStore } from "../../store/appStore";

export function BodyTab() {
  const { body, method, setBody } = useAppStore();
  const usesBody = ["POST", "PUT", "PATCH"].includes(method);

  return (
    <div className="flex flex-col gap-2 py-3">
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder={`{\n  "key": "value"\n}`}
        spellCheck={false}
        className="input-base font-mono text-xs resize-none h-28 leading-relaxed"
      />
      <p className={`text-[10px] ${usesBody ? "text-text-muted" : "text-warning/70"}`}>
        {usesBody
          ? `Body will be sent with ${method} requests.`
          : `Body is not sent with ${method} — switch to POST, PUT, or PATCH.`}
      </p>
    </div>
  );
}
