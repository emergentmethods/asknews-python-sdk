"""Synthetic only: no credentials or network. Run pytest in this directory."""

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import httpx
import pytest
from openpyxl import load_workbook

from asknews_sdk import AskNewsSDK


spec = importlib.util.spec_from_file_location(
    "distribution_report", Path(__file__).with_name("distribution_report.py")
)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
UTC = timezone.utc


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    import socket

    monkeypatch.setattr(
        socket.socket, "connect", Mock(side_effect=AssertionError("Network forbidden"))
    )


def article(n=1, value=3, url=None):
    return {
        "article_id": str(UUID(int=n)),
        "article_url": url or f"https://apnews.com/article/{n}",
        "hit_count": value,
    }


def page(rows, number=1, next_page=None):
    return {
        "data": rows,
        "total_count": sum(row["hit_count"] for row in rows),
        "page": number,
        "next_page": next_page,
    }


class Fake:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, endpoint, query):
        self.calls.append((endpoint, query))
        value = next(self.responses)
        if isinstance(value, Exception):
            raise value
        return value


@pytest.mark.parametrize(
    "month,days", [("2026-09", 30), ("2024-02", 29), ("2026-02", 28), ("2026-12", 31)]
)
def test_months_and_utc(month, days, monkeypatch):
    monkeypatch.setenv("TZ", "Pacific/Honolulu")
    start, end, following = m.month_bounds(month)
    assert following - start == timedelta(days=days)
    assert (following - end).total_seconds() == 1
    assert start.tzinfo == UTC
    if month == "2026-09":
        assert int(start.timestamp()) == 1788220800
        assert int(end.timestamp()) == 1790812799
    assert int(end.timestamp()) == int(following.timestamp()) - 1


@pytest.mark.parametrize(
    "month", ["2026-13", "2026-00", "2026-9", "1999-12", "2101-01", "2026-09Z"]
)
def test_invalid_month(month):
    with pytest.raises(m.ReportError):
        m.month_bounds(month)


@pytest.mark.parametrize(
    "value", ["https://apnews.com", "*.apnews.com", "apnews.com.evil/", "apnews.com.", "a,b.com"]
)
def test_domain_input(value):
    with pytest.raises(m.ReportError):
        m.exact_domain(value)


def test_paginate_and_page_totals():
    reader = Fake([page([article()], next_page=2), page([article(2, 4)], 2)])
    ranked = m.ranking(reader, {}, "apnews.com", "surface", 1, 4)
    assert ranked.complete and ranked.pages == 2
    assert sum(item[1] for item in ranked.rows.values()) == 7
    assert [call[1]["page"] for call in reader.calls] == [1, 2]


@pytest.mark.parametrize(
    "second",
    [
        page([article()], 2),
        page([article(2)], 2, 2),
        {"data": [], "total_count": 0},
        {"data": [article(2)], "total_count": 999, "page": 2, "next_page": None},
    ],
)
def test_page_guards_preserve_only_valid_pages(second):
    ranked = m.ranking(
        Fake([page([article()], next_page=2), second]), {}, "apnews.com", "surface", 1, 5
    )
    assert not ranked.complete
    assert len(ranked.rows) == 1


def test_caps_and_empty_final_page():
    ranked = m.ranking(Fake([page([article()], next_page=2)]), {}, "apnews.com", "surface", 1, 1)
    assert not ranked.complete and "cap" in ranked.note
    ranked = m.ranking(
        Fake([page([article()], next_page=2), page([], 2)]), {}, "apnews.com", "surface", 1, 2
    )
    assert ranked.complete and len(ranked.rows) == 1


@pytest.mark.parametrize(
    "url",
    [
        "https://other.com/a",
        "https://www.apnews.com/a",
        "https://apnews.com.evil/a",
        "https://u:p@apnews.com/a",
        '=HYPERLINK("https://evil")',
    ],
)
def test_domain_isolation(url):
    ranked = m.ranking(Fake([page([article(url=url)])]), {}, "apnews.com", "surface", 100, 1)
    assert not ranked.complete and not ranked.rows
    assert url not in ranked.note


def test_missing_id_is_not_url_joined():
    row = article()
    del row["article_id"]
    ranked = m.ranking(Fake([page([row])]), {}, "apnews.com", "surface", 100, 1)
    assert not ranked.complete and not ranked.rows


