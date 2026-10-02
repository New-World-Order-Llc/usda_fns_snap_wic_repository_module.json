def build_snap_application():
    return {
        "application_type": "SNAP Benefits Application",
        "version": "1.0",
        "timestamp": "",
        "applicant": {
            "first_name": "",
            "last_name": "",
            "date_of_birth": "",
            "ssn_last4": ""
        },
        "household": {
            "total_household_members": "",
            "household_member_details": []
        },
        "income": {
            "employment_status": "",
            "monthly_gross_income": ""
        },
        "expenses": {
            "rent_or_mortgage": "",
            "utilities": ""
        },
        "signature": {
            "applicant_signature": "",
            "signature_date": ""
        }
    }
