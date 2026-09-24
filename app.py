from flask import Flask, render_template, request, redirect, url_for, session
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
    get_supplier_risk_trend,
    get_supplier_trust_score
)
import re
import os


app = Flask(__name__)

# Used to keep the latest analysis result available after redirect.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "cyberguard-demo-secret"
)

initialize_database()


@app.route("/", methods=["GET", "POST"])
def home():

    # ---------------------------------------------------------
    # POST: ANALYZE PAYMENT REQUEST
    # ---------------------------------------------------------
    if request.method == "POST":

        print("FORM DATA:", request.form)

        message = request.form.get("message", "").strip()
        supplier_name = request.form.get("supplier", "").strip()

        # Get fresh dashboard data.
        stats = get_transaction_stats()
        all_recent_transactions = get_recent_transactions()
        recent_transactions = all_recent_transactions[:5]
        suppliers = get_all_suppliers()

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------
        if not message:
            return render_template(
                "index.html",
                result=None,
                suppliers=suppliers,
                selected_supplier=None,
                history=[],
                stats=stats,
                recent_transactions=recent_transactions,
                all_recent_transactions=all_recent_transactions,
                risk_trend=[],
                trust_score=None,
                error="Please enter a payment request to analyze."
            )

        if len(message) > 10000:
            return render_template(
                "index.html",
                result=None,
                suppliers=suppliers,
                selected_supplier=None,
                history=[],
                stats=stats,
                recent_transactions=recent_transactions,
                all_recent_transactions=all_recent_transactions,
                risk_trend=[],
                trust_score=None,
                error="The payment request is too long. Please provide a shorter message."
            )

        if not supplier_name:
            return render_template(
                "index.html",
                result=None,
                suppliers=suppliers,
                selected_supplier=None,
                history=[],
                stats=stats,
                recent_transactions=recent_transactions,
                all_recent_transactions=all_recent_transactions,
                risk_trend=[],
                trust_score=None,
                error="Please select a supplier."
            )

        supplier = get_supplier(supplier_name)

        if not supplier:
            return render_template(
                "index.html",
                result=None,
                suppliers=suppliers,
                selected_supplier=None,
                history=[],
                stats=stats,
                recent_transactions=recent_transactions,
                all_recent_transactions=all_recent_transactions,
                risk_trend=[],
                trust_score=None,
                error="The selected supplier could not be found."
            )

        # -----------------------------------------------------
        # SUPPLIER HISTORY
        # -----------------------------------------------------
        history = get_supplier_history(supplier["name"])

        # -----------------------------------------------------
        # DETERMINISTIC RISK ANALYSIS
        # -----------------------------------------------------
        try:
            score, risk_level, warnings, factors = analyze_transaction(
                message,
                supplier
            )

        except Exception as e:
            print("Risk engine error:", e)

            return render_template(
                "index.html",
                result=None,
                suppliers=suppliers,
                selected_supplier=supplier,
                history=history,
                stats=stats,
                recent_transactions=recent_transactions,
                all_recent_transactions=all_recent_transactions,
                risk_trend=[],
                trust_score=None,
                error="Security analysis could not be completed. Please try again."
            )

        # -----------------------------------------------------
        # BEHAVIOURAL ANALYSIS
        # -----------------------------------------------------
        try:
            pattern_result = analyze_pattern(
                message,
                history
            )

        except Exception as e:
            print("Pattern engine error:", e)

            pattern_result = {
                "deviation_score": 0,
                "warnings": [
                    "Behavioural analysis is currently unavailable."
                ],
                "deviations": []
            }

        # -----------------------------------------------------
        # GEMINI AI ANALYSIS
        # -----------------------------------------------------
        try:
            ai_result = analyze_with_ai(message)

        except Exception as e:
            print("AI engine error:", e)

            ai_result = {
                "assessment": "AI analysis unavailable.",
                "confidence": "UNAVAILABLE",
                "threat_type": "UNAVAILABLE",
                "indicators": [
                    "AI analysis could not be completed."
                ]
            }

        # -----------------------------------------------------
        # EXTRACT REQUESTED ACCOUNT
        # -----------------------------------------------------
        account_match = re.search(
            r"(?:account|account number|a/c)\s*(?:is|:)?\s*(\d{4,})",
            message.lower()
        )

        requested_account = None

        if account_match:
            requested_account = account_match.group(1)[-4:]

        # -----------------------------------------------------
        # IMPORTANT:
        # Gemini and behavioural analysis DO NOT INCREASE
        # THE DETERMINISTIC RISK SCORE.
        # -----------------------------------------------------
        pattern_score = pattern_result["deviation_score"]

        combined_score = score

        if combined_score >= 80:
            final_risk_level = "CRITICAL"

        elif combined_score >= 60:
            final_risk_level = "HIGH"

        elif combined_score >= 30:
            final_risk_level = "MEDIUM"

        else:
            final_risk_level = "LOW"

        # -----------------------------------------------------
        # COMBINE WARNINGS / FACTORS
        # -----------------------------------------------------
        all_warnings = warnings + pattern_result["warnings"]
        all_factors = factors.copy()

        # -----------------------------------------------------
        # SAVE EXACTLY ONE TRANSACTION
        # -----------------------------------------------------
        save_transaction(
            supplier["name"],
            message,
            combined_score,
            final_risk_level,
            requested_account,
            "LIVE"
        )

        # -----------------------------------------------------
        # REFRESH SUPPLIER DATA AFTER SAVING
        # -----------------------------------------------------
        risk_trend = get_supplier_risk_trend(
            supplier["name"]
        )

        trust_score = get_supplier_trust_score(
            supplier["name"]
        )

        # -----------------------------------------------------
        # BUILD RESULT
        # -----------------------------------------------------
        result = {
            "score": combined_score,
            "risk_level": final_risk_level,
            "warnings": all_warnings,
            "factors": all_factors,
            "requested_account": requested_account,

            "pattern_score": pattern_score,
            "pattern_warnings": pattern_result["warnings"],
            "pattern_deviations": pattern_result["deviations"],

            "ai_assessment": ai_result["assessment"],
            "ai_confidence": ai_result["confidence"],
            "ai_threat_type": ai_result["threat_type"],
            "ai_indicators": ai_result["indicators"]
        }

        # -----------------------------------------------------
        # STORE RESULT IN SESSION
        #
        # This allows us to redirect to GET without losing
        # the analysis currently displayed on the dashboard.
        # -----------------------------------------------------
        session["analysis_result"] = result
        session["selected_supplier"] = supplier["name"]

        # -----------------------------------------------------
        # POST → REDIRECT → GET
        #
        # THIS IS THE ACTUAL REFRESH BUG FIX.
        # -----------------------------------------------------
        return redirect(url_for("home"))

    # =========================================================
    # GET: DISPLAY DASHBOARD
    # =========================================================

    stats = get_transaction_stats()

    all_recent_transactions = get_recent_transactions()

    recent_transactions = all_recent_transactions[:5]

    suppliers = get_all_suppliers()

    result = session.get("analysis_result")

    selected_supplier = None
    history = []
    risk_trend = []
    trust_score = None

    # ---------------------------------------------------------
    # RESTORE THE LAST ANALYSIS
    # ---------------------------------------------------------
    selected_supplier_name = session.get(
        "selected_supplier"
    )

    if selected_supplier_name:

        selected_supplier = get_supplier(
            selected_supplier_name
        )

        if selected_supplier:

            history = get_supplier_history(
                selected_supplier["name"]
            )

            risk_trend = get_supplier_risk_trend(
                selected_supplier["name"]
            )

            trust_score = get_supplier_trust_score(
                selected_supplier["name"]
            )

    # ---------------------------------------------------------
    # DISPLAY DASHBOARD
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
        risk_trend=risk_trend,
        trust_score=trust_score
    )


if __name__ == "__main__":
    app.run(debug=True)