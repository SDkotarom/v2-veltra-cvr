#!/usr/bin/env python3
"""
Fix W14 data.json: replace eventCount/sessions-based metrics with activeUsers.
Also fix W15 data.json prev_week (which inherits from W14 current_week) and recalculate wow_pp.

Root cause: W14 data was collected using eventCount for event-based steps
and sessions for page-based steps, instead of activeUsers throughout.
Purchase uses transactions (correct in both weeks).
"""

import json
import copy

def safe_div(a, b):
    if b == 0 or b is None:
        return None
    return round(a / b, 6)

# ── Corrected W14 data from GA4 (activeUsers metric, transactions for purchase) ──

# 28d baseline (2026-03-08 to 2026-04-04)
BASELINE_CORRECTED = {
    "sessions": 2945578,
    "session_start_users": 1811769,
    "ac_page_reach_users": 944855,
    "calendar_view": 138526,
    "form_start": 55045,
    "purchase": 42119,
}

# 7d current_week (2026-03-29 to 2026-04-04)
CURRENT_WEEK_CORRECTED = {
    "session_start_users": 493632,
    "ac_page_reach_users": 257671,
    "calendar_view": 36659,
    "form_start": 15984,
    "purchase": 10118,
}

# 7d prev_week (2026-03-22 to 2026-03-28)
PREV_WEEK_CORRECTED = {
    "session_start_users": 501056,
    "ac_page_reach_users": 267580,
    "calendar_view": 37030,
    "form_start": 15957,
    "purchase": 9536,
}

# ── Channel segment data (28d baseline, activeUsers) ──
CHANNEL_CORRECTED = {
    "Organic Search": {
        "sessions": 1203050, "purchases": 9236,
        "funnel": {"ac_page_reach_users": 401958, "calendar_view": 53149, "form_start": 15838, "purchase": 9236}
    },
    "Paid Search": {
        "sessions": 712209, "purchases": 10028,
        "funnel": {"ac_page_reach_users": 286703, "calendar_view": 47833, "form_start": 16059, "purchase": 10028}
    },
    "Direct": {
        "sessions": 405298, "purchases": 7957,
        "funnel": {"ac_page_reach_users": 156733, "calendar_view": 20447, "form_start": 11760, "purchase": 7957}
    },
    "Unassigned": {
        "sessions": 226953, "purchases": 7778,
        "funnel": {"ac_page_reach_users": 71841, "calendar_view": 12620, "form_start": 11737, "purchase": 7778}
    },
    "Email": {
        "sessions": 170756, "purchases": 3169,
        "funnel": {"ac_page_reach_users": 28674, "calendar_view": 5932, "form_start": 14860, "purchase": 3169}
    },
    "Referral": {
        "sessions": 99858, "purchases": 2489,
        "funnel": {"ac_page_reach_users": 44776, "calendar_view": 8952, "form_start": 5341, "purchase": 2489}
    },
    "Paid Other": {
        "sessions": 89397, "purchases": 878,
        "funnel": {"ac_page_reach_users": 44767, "calendar_view": 4500, "form_start": 1435, "purchase": 878}
    },
    "Paid Social": {
        "sessions": 25438, "purchases": 12,
        "funnel": {"ac_page_reach_users": 862, "calendar_view": 102, "form_start": 29, "purchase": 12}
    },
    "Organic Social": {
        "sessions": 10668, "purchases": 102,
        "funnel": {"ac_page_reach_users": 4501, "calendar_view": 744, "form_start": 203, "purchase": 102}
    },
    "Cross-network": {
        "sessions": 4094, "purchases": 448,
        "funnel": {"ac_page_reach_users": 2960, "calendar_view": 950, "form_start": 536, "purchase": 448}
    },
    "Organic Video": {
        "sessions": 783, "purchases": 14,
        "funnel": {"ac_page_reach_users": 464, "calendar_view": 70, "form_start": 22, "purchase": 14}
    },
    "Affiliates": {
        "sessions": 378, "purchases": 8,
        "funnel": {"ac_page_reach_users": 120, "calendar_view": 21, "form_start": 11, "purchase": 8}
    },
    "Organic Shopping": {
        "sessions": 141, "purchases": 0,
        "funnel": {"ac_page_reach_users": 136, "calendar_view": 2, "form_start": 0, "purchase": 0}
    },
}

