# Sky IP Checker — Backend + Website

This is the complete FastAPI application. It serves the website and its API from the same host.
Do **not** deploy this as a GitHub Pages-only site: GitHub Pages cannot run Python.

## Deploy on Render

1. Upload the contents of this folder to the root of a GitHub repository (the `main.py` file and `static` folder must be at repository root).
2. In Render, choose **New → Blueprint** or **New → Web Service**, then connect that GitHub repository.
3. If using Web Service manually:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. In Render → your service → Environment, add:
   - Key: `SKY_API_KEY`
   - Value: create your own long, private password (do not reuse a GitHub password).
5. Deploy, wait until the service is Live, then open its `https://....onrender.com` URL on your phone.
6. Enter the same `SKY_API_KEY` value in the website's Personal Access Key field.

## Important notes

- The website and API are served by the same Python service. The GitHub Pages URL is not the working app URL.
- Supports HTTP, HTTPS destination checks through HTTP CONNECT proxies, SOCKS4 and SOCKS5.
- Up to 1,000 proxies can be submitted per batch; start with a small batch and low concurrency (5–10). Free hosting may throttle or suspend high-volume proxy traffic and may not reliably handle 1,000 checks.
- Free services can sleep when idle; the first request may take time to wake up. Free-host limits can change.
- Job data is held in memory and may disappear if the service restarts. Working proxies are saved in the browser on that device.
- A proxy marked dead failed this particular HTTPS test within the timeout; it may still work for another destination.
- Only test proxies you are authorized to use. Avoid sharing proxy credentials or your API key.
