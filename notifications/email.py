from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="sriharankiaq@gmail.com",
    MAIL_PASSWORD="hhiy tpbk puca lwky",
    MAIL_FROM="sriharankiaq@gmail.com",
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

fm = FastMail(conf)
async def send_order_email(data):
    message = MessageSchema(
        subject="Order Created",
        recipients=[data["email"]],
        body=f"""
Hello {data['name']},

Your order #{data['order_id']} has been placed successfully.

Amount: {data['total']}

Thank you.
""",
        subtype="plain",
    )

    await fm.send_message(message)