"""Tests for secret detection in user-submitted content."""

from core.security.secret_detection import detect_secrets, has_secrets


def test_detects_anthropic_api_key():
    content = "My key is sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxx"
    findings = detect_secrets(content)
    assert len(findings) == 1
    assert findings[0].pattern_name == "Anthropic API Key"


def test_detects_openai_api_key():
    content = "key = sk-1234567890abcdefghijklmnop"
    findings = detect_secrets(content)
    names = [f.pattern_name for f in findings]
    assert "OpenAI API Key" in names


def test_detects_aws_access_key():
    content = "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE"
    findings = detect_secrets(content)
    names = [f.pattern_name for f in findings]
    assert "AWS Access Key" in names


def test_detects_github_pat():
    content = "token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh12"
    findings = detect_secrets(content)
    names = [f.pattern_name for f in findings]
    assert "GitHub Personal Access Token" in names


def test_detects_private_key():
    content = "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."
    findings = detect_secrets(content)
    names = [f.pattern_name for f in findings]
    assert "Private Key" in names


def test_detects_hardcoded_password():
    content = 'password: "supersecret123"'
    findings = detect_secrets(content)
    names = [f.pattern_name for f in findings]
    assert "Hardcoded Password" in names


def test_detects_slack_token():
    content = "SLACK_TOKEN=xoxb-1234-5678-abcdefghij"
    findings = detect_secrets(content)
    names = [f.pattern_name for f in findings]
    assert "Slack Token" in names


def test_no_findings_for_clean_content():
    content = "This is a normal design description with no secrets."
    findings = detect_secrets(content)
    assert len(findings) == 0


def test_has_secrets_returns_bool():
    assert has_secrets("sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxx") is True
    assert has_secrets("normal content") is False


def test_multiple_secrets_in_one_content():
    content = (
        "api_key = sk-1234567890abcdefghijklmnop\n"
        "aws = AKIAIOSFODNN7EXAMPLE\n"
    )
    findings = detect_secrets(content)
    assert len(findings) >= 2


def test_finding_does_not_include_secret_value():
    content = "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxx"
    findings = detect_secrets(content)
    for f in findings:
        assert "sk-ant" not in f.pattern_name
