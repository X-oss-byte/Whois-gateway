import os
import tempfile
import pytest
from app import app


@pytest.fixture(name='client')
def fixture_client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            None
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_error_for_non_existent_path(client):
    """404 for non-existent path."""

    assert client.get('/non-existent-path').status_code == 404
    assert client.get('/x/').status_code == 404


def test_error_for_invalid_ip(client):
    """400 for invalid IP addresses."""

    assert client.get('/w/x.x.x.x').status_code == 400


def test_respond_to_entry_path_ipv4(client):
    """200 for simple paths"""

    assert client.get('/w/8.8.8.8').status_code == 200
    assert client.get('/').status_code == 200
    assert client.get('/whois/8.8.8.8').status_code == 200
    assert client.get('/gateway.py?').status_code == 200
    assert client.get('/robots.txt').status_code == 200


def test_respond_to_standard_path_ipv6(client):
    """200 for simple paths (IPv6)."""

    assert client.get('/w/2606:4700:4700::1111').status_code == 200
    assert client.get('/w/1%3A%3A1/').status_code == 200


def test_respond_to_rest_queries(client):
    """200 for REST queries."""

    assert client.get('/w/2606:4700:4700::1111/lookup').status_code == 200
    assert client.get('/w/2606:4700:4700::1111/lookup/json').status_code == 200
    assert client.get('/w/8.8.8.8/lookup').status_code == 200
    assert client.get('/w/8.8.8.8/redirect/APNIC').status_code == 302


def test_respond_to_legacy_queries(client):
    """200 for legacy queries."""

    assert client.get('/gateway.py?ip=8.8.8.8&lookup=true').status_code == 200


def test_error_for_attack(client):
    """400 for paths that obviously do not ask about IPs"""

    assert client.get('/w/../../').status_code == 400
    assert client.get('/w/ "| ls / "').status_code == 400


def test_tolerance_to_whitespace(client):
    """200 for paths that include different kinds of whitespace."""

    assert client.get('/w/%208.8.8.8').status_code == 200
    assert client.get('/w/8.8.8. ').status_code == 200
    assert client.get('/w/ 8.8.8.8/').status_code == 200


if __name__ == '__main__':
    pytest.main()
