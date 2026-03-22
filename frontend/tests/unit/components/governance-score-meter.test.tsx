import { render, screen } from "@testing-library/react";
import { GovernanceScoreMeter } from "@/components/governance/governance-score-meter";

describe("GovernanceScoreMeter", () => {
  it("renders with role=meter and correct ARIA attributes", () => {
    render(<GovernanceScoreMeter score={0.85} />);
    const meter = screen.getByRole("meter");
    expect(meter).toHaveAttribute("aria-valuenow", "85");
    expect(meter).toHaveAttribute("aria-valuemin", "0");
    expect(meter).toHaveAttribute("aria-valuemax", "100");
  });

  it("includes label in aria-label", () => {
    render(<GovernanceScoreMeter score={0.72} label="Policy Score" />);
    const meter = screen.getByRole("meter");
    expect(meter).toHaveAttribute("aria-label", "Policy Score: 72%");
  });

  it("uses default label when none provided", () => {
    render(<GovernanceScoreMeter score={0.5} />);
    const meter = screen.getByRole("meter");
    expect(meter).toHaveAttribute("aria-label", "Governance Score: 50%");
  });

  it("displays percentage text", () => {
    render(<GovernanceScoreMeter score={0.93} />);
    expect(screen.getByText("93%")).toBeInTheDocument();
  });

  it("rounds score correctly", () => {
    render(<GovernanceScoreMeter score={0.856} />);
    expect(screen.getByText("86%")).toBeInTheDocument();
  });
});
