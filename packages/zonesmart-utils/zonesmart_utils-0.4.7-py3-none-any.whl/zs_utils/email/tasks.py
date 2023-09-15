from celery import current_app as app
from zs_utils.email.services import EmailService


@app.task()
def send_email_task(
    emails: list[str],
    subject: str,
    title: str,
    email_icon_path: str,
    body_content: str,
    **kwargs,
):
    return EmailService.send_standard_team_email(
        receivers=emails,
        subject=subject,
        title=title,
        email_icon_path=email_icon_path,
        body_content=body_content,
        **kwargs,
    )
