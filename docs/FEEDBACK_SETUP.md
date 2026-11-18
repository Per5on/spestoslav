# Private feedback delivery

Selected route: Brevo transactional email over HTTPS443. Official API: https://developers.brevo.com/reference/sendtransacemail (POST https://api.brevo.com/v3/smtp/email,201with messageId). Free tier is listed at https://www.brevo.com/pricing/; provider limits/account activation still apply. No paid hosting change is needed. Yahoo SMTP465/587 cannot work on Render Free (https://render.com/docs/free.md); its optional adapter remains for a separately approved SMTP-capable environment.

Owner must create the free Brevo account, verify the sender they own, and privately configure `FEEDBACK_BREVO_API_KEY` in the API service's Render Environment. Do not paste an API key, Yahoo app password or other credentials in chat, source, CI logs or APK configuration. `FEEDBACK_FROM` is the verified sender; the user-entered contact email is Reply-To, never From. Recipient is fixed server-side to ivo77@duck.com; request bodies cannot override it. Name/optional phone/email/message are sent only to the configured provider over verified HTTPS, as plain text, with no CAPTCHA or attachments. No feedback body/key is logged or saved in a public cache.

Configuration: `FEEDBACK_PROVIDER=brevo`; `FEEDBACK_DELIVERY_ENABLED=false` until account/sender/key are ready for a controlled test. Required secrets: FEEDBACK_BREVO_API_KEY and FEEDBACK_FROM. Enable delivery only after confirming configuration, then verify one explicit synthetic support message with the recipient.201/messageId establishes provider acceptance, not inbox delivery. Failure, malformed acknowledgement, timeout or missing credentials never returns a success claim; UI shows unavailable/generic failure and does not automatically replay writes. Per-preview quota remains5attempts/10minutes.

Owner confirmed account/key setup is not yet complete. Keep unavailable state honest and continue independent readiness work. Before GooglePlay testing, finalize processor/retention/operator details in the Terms/Privacy draft and actual delivery evidence. Never describe the app as fully live before these gates pass.

## Pre-alpha integration result — 18 November 2026

The app form submitted one synthetic message through the actual feedback API to a local SMTP receiver. The receiver verified authenticated STARTTLS, fixed recipient, supplied Reply-To and matching message body. The API returned 202 and the app displayed the acceptance message. The local receiver did not forward mail. The live availability endpoint still returns false. Use the existing Brevo HTTPS configuration with a verified sender and private Render key for the live inbox test.

For each submission the user-entered address supplies Reply-To and the Brevo-verified address supplies From. All messages go to ivo77@duck.com. A two-user regression confirms the recipient stays fixed while Reply-To changes.
