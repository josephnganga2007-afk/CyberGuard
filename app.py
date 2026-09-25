from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

import re
import inspect
import sqlite3
import logging

from risk_engine import analyze_transaction
from pattern_engine import analyze_pattern
from ai_engine import analyze_with_ai

from database import (
    initialize_database,
    get_supplier,
    get_all_suppliers,
    save_transaction,
    get_supplier_history,
    get_transaction_stats,
    get_recent_transactions,
    get_pending_investigations,
    review_investigation,
)

from email_connector import get_gmail_emails
from gmail_ingestion import ingest_email


# =============================================================
# APPLICATION CONFIGURATION
# =============================================================

app = Flask(__name__)

app.secret_key = "cyberguard-development-key"

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CyberGuard")

initialize_database()


# =============================================================
# DATABASE COMPATIBILITY HELPERS
# =============================================================

def database_function(name):
    """
    Return a database function if it exists.

    This allows the dashboard to remain compatible with the
    database functions implemented in the existing project.
    """
    import database

    return getattr(database, name, None)


def call_if_available(name, *args, **kwargs):
    """
    Call an optional database helper safely.
    """
    function = database_function(name)

    if function is None:
        return None

    try:
        return function(*args, **kwargs)

    except Exception:
        logger.exception(
            "Database helper failed: %s",
            name
        )

        return None


def get_row_value(row, key, default=None):
    """
    Read a field from a sqlite3.Row, dictionary, or object.
    """
    if row is None:
        return default

    try:
        if isinstance(row, dict):
            return row.get(key, default)

        return row[key]

    except (KeyError, IndexError, TypeError):
        return getattr(row, key, default)


def row_to_dict(row):
    """
    Convert a database row into a dictionary.
    """
    if row is None:
        return {}

    if isinstance(row, dict):
        return dict(row)

    try:
        return dict(row)

    except (TypeError, ValueError):
        return {}


# =============================================================
# BUSINESS CONTEXT
# =============================================================

def get_business_from_session():
    """
    Resolve the active business using the business ID saved
    in the Flask session.

    The dashboard defaults to the existing demo business
    when a business has not yet been selected.
    """

    business_id = session.get("business_id")

    if business_id is not None:

        try:
            business_id = int(business_id)

        except (ValueError, TypeError):
            business_id = None

    if business_id is not None:

        business = call_if_available(
            "get_business_by_id",
            business_id
        )

        if business:
            return business

    # Use the existing demo business if available.
    business = call_if_available(
        "get_business_by_id",
        1
    )

    if business:
        session["business_id"] = 1
        return business

    return None


def get_active_business_id():
    """
    Return the business ID for the current session.
    """
    business = get_business_from_session()

    if business is None:
        return None

    value = get_row_value(
        business,
        "id"
    )

    try:
        return int(value)

    except (ValueError, TypeError):
        return None


def get_business_gmail(business):
    """
    Retrieve the Gmail address associated with the business.
    """
    if business is None:
        return None

    return (
        get_row_value(
            business,
            "gmail_account"
        )
        or get_row_value(
            business,
            "email"
        )
    )


def get_business_suppliers_safe(business_id):
    """
    Retrieve only suppliers linked to the active business.
    """
    if business_id is None:
        return []

    suppliers = call_if_available(
        "get_business_suppliers",
        business_id
    )

    if suppliers is None:
        return []

    return list(suppliers)


def get_business_transactions_safe(business_id):
    """
    Retrieve business-owned transactions only.
    """
    if business_id is None:
        return []

    transactions = call_if_available(
        "get_business_transactions",
        business_id
    )

    if transactions is None:
        return []

    return list(transactions)


def get_business_investigations_safe(business_id):
    """
    Retrieve investigations owned by the active business.
    """
    if business_id is None:
        return []

    investigations = call_if_available(
        "get_business_investigations",
        business_id
    )

    if investigations is None:
        return []

    return list(investigations)


# =============================================================
# BUSINESS DASHBOARD SUMMARY
# =============================================================