def report_fixture():
    report = m.Report("apnews.com", "2026-09")
    report.ranks = {
        "surface": m.Ranking({str(UUID(int=1)): ("https://apnews.com/a", 4)}, True, "exhausted", 1),
        "citation": m.Ranking(
            {str(UUID(int=2)): ("https://apnews.com/b", 2)}, True, "exhausted", 1
        ),
        "grounded": m.Ranking({}, False, "cap", 0),
    }
    return report


def test_join_missing_vs_zero_no_double_count():
    rows = list(m.joined_articles(report_fixture()))
    assert rows[0][2:] == (4, 0, None)
    assert rows[1][2:] == (0, 2, None)


def test_conflicting_identity_rejected():
    report = report_fixture()
    report.ranks["citation"].rows[str(UUID(int=1))] = ("https://apnews.com/changed", 2)
    with pytest.raises(m.ReportError, match="conflicting"):
        list(m.joined_articles(report))


def test_missing_daily_fields_and_absent_days_stay_unknown():
    start, _, end = m.month_bounds("2026-09")
    result = m.daily_values(
        {"data": [{"day": "2026-09-01", "surfaces": 0}], "total_surfaces": 0}, m.FIELDS, start, end
    )
    assert result["2026-09-01"]["surfaces"] == 0
    assert result["2026-09-01"]["grounded"] is None
    assert "2026-09-02" not in result


@pytest.mark.parametrize(
    "days", [["2026-09-01", "2026-09-01"], ["2026-10-01"], ["2026-09-01T00:00:00-04:00"]]
)
def test_daily_guard(days):
    start, _, end = m.month_bounds("2026-09")
    with pytest.raises(m.ReportError):
        m.daily_values(
            {"data": [{"day": day, "surfaces": 1} for day in days]}, ["surfaces"], start, end
        )


def test_daily_reconciliation():
    start, _, end = m.month_bounds("2026-09")
    with pytest.raises(m.ReportError, match="sum"):
        m.daily_values(
            {"data": [{"day": "2026-09-01", "surfaces": 3}], "total_surfaces": 4},
            ["surfaces"],
            start,
            end,
        )


def sdk_reader(handler, **kwargs):
    reader = m.Reader(None, sleep=Mock(), **kwargs)
    sdk = AskNewsSDK(
        api_key="synthetic-not-real",
        transport=httpx.MockTransport(handler),
        retries=0,
        follow_redirects=False,
        event_hooks={"request": [reader.before_request], "response": [reader.after_response]},
    )
    reader.sdk = sdk
    return reader


@pytest.mark.parametrize("status,error", [(401, m.AuthError), (403, m.Denied)])
def test_auth_no_retries_or_body_leak(status, error):
    handler = Mock(return_value=httpx.Response(status, text="SECRET PII"))
    reader = sdk_reader(handler)
    with pytest.raises(error) as caught:
        reader.get(m.RANK, {"domain_names": ["apnews.com"]})
    assert "SECRET" not in str(caught.value)
    assert handler.call_count == 1
    reader.sdk.close()


def test_429_then_503_then_success_actual_sdk():
    handler = Mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "3"}),
            httpx.Response(503),
            httpx.Response(200, json={"data": []}),
        ]
    )
    reader = sdk_reader(handler)
    assert reader.get(m.RANK, {}) == {"data": []}
    assert reader.requests == 3
    assert [call.args[0] for call in reader.sleep.call_args_list] == [1.0, 3, 1.0, 2, 1.0]
    assert all(call.args[0].method == "GET" for call in handler.call_args_list)
    reader.sdk.close()


def test_retry_after_date_and_budget():
    now = datetime(2026, 9, 1, tzinfo=UTC)
    assert m.retry_delay("Tue, 01 Sep 2026 00:00:07 GMT", 0, now) == 7
    for value in ("600", "NaN", "infinity", "nonsense"):
        with pytest.raises(m.ReportError):
            m.retry_delay(value, 0, now)
    reader = sdk_reader(lambda req: httpx.Response(503), max_requests=1)
    with pytest.raises(m.ReportError, match="budget"):
        reader.get(m.RANK, {})
    assert reader.requests == 1
    reader.sdk.close()


def test_transient_retry_bound_and_timeout_budget():
    reader = sdk_reader(lambda req: httpx.Response(503))
    with pytest.raises(m.ReportError, match="three"):
        reader.get(m.RANK, {})
    assert reader.requests == 3
    reader.deadline = 0
    with pytest.raises(m.ReportError, match="budget"):
        reader.get(m.RANK, {})
    reader.sdk.close()