# ── Device segment data (28d baseline, activeUsers) ──
DEVICE_CORRECTED = {
    "mobile": {
        "sessions": 2123396, "purchases": 29330,
        "funnel": {"ac_page_reach_users": 662320, "calendar_view": 105619, "form_start": 43046, "purchase": 29330}
    },
    "desktop": {
        "sessions": 785730, "purchases": 12259,
        "funnel": {"ac_page_reach_users": 265482, "calendar_view": 32184, "form_start": 14790, "purchase": 12259}
    },
    "tablet": {
        "sessions": 45647, "purchases": 530,
        "funnel": {"ac_page_reach_users": 16406, "calendar_view": 2201, "form_start": 771, "purchase": 530}
    },
}

# ── New/Returning segment data (28d baseline, activeUsers) ──
NEW_RETURNING_CORRECTED = {
    "new": {
        "sessions": 1588011, "purchases": 9876,
        "funnel": {"ac_page_reach_users": 744179, "calendar_view": 67658, "form_start": 18608, "purchase": 9876}
    },
    "returning": {
        "sessions": 1186802, "purchases": 32243,
        "funnel": {"ac_page_reach_users": 324603, "calendar_view": 79548, "form_start": 43618, "purchase": 32243}
    },
}

# ── Channel x Device (sessions + purchases only, from GA4) ──
CHANNEL_DEVICE_CORRECTED = {
    "Organic Search|mobile": {"sessions": 923033, "purchases": 5832},
    "Paid Search|mobile": {"sessions": 533267, "purchases": 6480},
    "Organic Search|desktop": {"sessions": 289737, "purchases": 3282},
    "Direct|desktop": {"sessions": 202546, "purchases": 1864},
    "Direct|mobile": {"sessions": 199621, "purchases": 6014},
    "Unassigned|mobile": {"sessions": 191439, "purchases": 6809},
    "Paid Search|desktop": {"sessions": 158110, "purchases": 3397},
    "Email|mobile": {"sessions": 131966, "purchases": 1992},
    "Referral|mobile": {"sessions": 66669, "purchases": 1580},
    "Paid Other|desktop": {"sessions": 46756, "purchases": 748},
    "Paid Other|mobile": {"sessions": 40737, "purchases": 125},
    "Email|desktop": {"sessions": 35734, "purchases": 1144},
    "Unassigned|desktop": {"sessions": 35315, "purchases": 878},
    "Referral|desktop": {"sessions": 32463, "purchases": 872},
    "Paid Social|mobile": {"sessions": 24424, "purchases": 12},
    "Organic Search|tablet": {"sessions": 20937, "purchases": 122},
    "Paid Search|tablet": {"sessions": 13472, "purchases": 151},
    "Organic Social|mobile": {"sessions": 9532, "purchases": 87},
    "Direct|tablet": {"sessions": 3704, "purchases": 79},
    "Cross-network|mobile": {"sessions": 3626, "purchases": 383},
    "Unassigned|tablet": {"sessions": 2480, "purchases": 91},
    "Email|tablet": {"sessions": 1707, "purchases": 33},
    "Referral|tablet": {"sessions": 1385, "purchases": 37},
    "Organic Social|desktop": {"sessions": 967, "purchases": 15},
    "Paid Other|tablet": {"sessions": 915, "purchases": 5},
    "Paid Social|tablet": {"sessions": 753, "purchases": 0},
    "Organic Video|mobile": {"sessions": 463, "purchases": 10},
    "Cross-network|desktop": {"sessions": 426, "purchases": 53},
    "Paid Social|desktop": {"sessions": 322, "purchases": 0},
    "Organic Video|desktop": {"sessions": 286, "purchases": 4},
}


def calc_rates(funnel_dict, sessions=None):
    """Calculate conversion rates from funnel dict."""
    ac = funnel_dict["ac_page_reach_users"]
    cal = funnel_dict["calendar_view"]
    form = funnel_dict["form_start"]
    purch = funnel_dict["purchase"]

    if sessions is not None:
        r_1_to_2 = safe_div(ac, sessions)
    else:
        ssu = funnel_dict.get("session_start_users")
        r_1_to_2 = safe_div(ac, ssu)

    return {
        "1_to_2": r_1_to_2,
        "2_to_3": safe_div(cal, ac),
        "3_to_4": safe_div(form, cal),
        "4_to_5": safe_div(purch, form),
        "cvr": safe_div(purch, sessions) if sessions else None,
    }


