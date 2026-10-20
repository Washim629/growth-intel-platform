# Growth & Lead Intelligence Platform

## Frontend and backend

The frontend calls the backend API using same-origin `/api` requests by
default. In Docker Compose, the frontend's Nginx server proxies those requests
to the `backend` service, so the browser does not need direct access to the
backend container.

Start the full stack from this directory:

```sh
docker compose up --build
```

Open the frontend at <http://localhost:8080>. The backend health endpoint and
interactive API documentation are available at <http://localhost:8000/api/health>
and <http://localhost:8000/docs>.

If the frontend is hosted separately from the backend, set `window.API_BASE`
before loading `assets/api.js` in `frontend/index.html`, for example:

```html
<script>window.API_BASE = "https://growth-intel-platform-1.onrender.com";</script>
```

The backend must allow the frontend's origin in its `CORS_ORIGINS` setting.

### Email one-time-code sign-in

The login page supports password sign-in and email one-time codes, and
creating a workspace requires email verification. Docker Compose defaults
to Gmail SMTP on port 587 using `growthanalyzer@gmail.com` as the sender.
For Gmail, create an app password for that account (Google requires
two-step verification) and set it as `SMTP_PASSWORD` in a local `.env` file.
Do not use your regular Gmail password or commit the app password.
For a different sender/provider, configure `SMTP_HOST`, `SMTP_PORT`,
`SMTP_FROM_EMAIL`, `SMTP_USERNAME`, and `SMTP_PASSWORD`.
`SMTP_USE_TLS` defaults to `true`; set it to `false` only when the SMTP
provider requires a non-STARTTLS connection. Codes expire after 10 minutes
and can be requested once per email every 60 seconds; override these defaults
with `LOGIN_OTP_EXPIRE_MINUTES` and `LOGIN_OTP_RESEND_SECONDS`.

When using Docker Compose, provide these as environment variables or in a
local `.env` file before starting the stack. Never commit SMTP credentials.