def test_oauth_401_stops_before_sdk_refresh():
    handler = Mock(return_value=httpx.Response(401, text="secret"))
    reader = m.Reader(None, sleep=Mock())
    sdk = AskNewsSDK(
        client_id="fake",
        client_secret="fake",
        scopes={"distribution"},
        transport=httpx.MockTransport(handler),
        event_hooks={"request": [reader.before_request], "response": [reader.after_response]},
    )
    reader.sdk = sdk
    with pytest.raises(m.AuthError):
        reader.get(m.RANK, {})
    assert handler.call_count == 1  # token exchange only; no retry
    sdk.close()


def test_index_disjoint_utc_and_leap_days():
    report = m.Report("apnews.com", "2024-02")
    start, _, following = m.month_bounds(report.month)
    calls = []

    def get(endpoint, query):
        calls.append(query)
        assert endpoint == m.INDEX
        assert query["domains"] == ["apnews.com"]
        assert query["time_filter"] == "crawl_date"
        return [{"start": query["start_datetime"], "end": query["end_datetime"], "count": 1}]

    m.collect_index(SimpleNamespace(get=get), report, start, following)
    assert len(calls) == 29 and sum(report.index.values()) == 29
    for first, second in zip(calls, calls[1:]):
        assert datetime.fromisoformat(
            first["end_datetime"].replace("Z", "+00:00")
        ) < datetime.fromisoformat(second["start_datetime"].replace("Z", "+00:00"))
    assert all(query["end_datetime"].endswith("23:59:59Z") for query in calls)


@pytest.mark.parametrize("start_string", ["2026-09-01T00:00:00", "2026-09-01T00:00:00-04:00"])
def test_index_rejects_naive_or_shifted_dates(start_string):
    report = m.Report("apnews.com", "2026-09")
    start, _, end = m.month_bounds(report.month)
    with pytest.raises(m.ReportError, match="timezone"):
        m.collect_index(
            Fake([[{"start": start_string, "end": "2026-09-01T23:59:59Z", "count": 1}]]),
            report,
            start,
            end,
        )
    assert not report.index


def test_share_not_dollars_and_foreign_rejected():
    assert m.parse_share({"data": [{"domain": "apnews.com", "hit_share": 0}]}, "apnews.com") == 0
    with pytest.raises(m.ReportError):
        m.parse_share({"data": [{"domain": "other.com", "hit_share": 0.4}]}, "apnews.com")
    with pytest.raises(m.ReportError):
        m.parse_share({"data": []}, "apnews.com")


def test_internal_forbidden_group_stops_without_zero():
    report = report_fixture()
    reader = Fake([m.Denied("403: internal scope required")])
    start, _, following = m.month_bounds(report.month)
    report.section("internal", lambda: m.collect_internal(reader, report, {}, start, following))
    assert len(reader.calls) == 1 and report.issues and not report.totals


def test_workbook_open_totals_injection_and_no_links(tmp_path):
    report = report_fixture()
    report.share = 0.25
    report.daily = {"2026-09-01": {"surfaces": 0, "citations": 2, "grounded": None}}
    book = m.workbook(report)
    payloads = [
        '=HYPERLINK("https://evil","x")',
        "+SUM(A1)",
        "-1+2",
        "@SUM(A1)",
        "\t=1+1",
        "https://apnews.com/a?x==SUM(A1)",
        "title\x01control",
    ]
    m.sheet(book, "Synthetic injection", ("Text",), [(value,) for value in payloads])
    path = tmp_path / "synthetic.xlsx"
    m.save_workbook(book, path)
    opened = load_workbook(path, data_only=False)
    assert {
        "Summary",
        "Daily metrics",
        "Articles",
        "Weighted share",
        "Coverage",
        "Methodology",
    } <= set(opened.sheetnames)
    assert opened["Daily metrics"]["B2"].value == 0
    assert opened["Daily metrics"]["D2"].value is None
    assert opened["Daily metrics"]["B3"].value is None
    assert opened["Weighted share"]["B2"].value == 0.25
    assert sum(row[2] for row in opened["Articles"].iter_rows(min_row=2, values_only=True)) == 4
    assert opened["Synthetic injection"]["A2"].value == payloads[0]
    for ws in opened:
        assert ws.freeze_panes == "A2" and ws.auto_filter.ref
        for row in ws:
            assert all(cell.data_type != "f" and not cell.hyperlink for cell in row)
    assert not opened._external_links
    with pytest.raises(m.ReportError, match="exists"):
        m.save_workbook(book, path)


