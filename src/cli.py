from src.database import initialize_database
from src.seed_data import seed_roles_and_permissions
from src.access_certification import generate_access_review, get_pending_access_reviews, review_access, get_pending_review_by_id, get_access_review_summary
from src.audit_reporting import get_audit_logs


def display_menu():
    print("\n========== NEXORA IAM GOVERNANCE ==========")
    print("1. Generate access reviews")
    print("2. View pending access reviews")
    print("3. Approve / Revoke access")
    print("4. View access review summary")
    print("5. View audit logs")
    print("0. Exit")
    print("===========================================")


def main():
    initialize_database()
    seed_roles_and_permissions()

    while True:
        display_menu()
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Exiting IAM Governance CLI.")
            break
        elif choice == "1":
            review_period = input(
                "Enter review period (e.g. 2026-Q4): "
            ).strip()

            if not review_period:
                print("Review period cannot be empty.")
                continue

            generate_access_review(review_period)
        elif choice == "2":
            review_period = input(
                "Enter review period (e.g. 2026-Q4): "
            ).strip()

            if not review_period:
                print("Review period cannot be empty.")
                continue

            pending_reviews = get_pending_access_reviews(review_period)

            if not pending_reviews:
                print("No pending access reviews found.")
                continue

            print(f"\nPending Access Reviews: {review_period}")
            print("-" * 75)

            for review in pending_reviews:
                print(
                    f"Review ID: {review['review_id']} | "
                    f"Employee: {review['full_name']} | "
                    f"Department: {review['department']} | "
                    f"Role: {review['role_name']}"
                )

            print("-" * 75)
            print(f"Total pending reviews: {len(pending_reviews)}")
        elif choice == "3":
            review_period = input(
                "Enter review period (e.g. 2026-Q4): "
            ).strip()

            pending_reviews = get_pending_access_reviews(review_period)

            if not pending_reviews:
                print("No pending reviews found.")
                continue

            print("\nSelect an employee to review:")
            print("-" * 70)

            for index, review in enumerate(pending_reviews, start=1):
                print(
                    f"{index}. {review['full_name']} | "
                    f"{review['employee_id']} | "
                    f"{review['department']} | "
                    f"{review['role_name']}"
                )

            try:
                selection = int(input("\nSelect employee number: ").strip())
            except ValueError:
                print("Invalid selection.")
                continue

            if selection < 1 or selection > len(pending_reviews):
                print("Selection out of range.")
                continue

            selected_review = pending_reviews[selection - 1]

            print("\nAccess Review Details")
            print("-" * 40)
            print(f"Employee: {selected_review['full_name']}")
            print(f"Employee ID: {selected_review['employee_id']}")
            print(f"Department: {selected_review['department']}")
            print(f"Role: {selected_review['role_name']}")

            decision = input(
                "\nDecision (approve/revoke): "
            ).strip().lower()

            decision_mapping = {
                "approve": "approved",
                "revoke": "revoked"
            }

            if decision not in decision_mapping:
                print("Invalid decision.")
                continue

            reviewer = input("Enter reviewer ID: ").strip()

            if not reviewer:
                print("Reviewer ID cannot be empty.")
                continue

            try:
                review_access(
                    review_id=selected_review["review_id"],
                    decision=decision_mapping[decision],
                    reviewer=reviewer
                )
                print(
                    f"Successfully processed access review for "
                    f"{selected_review['full_name']}."
                )
            except ValueError as error:
                print(f"Unable to process review: {error}")
        elif choice == "4":
            review_period = input(
                "Enter review period (e.g. 2026-Q4): "
            ).strip()

            if not review_period:
                print("Review period cannot be empty.")
                continue

            summary = get_access_review_summary(review_period)

            print(f"\nAccess Review Summary: {review_period}")
            print("-" * 40)
            print(f"Total Reviews : {summary['total_reviews']}")
            print(f"Approved      : {summary['approved']}")
            print(f"Revoked       : {summary['revoked']}")
            print(f"Pending       : {summary['pending']}")
            print("-" * 40)     
        elif choice == "5":
            try:
                limit = int(input("Number of audit records to display (default 50): ").strip() or "50")
                logs = get_audit_logs(limit)

                if not logs:
                    print("No audit records found.")
                    continue

                print("\nIAM Audit Logs")
                print("=" * 90)

                for log in logs:
                    print(f"Audit ID   : {log['audit_id']}")
                    print(f"Actor      : {log['actor']}")
                    print(f"Event      : {log['event_type']}")
                    print(f"Outcome    : {log['outcome']}")
                    print(f"Employee   : {log['full_name'] or 'N/A'}")
                    print(f"Department : {log['department'] or 'N/A'}")
                    print(f"Details    : {log['event_details']}")
                    print(f"Timestamp  : {log['event_timestamp']}")
                    print("-" * 90)

            except ValueError as error:
                print(f"Invalid input: {error}")
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
