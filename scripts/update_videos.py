#!/usr/bin/env python3
"""YouTubeのRSSから最新動画(ショート除外)を取得し videos.json に書き出す。
GitHub Actionsから定期実行される。"""
import urllib.request, re, json, datetime

CHANNEL_ID = "UCbpOQIf2qrJkLlQui__sTQQ"
# タイトルに #Shorts が付いていないショートはここにIDを追加
SHORTS_IDS = {"jq_ZbMLyq2g"}
MAX_VIDEOS = 6

def main():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)

    def grab(pattern, text):
        m = re.search(pattern, text, re.S)
        return m.group(1) if m else ""

    def unescape(s):
        return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                 .replace("&#39;", "'").replace("&quot;", '"'))

    videos = []
    for e in entries:
        vid = grab(r"<yt:videoId>(.*?)</yt:videoId>", e)
        title = unescape(grab(r"<title>(.*?)</title>", e))
        pub = grab(r"<published>(.*?)</published>", e)
        if re.search("shorts", title, re.I):
            continue
        if vid in SHORTS_IDS:
            continue
        d = datetime.datetime.fromisoformat(pub.replace("Z", "+00:00"))
        videos.append({
            "videoId": vid,
            "title": title,
            "link": f"https://www.youtube.com/watch?v={vid}",
            "date": f"{d.year}年{d.month}月{d.day}日",
        })
        if len(videos) >= MAX_VIDEOS:
            break

    data = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "videos": videos,
    }
    with open("videos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"wrote {len(videos)} videos")

if __name__ == "__main__":
    main()
