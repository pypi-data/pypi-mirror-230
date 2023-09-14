main.py
```python
import datetime
import os
from py_secure_edge import custom_token


def get_timedelta(str_val = ''):
    if str_val.endswith("m"):
        return datetime.timedelta(minutes=int(str_val[0:-1]))
    if str_val.endswith("h"):
        return datetime.timedelta(hours=int(str_val[0:-1]))
    if str_val.endswith("d"):
        return datetime.timedelta(days=int(str_val[0:-1]))
    return int(str_val)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url = os.environ["URL"]
    key = os.environ["KEY"]
    key_id = os.environ["KEY_ID"]
    exp = os.environ.get("EXP", "24h")
    firstExp = os.environ.get("FIRST_EXP", "5m")
    country = os.environ.get("CO", "")
    region = os.environ.get("REG", "")
    no_session = os.environ.get("NO_SSN", False)
    user_agent = os.environ.get("UA", "")
    referer = os.environ.get("REF", "")

    token_policy = custom_token.TokenPolicy()
    token_policy.expiry = get_timedelta(exp)
    token_policy.first_access_expiry = get_timedelta(firstExp)
    token_policy.session = not no_session
    token_policy.country = len(country) > 0
    token_policy.region = len(region) > 0
    token_policy.headers = []
    if len(user_agent) > 0:
        token_policy.headers.append("user-agent")
    if len(referer) > 0:
        token_policy.headers.append("referer")

    viewer_attrs = custom_token.ViewerAttributes()
    viewer_attrs.country = country
    viewer_attrs.region = region
    viewer_attrs.headers = {
        "user-agent": user_agent,
        "referer": referer,
    }

    custom_token = custom_token.CustomToken(secrets={key_id: key})

    url_with_token = custom_token.generate_url(url, key_id, token_policy, viewer_attrs)
    print(url_with_token)
```

```bash
URL=https://your-media-endpoint.com/master.m3u8 \
  KEY_ID=your-key-id KEY=your-key \
  UA="your-user-agent" \
  REF=your-referrer \
  python3 main.py
```