def empty_summary():
    """
    Return an empty summary without inventing transaction data.
    """
    return {
        "payment_transactions": 0,
        "high_risk_transactions": 0,
        "critical_transactions": 0,
        "pending_investigations": 0,
        "reviewed_suspicious": 0,
        "reviewed_legitimate": 0,
        "linked_suppliers": 0,
        "latest_transaction": None,
    }


def get_business_summary_safe(business_id):
    """
    Retrieve the existing business security summary.

    This function deliberately does not fall back to global
    transaction statistics, since that would expose one
    business's activity to another business.
    """

    if business_id is None:
        return empty_summary()

    summary = call_if_available(
        "get_business_security_summary",
        business_id
    )

    if summary is None:
        return empty_summary()

    result = empty_summary()

    result.update(
        row_to_dict(summary)
    )

    return result


# =============================================================
# DASHBOARD DATA
# =============================================================

def get_dashboard_data(business):
    """
    Build the dashboard using business-owned records.

    Existing template variables are retained for compatibility.
    """

    business_id = None

    if business is not None:

        try:
            business_id = int(
                get_row_value(
                    business,
                    "id"
                )
            )

        except (ValueError, TypeError):
            business_id = None

    # ---------------------------------------------------------
    # Business-scoped dashboard data
    # ---------------------------------------------------------

    stats = get_business_summary_safe(
        business_id
    )

    business_transactions = (
        get_business_transactions_safe(
            business_id
        )
    )

    business_investigations = (
        get_business_investigations_safe(
            business_id
        )
    )

    business_suppliers = (
        get_business_suppliers_safe(
            business_id
        )
    )

    # ---------------------------------------------------------
    # Recent transactions
    # ---------------------------------------------------------

    all_recent_transactions = []

    for transaction in business_transactions:

        row = row_to_dict(
            transaction
        )

        all_recent_transactions.append(
            (
                row.get("supplier_name", "Unknown supplier"),
                row.get("risk_score", 0),
                row.get("risk_level", "LOW"),
                row.get("requested_account"),
                row.get("created_at"),
            )
        )

    recent_transactions = (
        all_recent_transactions[:5]
    )

    # ---------------------------------------------------------
    # Pending investigations
    # ---------------------------------------------------------

    pending_investigations = []

    for investigation in business_investigations:

        row = row_to_dict(
            investigation
        )

        status = str(
            row.get("status", "")
        ).upper()

        if status in (
            "PENDING",
            "OPEN",
            "UNDER_REVIEW",
        ):
            pending_investigations.append(
                investigation
            )

    # ---------------------------------------------------------
    # Supplier options
    # ---------------------------------------------------------

    suppliers = []

    for supplier in business_suppliers:

        row = row_to_dict(
            supplier
        )

        supplier_id = row.get("id")
        supplier_name = row.get("name", "")

        suppliers.append(
            (
                supplier_id,
                supplier_name
            )
        )

    return {
        "stats": stats,
        "recent_transactions": recent_transactions,
        "all_recent_transactions": all_recent_transactions,
        "pending_investigations": pending_investigations,
        "suppliers": suppliers,
    }


# =============================================================
# RISK LEVEL
# =============================================================

def determine_risk_level(score):
    """
    Deterministic risk thresholds.
    """

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 30:
        return "MEDIUM"

    return "LOW"


# =============================================================
# ACCOUNT EXTRACTION
# =============================================================

