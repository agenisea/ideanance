import { render, screen, fireEvent } from "@testing-library/react";
import { PolicyCard } from "@/components/governance/policy-card";

const baseProps = {
  policyId: "nist-govern-1.1",
  name: "Legal and Regulatory Requirements",
  category: "govern",
  severity: "required",
  ruleCount: 3,
  wiringCount: 0,
  enabled: false,
  onToggle: vi.fn(),
};

describe("PolicyCard", () => {
  it("renders policy name and metadata", () => {
    render(<PolicyCard {...baseProps} />);
    expect(
      screen.getByText("Legal and Regulatory Requirements")
    ).toBeInTheDocument();
    expect(screen.getByText("3 rules")).toBeInTheDocument();
    expect(screen.getByText("severity: required")).toBeInTheDocument();
  });

  it("shows N/A badge when disabled and no wirings", () => {
    render(<PolicyCard {...baseProps} />);
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("shows Warning badge when enabled but no wirings", () => {
    render(<PolicyCard {...baseProps} enabled />);
    expect(screen.getByText("Warning")).toBeInTheDocument();
  });

  it("shows Pass badge when wirings exist", () => {
    render(<PolicyCard {...baseProps} enabled wiringCount={2} />);
    expect(screen.getByText("Pass")).toBeInTheDocument();
    expect(screen.getByText("2 evals wired")).toBeInTheDocument();
  });

  it("shows singular 'eval' for wiringCount=1", () => {
    render(<PolicyCard {...baseProps} enabled wiringCount={1} />);
    expect(screen.getByText("1 eval wired")).toBeInTheDocument();
  });

  it("calls onToggle when checkbox clicked", () => {
    const onToggle = vi.fn();
    render(<PolicyCard {...baseProps} onToggle={onToggle} />);
    const checkbox = screen.getByRole("checkbox");
    fireEvent.click(checkbox);
    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it("checkbox has accessible label", () => {
    render(<PolicyCard {...baseProps} />);
    expect(
      screen.getByLabelText("Activate Legal and Regulatory Requirements")
    ).toBeInTheDocument();
  });

  it("shows deactivate label when enabled", () => {
    render(<PolicyCard {...baseProps} enabled />);
    expect(
      screen.getByLabelText("Deactivate Legal and Regulatory Requirements")
    ).toBeInTheDocument();
  });
});
