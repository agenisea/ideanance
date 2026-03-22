import { render, screen } from "@testing-library/react";
import { EvalCriterionCard } from "@/components/evaluation/eval-criterion-card";

describe("EvalCriterionCard", () => {
  it("renders criterion details", () => {
    render(
      <EvalCriterionCard
        criterionId="eval-001"
        description="Agent must state its purpose clearly"
        metric="purpose_statement_present"
        threshold="100%"
        priority="required"
      />
    );
    expect(screen.getByText("eval-001")).toBeInTheDocument();
    expect(
      screen.getByText("Agent must state its purpose clearly")
    ).toBeInTheDocument();
    expect(
      screen.getByText("metric: purpose_statement_present")
    ).toBeInTheDocument();
    expect(screen.getByText("threshold: 100%")).toBeInTheDocument();
    expect(screen.getByText("required")).toBeInTheDocument();
  });

  it("shows wiring indicator when wired to a policy", () => {
    render(
      <EvalCriterionCard
        criterionId="eval-002"
        description="Risk assessment documented"
        metric="risk_assessment_present"
        threshold="100%"
        priority="recommended"
        wiredPolicyName="Risk Assessment"
        wiredFramework="NIST AI RMF"
      />
    );
    expect(
      screen.getByText("NIST AI RMF — Risk Assessment")
    ).toBeInTheDocument();
  });

  it("does not show wiring indicator when not wired", () => {
    render(
      <EvalCriterionCard
        criterionId="eval-003"
        description="No wiring"
        metric="test"
        threshold="80%"
        priority="optional"
      />
    );
    expect(screen.queryByText(/NIST/)).not.toBeInTheDocument();
  });
});