def extract_requested_account(message):
    """
    Extract the last four digits of a requested account number.
    """

    if not message:
        return None

    patterns = [
        r"(?:account number|account|a/c)"
        r"\s*(?:is|:|number)?\s*(\d{4,})",

        r"(?:banking details|bank account)"
        r"\s*(?:are|is|:)?\s*(\d{4,})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:
            return match.group(1)[-4:]

    return None


# =============================================================
# HOME / DASHBOARD
# =============================================================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    selected_supplier = None
    history = []

    business = get_business_from_session()

    business_id = get_active_business_id()

    dashboard = get_dashboard_data(
        business
    )

    stats = dashboard["stats"]

    recent_transactions = (
        dashboard["recent_transactions"]
    )

    all_recent_transactions = (
        dashboard["all_recent_transactions"]
    )

    pending_investigations = (
        dashboard["pending_investigations"]
    )

    suppliers = dashboard["suppliers"]

    # ---------------------------------------------------------
    # Manual transaction analysis
    # ---------------------------------------------------------

    if request.method == "POST":

        message = request.form.get(
            "message",
            ""
        ).strip()

        supplier_name = request.form.get(
            "supplier",
            ""
        ).strip()

        if not message:

            session["investigation_message"] = (
                "Please provide a payment request to analyse."
            )

            return redirect(
                url_for("home")
            )

        if not supplier_name:

            session["investigation_message"] = (
                "Please select a supplier."
            )

            return redirect(
                url_for("home")
            )

        if business_id is None:

            session["investigation_message"] = (
                "No active business is configured. "
                "Please configure a business before analysing "
                "payment requests."
            )

            return redirect(
                url_for("home")
            )

        # -----------------------------------------------------
        # Business-owned supplier lookup
        # -----------------------------------------------------

        business_suppliers = (
            get_business_suppliers_safe(
                business_id
            )
        )

        supplier = None

        for business_supplier in business_suppliers:

            name = get_row_value(
                business_supplier,
                "name"
            )

            if name == supplier_name:

                supplier = business_supplier
                break

        if supplier is None:

            session["investigation_message"] = (
                "This supplier is not linked to the active "
                "business. No transaction was saved."
            )

            return redirect(
                url_for("home")
            )

        # -----------------------------------------------------
        # Deterministic risk analysis
        # -----------------------------------------------------

        score, risk_level, warnings, factors = (
            analyze_transaction(
                message,
                supplier
            )
        )

        # Ensure the score is a valid integer.
        try:
            score = int(score)

        except (ValueError, TypeError):
            score = 0

        score = max(
            0,
            min(
                score,
                100
            )
        )

        final_risk_level = determine_risk_level(
            score
        )

        # -----------------------------------------------------
        # Supplier history
        # -----------------------------------------------------

        history = get_supplier_history(
            get_row_value(
                supplier,
                "name"
            )
        )

        # -----------------------------------------------------
        # Behavioural analysis
        # -----------------------------------------------------

        pattern_result = analyze_pattern(
            message,
            history
        )

        pattern_score = pattern_result.get(
            "deviation_score",
            0
        )

        pattern_warnings = pattern_result.get(
            "warnings",
            []
        )

        pattern_deviations = pattern_result.get(
            "deviations",
            []
        )

        # -----------------------------------------------------
        # AI contextual analysis
        # -----------------------------------------------------

        try:

            ai_result = analyze_with_ai(
                message
            )

        except Exception:

            logger.exception(
                "AI analysis failed"
            )

            ai_result = {
                "assessment": "UNAVAILABLE",
                "confidence": 0,
                "threat_type": "UNAVAILABLE",
                "indicators": [],
            }

        # -----------------------------------------------------
        # IMPORTANT SCORING INVARIANT
        # -----------------------------------------------------
        #
        # The deterministic score remains authoritative.
        #
        # Pattern analysis and AI analysis are separate
        # intelligence layers and cannot inflate or reduce
        # the deterministic transaction score.
        # -----------------------------------------------------

        combined_score = score

        final_risk_level = determine_risk_level(
            combined_score
        )

        # -----------------------------------------------------
        # Warnings and factors
        # -----------------------------------------------------

        all_warnings = list(
            warnings or []
        )

        all_warnings.extend(
            pattern_warnings or []
        )

        all_factors = list(
            factors or []
        )

        # -----------------------------------------------------
        # Requested account
        # -----------------------------------------------------

        requested_account = (
            extract_requested_account(
                message
            )
        )

        # -----------------------------------------------------
        # Persist business-owned transaction
        # -----------------------------------------------------

        try:

            save_transaction(
                get_row_value(
                    supplier,
                    "name"
                ),
                message,
                combined_score,
                final_risk_level,
                requested_account,
                "LIVE",
                business_id=business_id,
            )

        except Exception:

            logger.exception(
                "Transaction persistence failed"
            )

            session["investigation_message"] = (
                "The transaction could not be saved. "
                "Please check the application logs."
            )

            return redirect(
                url_for("home")
            )

        # -----------------------------------------------------
        # Analysis result
        # -----------------------------------------------------

        result = {
            "score": combined_score,
            "risk_level": final_risk_level,
            "warnings": all_warnings,
            "factors": all_factors,
            "requested_account": requested_account,

            # Behavioural intelligence
            "pattern_score": pattern_score,
            "pattern_warnings": pattern_warnings,
            "pattern_deviations": pattern_deviations,

            # AI intelligence
            "ai_assessment": ai_result.get(
                "assessment",
                "UNAVAILABLE"
            ),

            "ai_confidence": ai_result.get(
                "confidence",
                0
            ),

            "ai_threat_type": ai_result.get(
                "threat_type",
                "UNAVAILABLE"
            ),

            "ai_indicators": ai_result.get(
                "indicators",
                []
            ),
        }

        selected_supplier = supplier

        # -----------------------------------------------------
        # Refresh business-scoped dashboard
        # -----------------------------------------------------

        dashboard = get_dashboard_data(
            business
        )

        stats = dashboard["stats"]

        recent_transactions = (
            dashboard["recent_transactions"]
        )

        all_recent_transactions = (
            dashboard["all_recent_transactions"]
        )

        pending_investigations = (
            dashboard["pending_investigations"]
        )

        suppliers = dashboard["suppliers"]

    # ---------------------------------------------------------
    # Render dashboard
    # ---------------------------------------------------------

    return render_template(
        "index.html",

        result=result,

        suppliers=suppliers,

        selected_supplier=selected_supplier,

        history=history,

        stats=stats,

        recent_transactions=recent_transactions,

        all_recent_transactions=all_recent_transactions,

        pending_investigations=pending_investigations,

        business=business,
        business_id=business_id,
        business_security=get_business_summary_safe(business_id),

        gmail_scan=session.pop(
            "gmail_scan",
            None
        ),

        investigation_message=session.pop(
            "investigation_message",
            None
        ),
    )


# =============================================================
# GMAIL SECURITY SCANNER
# =============================================================

@app.route("/scan-gmail", methods=["POST"])
def scan_gmail():

    business = get_business_from_session()

    business_id = get_active_business_id()

    if business is None or business_id is None:

        session["gmail_scan"] = {
            "scanned": 0,
            "saved": 0,
            "skipped": 0,
            "stopped": 0,
            "held": 0,
            "already_held": 0,
            "errors": 1,
            "results": [],
            "error": (
                "No active business is configured."
            ),
        }

        return redirect(
            url_for("home")
        )

    try:

        emails = get_gmail_emails(
            max_results=10
        )

        saved = 0
        skipped = 0
        stopped = 0
        held = 0
        already_held = 0
        errors = 0

        results = []

        for email in emails:

            try:

                # -------------------------------------------------
                # Preserve existing ingestion pipeline.
                #
                # The ingestion pipeline handles triage,
                # duplicate detection, risk analysis and
                # investigation creation.
                # -------------------------------------------------

                ingestion_result = ingest_email(
                email,
                business_id=business_id,
                )

                status = ingestion_result.get(
                    "status",
                    "ERROR"
                )

                if status == "SAVED":
                    saved += 1

                elif status == "SKIPPED":
                    skipped += 1

                elif status == "STOPPED":
                    stopped += 1

                elif status == "HELD":
                    held += 1

                elif status == "ALREADY_HELD":
                    already_held += 1

                else:
                    errors += 1

                results.append({
                    "sender": email.get(
                        "sender",
                        ""
                    ),

                    "subject": email.get(
                        "subject",
                        ""
                    ),

                    "status": status,

                    "reason": ingestion_result.get(
                        "reason",
                        ""
                    ),

                    "gmail_message_id": (
                        ingestion_result.get(
                            "gmail_message_id"
                        )
                    ),
                })

            except Exception as email_error:

                logger.exception(
                    "Email ingestion failed"
                )

                errors += 1

                results.append({
                    "sender": email.get(
                        "sender",
                        ""
                    ),

                    "subject": email.get(
                        "subject",
                        ""
                    ),

                    "status": "ERROR",

                    "reason": str(
                        email_error
                    ),

                    "gmail_message_id": email.get(
                        "id"
                    ),
                })

        session["gmail_scan"] = {
            "scanned": len(emails),
            "saved": saved,
            "skipped": skipped,
            "stopped": stopped,
            "held": held,
            "already_held": already_held,
            "errors": errors,
            "results": results,
        }

    except Exception as error:

        logger.exception(
            "Gmail scan failed"
        )

        session["gmail_scan"] = {
            "scanned": 0,
            "saved": 0,
            "skipped": 0,
            "stopped": 0,
            "held": 0,
            "already_held": 0,
            "errors": 1,
            "results": [],
            "error": str(error),
        }

    return redirect(
        url_for("home")
    )


# =============================================================
# HUMAN INVESTIGATION REVIEW
# =============================================================

@app.route(
    "/review-investigation",
    methods=["POST"]
)
def review_investigation_route():

    investigation_id = request.form.get(
        "investigation_id"
    )

    decision = request.form.get(
        "decision",
        ""
    ).upper().strip()

    reviewer_notes = request.form.get(
        "reviewer_notes",
        ""
    ).strip()

    business_id = get_active_business_id()

    # ---------------------------------------------------------
    # Validate investigation ID
    # ---------------------------------------------------------

    if not investigation_id:

        session["investigation_message"] = (
            "Investigation ID was not provided."
        )

        return redirect(
            url_for("home")
        )

    try:

        investigation_id = int(
            investigation_id
        )

    except (ValueError, TypeError):

        session["investigation_message"] = (
            "Invalid investigation ID."
        )

        return redirect(
            url_for("home")
        )

    # ---------------------------------------------------------
    # Validate decision
    # ---------------------------------------------------------

    allowed_decisions = {
        "APPROVED",
        "REJECTED",
        "ESCALATED",
    }

    if decision not in allowed_decisions:

        session["investigation_message"] = (
            "Invalid investigation decision."
        )

        return redirect(
            url_for("home")
        )

    # ---------------------------------------------------------
    # Verify business ownership
    # ---------------------------------------------------------

    if business_id is None:

        session["investigation_message"] = (
            "No active business is configured."
        )

        return redirect(
            url_for("home")
        )

    investigations = (
        get_business_investigations_safe(
            business_id
        )
    )

    investigation_exists = False

    for investigation in investigations:

        current_id = get_row_value(
            investigation,
            "id"
        )

        try:

            if int(current_id) == investigation_id:

                investigation_exists = True
                break

        except (ValueError, TypeError):
            continue

    if not investigation_exists:

        session["investigation_message"] = (
            "This investigation does not belong to "
            "the active business or could not be found."
        )

        return redirect(
            url_for("home")
        )

    # ---------------------------------------------------------
    # Save review decision
    # ---------------------------------------------------------

    try:

        success = review_investigation(
            investigation_id,
            decision,
            reviewer_notes
        )

        if success:

            session["investigation_message"] = (
                f"Investigation marked as {decision}."
            )

        else:

            session["investigation_message"] = (
                "Investigation could not be updated. "
                "It may already have been reviewed."
            )

    except Exception:

        logger.exception(
            "Investigation review failed"
        )

        session["investigation_message"] = (
            "The investigation review failed. "
            "Please check the application logs."
        )

    return redirect(
        url_for("home")
    )


# =============================================================
# HEALTH CHECK
# =============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return {
        "application": "CyberGuard",
        "version": "14.0 FINAL",
        "status": "running",
    }, 200


# =============================================================
# APPLICATION START
# =============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )