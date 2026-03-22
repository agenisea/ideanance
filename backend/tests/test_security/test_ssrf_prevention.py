"""Tests for SSRF prevention."""

from ideanance.core.security.ssrf_prevention import validate_url


def test_allows_public_https():
    assert validate_url("https://example.com/api") is True


def test_allows_public_http():
    assert validate_url("http://example.com/api") is True


def test_blocks_localhost():
    assert validate_url("http://localhost:8080") is False


def test_blocks_127_0_0_1():
    assert validate_url("http://127.0.0.1:8080/admin") is False


def test_blocks_0_0_0_0():
    assert validate_url("http://0.0.0.0:80") is False


def test_blocks_private_ip_10():
    assert validate_url("http://10.0.0.1/internal") is False


def test_blocks_private_ip_172():
    assert validate_url("http://172.16.0.1/internal") is False


def test_blocks_private_ip_192_168():
    assert validate_url("http://192.168.1.1/admin") is False


def test_blocks_link_local():
    assert validate_url("http://169.254.1.1/metadata") is False


def test_blocks_metadata_endpoint():
    assert validate_url("http://metadata.google.internal/computeMetadata") is False


def test_blocks_aws_metadata():
    assert validate_url("http://169.254.169.254/latest/meta-data") is False


def test_blocks_ftp_scheme():
    assert validate_url("ftp://example.com/file") is False


def test_blocks_file_scheme():
    assert validate_url("file:///etc/passwd") is False


def test_blocks_empty_url():
    assert validate_url("") is False


def test_blocks_no_hostname():
    assert validate_url("http://") is False
