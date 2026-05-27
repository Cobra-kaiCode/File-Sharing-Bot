import html
from aiohttp import web
from database.database import db

routes = web.RouteTableDef()


def _html_page(title: str, body: str, redirect_path: str = None):
    """Small Telegram WebApp friendly page."""
    safe_title = html.escape(title)
    redirect_script = ""
    if redirect_path:
        safe_redirect = html.escape(redirect_path, quote=True)
        redirect_script = f"""
        <script>
          setTimeout(function() {{
            window.location.replace("{safe_redirect}");
          }}, 900);
        </script>
        """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <meta name="robots" content="noindex,nofollow">
  <title>{safe_title}</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif;
      background: #101010;
      color: #ffffff;
      padding: 22px;
    }}
    .card {{
      width: 100%;
      max-width: 420px;
      border-radius: 22px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.15);
      padding: 24px;
      text-align: center;
      box-shadow: 0 14px 40px rgba(0,0,0,0.35);
    }}
    .loader {{
      width: 46px;
      height: 46px;
      border: 4px solid rgba(255,255,255,0.22);
      border-top-color: #ffffff;
      border-radius: 50%;
      animation: spin .8s linear infinite;
      margin: 0 auto 18px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    h1 {{ font-size: 22px; margin: 0 0 12px; }}
    p {{ font-size: 15px; line-height: 1.5; opacity: .88; margin: 0; }}
    .credit {{ margin-top: 18px; font-size: 13px; opacity: .65; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="loader"></div>
    <h1>{safe_title}</h1>
    <p>{body}</p>
    <div class="credit">Powered by @BotWorld4U</div>
  </div>
  <script>
    try {{
      if (window.Telegram && window.Telegram.WebApp) {{
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
      }}
    }} catch (e) {{}}
  </script>
  {redirect_script}
</body>
</html>"""


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "ok", "credit": "@BotWorld4U", "bot": "FileStore Shortener", "gateway": "active"})


@routes.get("/health", allow_head=True)
async def health_route_handler(request):
    return web.json_response({"status": "ok"})


@routes.get("/v/{token}", allow_head=True)
async def verify_gateway_page(request):
    """Telegram Mini App page.

    It never shows the real shortener URL. It redirects to /r/<token>, and the
    server-side /r route redirects to the actual shortener link.
    """
    token = (request.match_info.get("token") or "").strip()
    if not token:
        return web.Response(
            text=_html_page("Invalid Link", "This verify link is invalid. Please open the file link again."),
            content_type="text/html"
        )

    data = await db.get_verify_token(token)
    if not data or not data.get("short_url"):
        return web.Response(
            text=_html_page("Link Expired", "This verify link expired. Please go back to Telegram and open the file link again."),
            content_type="text/html"
        )

    return web.Response(
        text=_html_page("Opening Verify Page", "Please wait. Your protected verification page is opening...", f"/r/{html.escape(token)}"),
        content_type="text/html"
    )


@routes.get("/r/{token}", allow_head=True)
async def verify_gateway_redirect(request):
    """Server-side redirect to real shortener URL.

    The real shortener URL is stored in MongoDB and is not placed in the
    Telegram button or visible HTML page.
    """
    token = (request.match_info.get("token") or "").strip()
    data = await db.get_verify_token(token)
    if not data or not data.get("short_url"):
        return web.Response(
            text=_html_page("Link Expired", "This verify link expired. Please open the file link again in Telegram."),
            content_type="text/html"
        )

    return web.HTTPFound(location=str(data.get("short_url")))
