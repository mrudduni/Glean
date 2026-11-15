/** Small area sparkline in plain SVG (no chart library), coloured by the current text accent. */
export function Sparkline({ values, reversed = false, height = 56, label }: { values: number[]; reversed?: boolean; height?: number; label: string }) {
  if (values.length < 2) return null;
  const width = 300;
  const lo = reversed ? 0 : Math.min(...values);
  const hi = Math.max(...values);
  const span = hi - lo || 1;
  const x = (i: number) => (i / (values.length - 1)) * width;
  // reversed: larger values plot lower (depth to water reads downward, like a well).
  const y = (v: number) => {
    const t = (v - lo) / span;
    return 2 + (reversed ? t : 1 - t) * (height - 4);
  };
  const line = values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const base = reversed ? 0 : height;
  const area = `${line} L${width},${base} L0,${base} Z`;
  return (
    <svg className="sparkline" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" role="img" aria-label={label} width="100%" height={height}>
      <path d={area} fill="currentColor" fillOpacity={0.12} />
      <path d={line} fill="none" stroke="currentColor" strokeWidth={1.5} vectorEffect="non-scaling-stroke" />
    </svg>
  );
}
