import Link from "next/link";

export default function ProjectNotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <h2 className="text-lg font-semibold">Project not found</h2>
      <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
        The project you are looking for does not exist or has been deleted.
      </p>
      <Link
        href="/projects"
        className="px-4 py-2 rounded text-sm font-medium"
        style={{
          backgroundColor: "var(--color-primary)",
          color: "var(--color-primary-foreground)",
        }}
      >
        Back to projects
      </Link>
    </div>
  );
}
