export default function ProjectLoading() {
  return (
    <div className="space-y-4 p-4 animate-pulse">
      <div
        className="h-8 w-48 rounded"
        style={{ backgroundColor: "var(--color-muted)" }}
      />
      <div
        className="h-4 w-96 rounded"
        style={{ backgroundColor: "var(--color-muted)" }}
      />
      <div className="grid grid-cols-3 gap-4 mt-6">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 rounded"
            style={{ backgroundColor: "var(--color-muted)" }}
          />
        ))}
      </div>
    </div>
  );
}
