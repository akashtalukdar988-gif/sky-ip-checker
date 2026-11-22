# Sky IP Checker

Personal-use FastAPI + mobile web interface. Supports HTTP proxies, HTTPS destination checks through HTTP CONNECT proxies, SOCKS4 and SOCKS5 proxy checks by requesting `https://api.ipify.org?format=json` through each proxy.

## Important
- This is a starter project; it is not deployed yet.
- A cloud host gives the app a provider subdomain URL; you do not need to buy a domain.
- Render Free services sleep after 15 minutes idle and can take about a minute to wake. The free filesystem is ephemeral, so saved working proxies are stored in the user's browser localStorage, not on the server.
- Render says it may suspend free services that initiate unusually high volumes of public-internet traffic. Testing 1,000 proxies may hit resource/network limits; use low concurrency first and review host rules. Do not assume free hosting will reliably support repeated large batches.
- Jobs are held in memory and disappear if the server restarts. Run one batch at a time.
- A proxy marked dead means it failed this specific HTTPS test within the timeout; it may still work for another destination or protocol.
- Never paste proxy credentials into a public repository or share the URL/key. Set `SKY_API_KEY` as a secret environment variable.
- Only test proxies you are authorized to use.

## Run locally on Windows
1. Install Python 3.11+.
2. Open PowerShell in this folder.
3. Run: `py -m venv .venv`
4. Run: `.venv\\Scripts\\Activate.ps1`
5. Run: `pip install -r requirements.txt`
6. Run: `$env:SKY_API_KEY="choose-a-long-private-key"`
7. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
8. On the same Wi-Fi, open `http://WINDOWS-PC-LAN-IP:8000` on your phone.

## Deploy without buying a domain (Render)
1. Create a private GitHub repository and upload these project files.
2. Create a Render account and choose New -> Web Service, then connect the repository.
3. Use the build command `pip install -r requirements.txt` and start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Choose Free for a trial/personal test. Add an environment variable named `SKY_API_KEY` with a long random secret.
5. Deploy. Render provides a `*.onrender.com` URL; open it on your phone.
6. On Android Chrome, menu -> Add to Home screen if you want an icon.

Render Free limitations change. Confirm current plan limits before deploying or relying on it. For dependable 1,000-proxy batches, a small paid VPS may be necessary.