def fix_w14():
    with open("reports/2026-w14/data.json", "r") as f:
        data = json.load(f)

    total_sessions = BASELINE_CORRECTED["sessions"]

    # ── Fix baseline ──
    data["baseline"]["sessions"] = total_sessions
    data["baseline"]["purchases"] = BASELINE_CORRECTED["purchase"]
    data["baseline"]["cvr"] = safe_div(BASELINE_CORRECTED["purchase"], total_sessions)
    data["baseline"]["funnel"] = dict(BASELINE_CORRECTED)
    del data["baseline"]["funnel"]["sessions"]

    rates = calc_rates(BASELINE_CORRECTED)
    data["baseline"]["conversion_rates"]["1_to_2"] = rates["1_to_2"]
    data["baseline"]["conversion_rates"]["2_to_3"] = rates["2_to_3"]
    data["baseline"]["conversion_rates"]["3_to_4"] = rates["3_to_4"]
    data["baseline"]["conversion_rates"]["4_to_5"] = rates["4_to_5"]

    # ── Fix funnel_7d current_week ──
    data["funnel_7d"]["current_week"]["funnel"] = dict(CURRENT_WEEK_CORRECTED)
    cw_rates = {
        "1_to_2": safe_div(CURRENT_WEEK_CORRECTED["ac_page_reach_users"], CURRENT_WEEK_CORRECTED["session_start_users"]),
        "2_to_3": safe_div(CURRENT_WEEK_CORRECTED["calendar_view"], CURRENT_WEEK_CORRECTED["ac_page_reach_users"]),
        "3_to_4": safe_div(CURRENT_WEEK_CORRECTED["form_start"], CURRENT_WEEK_CORRECTED["calendar_view"]),
        "4_to_5": safe_div(CURRENT_WEEK_CORRECTED["purchase"], CURRENT_WEEK_CORRECTED["form_start"]),
    }
    data["funnel_7d"]["current_week"]["conversion_rates"] = cw_rates

    # ── Fix funnel_7d prev_week ──
    data["funnel_7d"]["prev_week"]["funnel"] = dict(PREV_WEEK_CORRECTED)
    pw_rates = {
        "1_to_2": safe_div(PREV_WEEK_CORRECTED["ac_page_reach_users"], PREV_WEEK_CORRECTED["session_start_users"]),
        "2_to_3": safe_div(PREV_WEEK_CORRECTED["calendar_view"], PREV_WEEK_CORRECTED["ac_page_reach_users"]),
        "3_to_4": safe_div(PREV_WEEK_CORRECTED["form_start"], PREV_WEEK_CORRECTED["calendar_view"]),
        "4_to_5": safe_div(PREV_WEEK_CORRECTED["purchase"], PREV_WEEK_CORRECTED["form_start"]),
    }
    data["funnel_7d"]["prev_week"]["conversion_rates"] = pw_rates

    # ── Fix wow_pp ──
    wow = {}
    for key in ["1_to_2", "2_to_3", "3_to_4", "4_to_5"]:
        wow[key] = round(cw_rates[key] - pw_rates[key], 6)
    data["funnel_7d"]["wow_pp"] = wow
    data["baseline"]["conversion_rates"]["wow_pp"] = dict(wow)

    # ── Fix channel segments ──
    for ch_name, ch_data in CHANNEL_CORRECTED.items():
        if ch_name in data["segments"]["channel"]:
            seg = data["segments"]["channel"][ch_name]
            seg["sessions"] = ch_data["sessions"]
            seg["share"] = safe_div(ch_data["sessions"], total_sessions)
            seg["purchases"] = ch_data["purchases"]
            seg["cvr"] = safe_div(ch_data["purchases"], ch_data["sessions"])
            seg["funnel"] = dict(ch_data["funnel"])
            r = calc_rates(ch_data["funnel"], ch_data["sessions"])
            seg["rates"] = r

    # ── Fix device segments ──
    for dev_name, dev_data in DEVICE_CORRECTED.items():
        if dev_name in data["segments"]["device"]:
            seg = data["segments"]["device"][dev_name]
            seg["sessions"] = dev_data["sessions"]
            seg["share"] = safe_div(dev_data["sessions"], total_sessions)
            seg["purchases"] = dev_data["purchases"]
            seg["cvr"] = safe_div(dev_data["purchases"], dev_data["sessions"])
            seg["funnel"] = dict(dev_data["funnel"])
            r = calc_rates(dev_data["funnel"], dev_data["sessions"])
            seg["rates"] = r

    # ── Fix new/returning segments ──
    for nr_name, nr_data in NEW_RETURNING_CORRECTED.items():
        if nr_name in data["segments"]["new_returning"]:
            seg = data["segments"]["new_returning"][nr_name]
            seg["sessions"] = nr_data["sessions"]
            seg["share"] = safe_div(nr_data["sessions"], total_sessions)
            seg["purchases"] = nr_data["purchases"]
            seg["cvr"] = safe_div(nr_data["purchases"], nr_data["sessions"])
            seg["funnel"] = dict(nr_data["funnel"])
            r = calc_rates(nr_data["funnel"], nr_data["sessions"])
            seg["rates"] = r

    # ── Fix channel_device segments ──
    for cd_key, cd_data in CHANNEL_DEVICE_CORRECTED.items():
        if cd_key in data["segments"]["channel_device"]:
            seg = data["segments"]["channel_device"][cd_key]
            seg["sessions"] = cd_data["sessions"]
            seg["purchases"] = cd_data["purchases"]
            seg["cvr"] = safe_div(cd_data["purchases"], cd_data["sessions"])
            seg["share"] = safe_div(cd_data["sessions"], total_sessions)

    # ── Add fix note ──
    data["meta"]["fix_note"] = (
        "2026-04-15: Funnel metrics corrected from eventCount/sessions to activeUsers "
        "(purchase uses transactions). Original W14 data used mixed metrics."
    )

    with open("reports/2026-w14/data.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ W14 data.json fixed")
    print(f"  baseline 2→3: {data['baseline']['conversion_rates']['2_to_3']}")
    print(f"  7d current 2→3: {cw_rates['2_to_3']}")
    print(f"  7d prev 2→3: {pw_rates['2_to_3']}")
    print(f"  wow_pp 2→3: {wow['2_to_3']}")

    return cw_rates  # Return for W15 prev_week fix


