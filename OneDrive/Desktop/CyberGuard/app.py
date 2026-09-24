from flask import Flask, render_template, request

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
    get_recent_transactions
)
import re


app = Flask(__name__)


# Make sure the database exists
initialize_database()


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    selected_supplier = None
    history = []

    stats = get_transaction_stats()
    all_recent_transactions = get_recent_transactions()
    recent_transactions = all_recent_transactions[:5]

    suppliers = get_all_suppliers()

    if request.method == "POST":

        print("FORM DATA:", request.form)

        message = request.form.get("message", "")
        supplier_name = request.form.get("supplier", "")

        if not message:
            return "ERROR: The message field was not received from the webpage."

        supplier = get_supplier(supplier_name)

        if not supplier:
            return "ERROR: Supplier was not found."

        # ---------------------------------
        # Traditional rule-based analysis
        # ---------------------------------

        score, risk_level, warnings, factors = analyze_transaction(
            message,
            supplier
        )

        # ---------------------------------
        # Get supplier history
        # ---------------------------------

        history = get_supplier_history(
            supplier["name"]
        )

        # ---------------------------------
        # Traditional pattern analysis
        # ---------------------------------

        pattern_result = analyze_pattern(
            message,
            history
        )
        # ---------------------------------
        # AI analysis
        # ---------------------------------

        ai_result = analyze_with_ai(message)
        # ---------------------------------
        # Extract requested account
        # ---------------------------------

        account_match = re.search(
            r"(?:account|account number|a/c)\s*(?:is|:)?\s*(\d{4,})",
            message.lower()
        )

        requested_account = None

        if account_match:
            requested_account = account_match.group(1)[-4:]

        # ---------------------------------
        # Add pattern score
        # ---------------------------------

        pattern_score = pattern_result["deviation_score"]

        combined_score = score
        

        # ---------------------------------
        # Determine final risk level
        # ---------------------------------

        if combined_score >= 80:
            final_risk_level = "CRITICAL"

        elif combined_score >= 60:
            final_risk_level = "HIGH"

        elif combined_score >= 30:
            final_risk_level = "MEDIUM"

        else:
            final_risk_level = "LOW"

        # ---------------------------------
        # Add pattern warnings
        # ---------------------------------

        all_warnings = (
            warnings +
            pattern_result["warnings"]
        )

        all_factors = factors.copy()

        

        # ---------------------------------
        # Save LIVE transaction
        # ---------------------------------

        save_transaction(
            supplier["name"],
            message,
            combined_score,
            final_risk_level,
            requested_account,
            "LIVE"
        )

        # ---------------------------------
        # Prepare result
        # ---------------------------------

        result = {
            "score": combined_score,
            "risk_level": final_risk_level,
            "warnings": all_warnings,
            "factors": all_factors,
            "requested_account": requested_account,

            # Pattern information
            "pattern_score": pattern_score,
            "pattern_warnings": pattern_result["warnings"],
            "pattern_deviations": pattern_result["deviations"],

                # AI information
                "ai_assessment": ai_result["assessment"],
                "ai_confidence": ai_result["confidence"],
                "ai_threat_type": ai_result["threat_type"],
                "ai_indicators": ai_result["indicators"]
        }

        selected_supplier = supplier

    return render_template(
    "index.html",
    result=result,
    suppliers=suppliers,
    selected_supplier=selected_supplier,
    history=history,
    stats=stats,
    recent_transactions=recent_transactions,
    all_recent_transactions=all_recent_transactions
)


if __name__ == "__main__":
    app.run(debug=True)