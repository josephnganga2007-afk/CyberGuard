from email_connector import get_demo_emails
from triage_engine import triage_email


def print_result(email, result):
    print("=" * 60)
    print("FROM:", email["sender"])
    print("SUBJECT:", email["subject"])
    print()
    print("BODY:")
    print(email["body"])
    print()
    print("TRIAGE RESULT:")
    print("Category:", result["category"])
    print("Reason:", result["reason"])
    print("Signals:", result["signals"])
    print()


test_emails = get_demo_emails()

# Additional attack tests
test_emails.extend([
    {
        "sender": "hr@company.co.za",
        "subject": "Account manager meeting",
        "body": "Our account manager will join the meeting tomorrow."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Invoice 4582",
        "body": "Please find attached invoice 4582."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Payment request",
        "body": "Please make payment for the outstanding amount."
    },
    {
        "sender": "supplier@example.com",
        "subject": "New bank account",
        "body": "Please note that our banking details have changed."
    },
    {
        "sender": "marketing@example.com",
        "subject": "Payroll software promotion",
        "body": "Our payroll software can help your business."
    },
        {
        "sender": "supplier@example.com",
        "subject": "Updated beneficiary",
        "body": "Please use the new beneficiary details for the outstanding amount."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Outstanding balance",
        "body": "Kindly settle the outstanding balance on our account."
    },
    {
        "sender": "supplier@example.com",
        "subject": "EFT instructions",
        "body": "Please follow the attached EFT instructions."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Account representative",
        "body": "Our account representative will contact you regarding the contract."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Bank details",
        "body": "Please update your records with our new beneficiary bank details."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Funds transfer",
        "body": "Please transfer the funds to the account provided."
    },
        {
        "sender": "supplier@example.com",
        "subject": "URGENT: Supplier profile update",
        "body": "Please review our updated supplier profile when you have time."
    },
    {
        "sender": "security@example.com",
        "subject": "Banking fraud awareness webinar",
        "body": "Our banking partner is hosting a webinar about payment fraud prevention."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Invoice process update",
        "body": "Our invoice process has been improved. No action is required from your side."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Verify beneficiary",
        "body": "Please verify the beneficiary information before our scheduled payment."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Future payment banking change",
        "body": "We have changed our bank account. This change applies to future payments."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Payment fraud article",
        "body": "Please read our article explaining common payment fraud techniques."
    },
    {
        "sender": "supplier@example.com",
        "subject": "Account update",
        "body": "Please update our supplier account profile. No banking information has changed."
    },

])


for email in test_emails:
    result = triage_email(email)
    print_result(email, result)