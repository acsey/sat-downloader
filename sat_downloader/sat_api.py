# -*- coding: utf-8 -*-
"""Helpers for communicating with SAT mass download services.

This module contains simplified wrappers around the SAT web service
for CFDI mass downloads. Endpoints must be filled with the real SAT
URLs. Functions are designed to be used by the GUI application and are
intended for educational purposes. They do not implement the full SAT
protocol but show the general structure required.
"""

from __future__ import annotations

import datetime as _dt
import os
import time
import zipfile
from typing import Callable, Iterable, List

import requests

# Placeholder endpoints (replace with actual SAT URLs)
AUTH_URL = "https://example.com/sat/auth"
QUERY_URL = "https://example.com/sat/query"
DOWNLOAD_URL = "https://example.com/sat/download"


class SATAPIError(Exception):
    """Raised when the SAT API returns an error."""


def authenticate(cer_path: str, key_path: str, password: str) -> str:
    """Authenticate with the SAT and return a security token.

    The actual implementation should sign the request with the user's
    certificate and private key and send it to the SAT authentication
    endpoint. This simplified version performs an HTTP POST request
    and expects a JSON response containing a token.
    """

    with open(cer_path, "rb") as cer_file, open(key_path, "rb") as key_file:
        files = {"cer": cer_file, "key": key_file}
        data = {"password": password}
        resp = requests.post(AUTH_URL, files=files, data=data, timeout=30)
    resp.raise_for_status()
    token = resp.json().get("token")
    if not token:
        raise SATAPIError("Token not found in response")
    return token


def query_available_packages(
    token: str,
    rfc: str,
    start: _dt.date,
    end: _dt.date,
) -> List[str]:
    """Request the list of download package identifiers for the given range."""
    payload = {
        "rfc": rfc,
        "fechaInicial": start.isoformat(),
        "fechaFinal": end.isoformat(),
    }
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(QUERY_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("packages", [])


def download_package(token: str, package_id: str, output_dir: str) -> str:
    """Download a single package and return the path to the ZIP file."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{DOWNLOAD_URL}/{package_id}",
        headers=headers,
        stream=True,
        timeout=60,
    )
    resp.raise_for_status()
    zip_path = os.path.join(output_dir, f"{package_id}.zip")
    with open(zip_path, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            fh.write(chunk)
    return zip_path


def extract_zip(zip_path: str, output_dir: str) -> Iterable[str]:
    """Extract XML files from a ZIP archive and yield their paths."""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if not info.filename.lower().endswith(".xml"):
                continue
            dest = os.path.join(output_dir, info.filename)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as fh, zf.open(info) as src:
                fh.write(src.read())
            yield dest


def download_invoices(
    rfc: str,
    cer_path: str,
    key_path: str,
    password: str,
    start: _dt.date,
    end: _dt.date,
    batch_callback: Callable[[int, int], None] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    output_dir: str = "downloads",
) -> None:
    """Download all invoices for the RFC in the given date range."""
    token = authenticate(cer_path, key_path, password)
    packages = query_available_packages(token, rfc, start, end)
    total = len(packages)
    if batch_callback:
        batch_callback(total, 0)
    for idx, pkg in enumerate(packages, 1):
        try:
            zip_path = download_package(token, pkg, output_dir)
            extract_zip(zip_path, output_dir)
            if progress_callback:
                progress_callback(idx, total)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Failed to download package {pkg}: {exc}")
        time.sleep(1)  # avoid hammering the server
