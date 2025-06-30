def send_email_for_verification(to_email: str, verify_link: str):
    print("Sending email:")
    print(f"For: {to_email}")
    print(f"Follow the link to confirm email: {verify_link}")
    return True if to_email and verify_link else False
