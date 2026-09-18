"""
Comprehensive End-to-End Test Suite for Google Cloud Summit 2026.
Tests the live Flask server at http://127.0.0.1:5000 and data layer.
"""
import sys
import json
import urllib.request
import urllib.parse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"


def http_get(path):
    """Helper to perform HTTP GET on running server."""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "SummitTestBot/1.0"})
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def run_comprehensive_e2e():
    print("=" * 75)
    print("GOOGLE CLOUD SUMMIT 2026 - END-TO-END VERIFICATION SUITE")
    print(f"Target Server: {BASE_URL}")
    print("=" * 75)

    passed_count = 0
    total_count = 0

    def assert_test(name, condition, extra=""):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            passed_count += 1
            print(f" [PASS] Test {total_count:02d}: {name} {extra}")
        else:
            print(f" [FAIL] Test {total_count:02d}: {name} {extra}")
            raise AssertionError(f"Failed test: {name}")

    # 1. Server Connectivity & Home Page
    code, html = http_get("/")
    assert_test("Home Page HTTP 200 OK", code == 200)
    assert_test("Home Page contains Conference Name", "Google Cloud Summit 2026" in html)
    assert_test("Home Page contains Date (Saturday, October 24, 2026)", "Saturday, October 24, 2026" in html)
    assert_test("Home Page contains Venue (San Francisco)", "San Francisco" in html and "Google Community Space" in html)
    assert_test("Home Page contains Countdown timer element", 'id="countdownTimer"' in html)

    # 2. Schedule & 8 Talks Count
    code, json_str = http_get("/api/talks")
    assert_test("REST API /api/talks HTTP 200 OK", code == 200)
    talks_data = json.loads(json_str)
    talks = talks_data.get("talks", [])
    assert_test("Exact Talk Count (Requirement: 8 Talks)", len(talks) == 8, f"(found {len(talks)})")

    # 3. Speaker Limit Constraints (1 or 2 max)
    speaker_counts = [len(t["speakers"]) for t in talks]
    all_1_or_2 = all(1 <= c <= 2 for c in speaker_counts)
    assert_test("Speaker Count Constraint (1 or 2 speakers max per talk)", all_1_or_2, f"(counts: {speaker_counts})")

    # 4. Talk Schema Integrity
    schema_valid = all(
        isinstance(t["id"], int) and
        len(t["title"]) > 5 and
        1 <= len(t["categories"]) <= 2 and
        len(t["description"]) > 20 and
        len(t["start_time"]) > 0 and
        len(t["end_time"]) > 0
        for t in talks
    )
    assert_test("Talk Schema (ID, Title, 1-2 Categories, Description, Start/End Time)", schema_valid)

    # 5. Speaker Data (First Name, Last Name, LinkedIn URL)
    code, spk_json_str = http_get("/api/speakers")
    speakers = json.loads(spk_json_str).get("speakers", [])
    speakers_valid = all(
        len(s["first_name"]) > 0 and
        len(s["last_name"]) > 0 and
        s["linkedin"].startswith("https://www.linkedin.com/")
        for s in speakers
    )
    assert_test("Speaker Data Completeness (First Name, Last Name, Valid LinkedIn)", speakers_valid, f"({len(speakers)} speakers)")

    # 6. 60-Minute Lunch Break
    code, sched_json_str = http_get("/api/schedule")
    schedule = json.loads(sched_json_str).get("schedule", [])
    lunch_items = [i for i in schedule if i.get("is_lunch")]
    assert_test("Lunch Break Presence in Timetable", len(lunch_items) == 1)
    lunch = lunch_items[0]
    assert_test("Lunch Break 60-Minute Duration (01:05 PM – 02:05 PM)", "60" in lunch.get("duration", "") and "01:05 PM" in lunch.get("time", ""))

    # 7. Search & Filter: By Category
    categories = ["AI & ML", "Cloud Architecture", "Data & Analytics", "Cloud Security", "DevOps & SRE", "Serverless & Containers"]
    for cat in categories:
        encoded_cat = urllib.parse.quote(cat)
        code, cat_json_str = http_get(f"/api/talks?category={encoded_cat}")
        cat_talks = json.loads(cat_json_str).get("talks", [])
        assert_test(f"Filter by Category '{cat}'", len(cat_talks) >= 1, f"({len(cat_talks)} talks matched)")

    # 8. Search & Filter: By Speaker Name
    speaker_queries = ["Elena", "Priya", "Chen", "David", "Carlos", "Al-Mansoor"]
    for spk_q in speaker_queries:
        encoded_q = urllib.parse.quote(spk_q)
        code, spk_res = http_get(f"/api/talks?speaker={encoded_q}")
        matched_talks = json.loads(spk_res).get("talks", [])
        assert_test(f"Filter by Speaker Name '{spk_q}'", len(matched_talks) >= 1, f"({len(matched_talks)} talks matched)")

    # 9. Search & Filter: By Title / Keywords
    keyword_queries = ["Gemini", "Kubernetes", "BigQuery", "Zero Trust", "Cloud Run", "Spanner", "SRE", "Autonomous"]
    for kw in keyword_queries:
        encoded_kw = urllib.parse.quote(kw)
        code, kw_res = http_get(f"/api/talks?q={encoded_kw}")
        matched_talks = json.loads(kw_res).get("talks", [])
        assert_test(f"Filter by Title/Topic Keyword '{kw}'", len(matched_talks) >= 1, f"({len(matched_talks)} talks matched)")

    # 10. Individual Talk Pages (1 to 8)
    for talk_id in range(1, 9):
        code, talk_html = http_get(f"/talk/{talk_id}")
        assert_test(f"Talk Detail Page /talk/{talk_id} HTTP 200", code == 200 and f"Talk #0{talk_id}" in talk_html)

    # 11. 404 Error Handling
    code, err_html = http_get("/talk/999")
    assert_test("404 Error Page on invalid talk ID /talk/999", code == 404 and "Talk or Page Not Found" in err_html)

    # 12. Speakers Directory Page
    code, spk_html = http_get("/speakers")
    assert_test("Speakers Directory Page /speakers HTTP 200", code == 200 and "Elena Rostova" in spk_html and "https://www.linkedin.com/" in spk_html)

    # 13. Schedule Page
    code, sched_html = http_get("/schedule")
    assert_test("Schedule Page /schedule HTTP 200", code == 200 and "60-Min Lunch Break" in sched_html)

    # 14. Static Assets (CSS & JS)
    code, css_data = http_get("/static/css/style.css")
    assert_test("CSS Stylesheet /static/css/style.css HTTP 200", code == 200 and "--gcp-blue" in css_data)

    code, js_data = http_get("/static/js/app.js")
    assert_test("JavaScript /static/js/app.js HTTP 200", code == 200 and "initSearchAndFilter" in js_data)

    print("=" * 75)
    print(f"SUMMARY: {passed_count}/{total_count} TESTS PASSED SUCCESSFULLY! (100% SUCCESS RATE)")
    print("=" * 75)


if __name__ == "__main__":
    run_comprehensive_e2e()
