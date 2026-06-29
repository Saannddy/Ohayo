/**
 * Resolve `{{name}}` placeholders against a variable map.
 * Unknown variables are left untouched so they're visible in the log.
 */
export function resolveVars(input: string, vars: Record<string, string>): string {
  if (!input) return input;
  return input.replace(/\{\{\s*([\w.-]+)\s*\}\}/g, (match, name: string) =>
    Object.prototype.hasOwnProperty.call(vars, name) ? vars[name] : match,
  );
}

/** Apply variable resolution across a header map (keys and values). */
export function resolveHeaders(
  headers: Record<string, string>,
  vars: Record<string, string>,
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(headers)) {
    out[resolveVars(k, vars)] = resolveVars(v, vars);
  }
  return out;
}
