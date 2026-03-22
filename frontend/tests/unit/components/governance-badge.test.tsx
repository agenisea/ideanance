import { render, screen } from "@testing-library/react";
import { GovernanceBadge } from "@/components/governance/governance-badge";

describe("GovernanceBadge", () => {
  it("renders pass status with triple encoding (color + icon + text)", () => {
    render(<GovernanceBadge status="pass" score={0.92} />);
    expect(screen.getByText("Pass")).toBeInTheDocument();
    expect(screen.getByText("92%")).toBeInTheDocument();
    // Icon present
    expect(screen.getByRole("img", { name: "Pass" })).toBeInTheDocument();
  });

  it("renders fail status with label", () => {
    render(<GovernanceBadge status="fail" score={0.3} />);
    expect(screen.getByText("Fail")).toBeInTheDocument();
    expect(screen.getByText("30%")).toBeInTheDocument();
  });

  it("renders warn status with label", () => {
    render(<GovernanceBadge status="warn" score={0.65} />);
    expect(screen.getByText("Warning")).toBeInTheDocument();
  });

  it("renders na status without score", () => {
    render(<GovernanceBadge status="na" />);
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("has correct ARIA attributes for screen readers", () => {
    render(<GovernanceBadge status="warn" score={0.65} />);
    const badge = screen.getByRole("status");
    expect(badge).toHaveAttribute(
      "aria-label",
      "Governance status: Warning (65%)"
    );
  });

  it("omits score from aria-label when no score provided", () => {
    render(<GovernanceBadge status="na" />);
    const badge = screen.getByRole("status");
    expect(badge).toHaveAttribute("aria-label", "Governance status: N/A");
  });

  it("has data-testid for integration tests", () => {
    render(<GovernanceBadge status="pass" />);
    expect(screen.getByTestId("governance-badge")).toBeInTheDocument();
  });
});
