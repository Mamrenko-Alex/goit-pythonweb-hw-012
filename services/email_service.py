def send_email_for_verification(to_email: str, verify_link: str):
    """Надсилає листа для підтвердження email користувача."""
    print("📧 Надсилаємо листа:")
    print(f"Кому: {to_email}")
    print(f"Перейдіть за посиланням для підтвердження email: {verify_link}")
