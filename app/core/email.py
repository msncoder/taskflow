"""Email utility for sending invitation emails via SMTP."""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_invitation_email(to_email: str, invite_link: str, inviter_name: str) -> None:
    """
    Send an invitation email to a user.

    This is designed to be run as a background task via FastAPI's BackgroundTasks.

    Args:
        to_email: Recipient email address
        invite_link: Full URL to the accept-invite page with token
        inviter_name: Full name of the person who sent the invitation
    """
    subject = f"You've been invited to join TaskFlow"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
    <body style="margin:0;padding:0;background-color:#09090b;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090b;padding:40px 16px;">
        <tr>
          <td align="center">
            <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

              <!-- Logo / Header -->
              <tr>
                <td align="center" style="padding-bottom:32px;">
                  <table cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="background-color:#6366f1;border-radius:10px;width:40px;height:40px;text-align:center;vertical-align:middle;">
                        <span style="color:#ffffff;font-size:20px;font-weight:700;line-height:40px;">T</span>
                      </td>
                      <td style="padding-left:10px;">
                        <span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:-0.5px;">TaskFlow</span>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Card -->
              <tr>
                <td style="background-color:#18181b;border:1px solid #27272a;border-radius:16px;padding:40px 36px;">

                  <h1 style="margin:0 0 8px;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-0.3px;">
                    You've been invited 🎉
                  </h1>
                  <p style="margin:0 0 28px;color:#a1a1aa;font-size:15px;line-height:1.6;">
                    <strong style="color:#d4d4d8;">{inviter_name}</strong> has invited you to join their workspace on TaskFlow.
                    Click the button below to accept your invitation and set up your account.
                  </p>

                  <!-- CTA Button -->
                  <table cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="background-color:#6366f1;border-radius:8px;">
                        <a href="{invite_link}"
                           style="display:inline-block;padding:12px 28px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.1px;">
                          Accept Invitation →
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Divider -->
                  <hr style="border:none;border-top:1px solid #27272a;margin:0 0 24px;" />

                  <!-- Fallback link -->
                  <p style="margin:0;color:#71717a;font-size:13px;line-height:1.6;">
                    If the button doesn't work, copy and paste this link into your browser:
                  </p>
                  <p style="margin:8px 0 0;word-break:break-all;">
                    <a href="{invite_link}" style="color:#818cf8;font-size:13px;text-decoration:none;">{invite_link}</a>
                  </p>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td align="center" style="padding-top:24px;">
                  <p style="margin:0;color:#52525b;font-size:12px;">
                    This invitation was sent by TaskFlow. If you weren't expecting this, you can safely ignore it.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    plain_body = (
        f"You've been invited to join TaskFlow by {inviter_name}.\n\n"
        f"Accept your invitation here:\n{invite_link}\n\n"
        f"If you weren't expecting this, you can safely ignore this email."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"TaskFlow <{settings.smtp_from_email}>"
    msg["To"] = to_email

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())
        logger.info(f"Invitation email sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check SMTP_USER and SMTP_PASSWORD in .env")
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send invitation email to {to_email}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {e}")