def fix_w15(w14_cw_rates):
    with open("reports/2026-w15/data.json", "r") as f:
        data = json.load(f)

    # ── Fix prev_week (= W14 current_week) ──
    data["funnel_7d"]["prev_week"]["funnel"] = dict(CURRENT_WEEK_CORRECTED)
    data["funnel_7d"]["prev_week"]["conversion_rates"] = dict(w14_cw_rates)

    # ── Recalculate wow_pp ──
    cw_rates = data["funnel_7d"]["current_week"]["conversion_rates"]
    wow = {}
    for key in ["1_to_2", "2_to_3", "3_to_4", "4_to_5"]:
        wow[key] = round(cw_rates[key] - w14_cw_rates[key], 6)
    data["funnel_7d"]["wow_pp"] = wow

    # ── Fix baseline wow_pp (W15 28d rates vs W14 28d corrected rates) ──
    w14_baseline_rates = {
        "1_to_2": safe_div(BASELINE_CORRECTED["ac_page_reach_users"], BASELINE_CORRECTED["session_start_users"]),
        "2_to_3": safe_div(BASELINE_CORRECTED["calendar_view"], BASELINE_CORRECTED["ac_page_reach_users"]),
        "3_to_4": safe_div(BASELINE_CORRECTED["form_start"], BASELINE_CORRECTED["calendar_view"]),
        "4_to_5": safe_div(BASELINE_CORRECTED["purchase"], BASELINE_CORRECTED["form_start"]),
    }
    w15_rates = data["baseline"]["conversion_rates"]
    baseline_wow = {}
    for key in ["1_to_2", "2_to_3", "3_to_4", "4_to_5"]:
        baseline_wow[key] = round(w15_rates[key] - w14_baseline_rates[key], 6)
    data["baseline"]["conversion_rates"]["wow_pp"] = baseline_wow

    # ── Add fix note ──
    data["meta"]["fix_note"] = (
        "2026-04-15: prev_week and wow_pp corrected after W14 metric fix."
    )

    with open("reports/2026-w15/data.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ W15 data.json fixed")
    print(f"  baseline wow_pp 2→3: {baseline_wow['2_to_3']}")
    print(f"  7d wow_pp 2→3: {wow['2_to_3']}")
    print(f"  7d wow_pp all: {wow}")


if __name__ == "__main__":
    w14_cw_rates = fix_w14()
    fix_w15(w14_cw_rates)
