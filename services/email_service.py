def send_email_for_verification(to_email: str, verify_link: str):
    print("Sending email:")
    print(f"For: {to_email}")
    print(f"Follow the link to confirm email: {verify_link}")
    return True if to_email and verify_link else False


def send_password_reset_email(email: str, reset_link: str):
    # subject = "Скидання пароля"
    body = f"Натисніть на посилання для скидання пароля: {reset_link}"
    print(f"[DEBUG] Відправлено на {email}:\n{body}")