def test_environment_auth_and_no_cli_credentials():
    assert m.credentials({"ASKNEWS_API_KEY": "synthetic"}) == {"api_key": "synthetic"}
    assert m.credentials({"ASKNEWS_CLIENT_ID": "a", "ASKNEWS_CLIENT_SECRET": "b"})["scopes"] == {
        "distribution",
        "news",
    }
    for env in (
        {},
        {"ASKNEWS_CLIENT_SECRET": "b"},
        {"ASKNEWS_API_KEY": "a", "ASKNEWS_CLIENT_ID": "b"},
    ):
        with pytest.raises(m.ReportError):
            m.credentials(env)


def test_end_to_end_synthetic_sdk_requests_and_metrics(tmp_path):
    def handler(request):
        q = request.url.params
        assert request.method == "GET"
        assert q.get_list("domain_names") == ["apnews.com"] or q.get_list("domains") == [
            "apnews.com"
        ]
        path = request.url.path
        if path == m.RANK:
            return httpx.Response(200, json=page([article(value=3)]))
        if path == m.SHARE:
            return httpx.Response(200, json={"data": [{"domain": "apnews.com", "hit_share": 0.1}]})
        if path == m.TOTAL:
            return httpx.Response(200, json=dict.fromkeys(m.FIELDS, 3))
        if path == m.DAILY:
            return httpx.Response(
                200,
                json={
                    "data": [dict(day="2026-09-01", **dict.fromkeys(m.FIELDS, 3))],
                    **{"total_" + name: 3 for name in m.FIELDS},
                },
            )
        if path == m.UNIQUE:
            return httpx.Response(200, json={"hits": 3, "surfaced": 1})
        if path == m.UNIQUE_DAILY:
            return httpx.Response(
                200,
                json={
                    "data": [{"day": "2026-09-01", "hits": 3, "surfaced": 1}],
                    "total_hits": 3,
                    "total_surfaced": 1,
                },
            )
        assert path == m.INDEX
        return httpx.Response(
            200, json=[{"start": q["start_datetime"], "end": q["end_datetime"], "count": 2}]
        )

    reader = sdk_reader(handler)
    report = m.collect(reader, "apnews.com", "2026-09", include_internal=True)
    assert not report.issues and reader.requests == 38
    assert report.totals["grounded"] == 3 and len(report.index) == 30
    path = tmp_path / "complete-fixture.xlsx"
    m.save_workbook(m.workbook(report), path)
    assert load_workbook(path)["Articles"].max_row == 2
    reader.sdk.close()


def test_partial_output_is_explicit(tmp_path, monkeypatch, capsys):
    report = report_fixture()
    report.issues = ["synthetic partial"]
    monkeypatch.setattr(m, "credentials", lambda env: {"api_key": "synthetic"})
    monkeypatch.setattr(m, "collect", lambda *a: report)
    output = tmp_path / "partial.xlsx"
    assert m.main(["--output", str(output)]) == 1
    assert not output.exists()
    assert m.main(["--output", str(output), "--allow-partial"]) == 2
    assert output.exists()
    assert "PARTIAL CALENDAR COVERAGE" in capsys.readouterr().out


def test_api_401_does_not_trigger_sdk_oauth_refresh():
    handler = Mock(
        side_effect=[
            httpx.Response(
                200, json={"access_token": "synthetic", "expires_in": 3600, "token_type": "Bearer"}
            ),
            httpx.Response(401, text="sensitive body"),
        ]
    )
    reader = m.Reader(None, sleep=Mock())
    with AskNewsSDK(
        client_id="fake",
        client_secret="fake",
        scopes={"distribution"},
        transport=httpx.MockTransport(handler),
        event_hooks={"request": [reader.before_request], "response": [reader.after_response]},
    ) as sdk:
        reader.sdk = sdk
        with pytest.raises(m.AuthError):
            reader.get(m.RANK, {})
    assert handler.call_count == 2
    assert reader.requests == 2


def test_partial_page_failure_and_numeric_precision():
    ranked = m.ranking(
        Fake([page([article()], next_page=2), m.ReportError("Transient exhausted")]),
        {},
        "apnews.com",
        "surface",
        1,
        3,
    )
    assert not ranked.complete and len(ranked.rows) == 1
    for value in (None, True, -1, 2**53, 1.5, "3"):
        with pytest.raises(m.ReportError):
            m.count(value)
