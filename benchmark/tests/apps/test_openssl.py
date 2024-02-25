"""
Tests for openssl s_client
"""

import itertools
import logging

import pytest
from conftest import (DUMP_METHODS, TLS_CLIENTS_CONTAINER,
                      TLS_TRAFFIC_ANALYZER_CONTAINER, URL_TLS_12_ONLY,
                      URL_TLS_13_ONLY, save_benchmark_results,
                      tls_decryption_success)

LOGGER = logging.getLogger()


@pytest.mark.parametrize(
    "dump_method,url",
    [
        (dump_method, url)
        for dump_method, url in itertools.product(
            DUMP_METHODS, (URL_TLS_12_ONLY, URL_TLS_13_ONLY)
        )
    ]
)
def test_openssl(dump_method, url):
    url = url[8:]  # remove https://
    TLS_TRAFFIC_ANALYZER_CONTAINER.exec_run(
        ["bash", "-c", f"echo {dump_method} > /tmp/dump_method"]
    )
    exit_code, output = TLS_CLIENTS_CONTAINER.exec_run(
        ["sh", "-c", f'echo -e "GET / HTTP/1.1\r\nHost:{url}\r\n\r\n" | openssl s_client -connect {url}']
    )
    assert exit_code == 0, f"TLS client failed to run: {output}"
    success, sessions = tls_decryption_success()
    assert success, f"TLS client logs: {output}\n"
    save_benchmark_results("openssl", dump_method, sessions)
