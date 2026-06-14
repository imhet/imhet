from python_graphql_client import GraphqlClient
import feedparser
import pathlib
import re
import os
import datetime
import ssl
import random

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")

TOKEN = os.environ.get("GH_TOKEN", "")


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def format_date(timestamp):
    dateStr = datetime.datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S GMT') + datetime.timedelta(hours=8)
    return dateStr.date()


def make_ssl_unverify():
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    pass


def fetch_douban():
    try:
        feed = feedparser.parse("https://www.douban.com/feed/people/heyitao/interests")
        if feed.get("bozo_exception") or not feed.get("entries"):
            print(f"豆瓣 RSS 获取失败: {feed.get('bozo_exception', '无数据')}")
            return []
        return [
            {
                "action": item["title"][0:2],
                "title": item["title"][2:],
                "url": item["link"].split("#")[0],
                "published": format_date(item["published"])
            }
            for item in feed["entries"]
        ]
    except Exception as e:
        print(f"豆瓣数据获取异常: {e}")
        return []


def fetch_blog_entries():
    try:
        feed = feedparser.parse("https://heyitao.com/feed")
        if feed.get("bozo_exception") or not feed.get("entries"):
            print(f"博客 RSS 获取失败: {feed.get('bozo_exception', '无数据')}")
            return []
        return [
            {
                "action": "发布",
                "title": entry["title"],
                "url": entry["link"].split("#")[0],
                "published": entry["updated"].split("T")[0],
            }
            for entry in feed["entries"]
        ]
    except Exception as e:
        print(f"博客数据获取异常: {e}")
        return []


def fetch_random_juzi(juzi_file):
    r = []
    with open(juzi_file, 'r', encoding="utf-8") as f:
        result = f.readlines()
    for s in result:
        if s.strip():
            r.append(s.strip())
    return r[random.randint(0, len(r) - 1)]


if __name__ == "__main__":
    real_root = pathlib.Path(__file__).parent.parent.resolve()
    readme = real_root / "README.md"
    readme_contents = readme.open().read()

    table_header = "| | |\n |:------------- | -------------: |\n"
    table_item = "| {action} <a href='{url}' target='_blank'>{title}</a> | {published} |"

    make_ssl_unverify()

    # 每日一句
    try:
        juzi_update = fetch_random_juzi(real_root / "src" / "juzi.txt")
        rewritten = replace_chunk(readme_contents, "juzi", "> " + juzi_update)
        print(f"✓ 每日一句更新成功")
    except Exception as e:
        print(f"✗ 每日一句更新失败: {e}")
        rewritten = readme_contents

    # 豆瓣
    try:
        doubans = fetch_douban()[:10]
        if doubans:
            doubans_update = table_header + "\n".join(
                [table_item.format(**item) for item in doubans]
            )
            rewritten = replace_chunk(rewritten, "douban", doubans_update)
            print(f"✓ 豆瓣数据更新成功 ({len(doubans)} 条)")
        else:
            print("✗ 豆瓣数据为空，跳过更新")
    except Exception as e:
        print(f"✗ 豆瓣数据更新失败: {e}")

    # 博客更新
    try:
        entries = fetch_blog_entries()[:10]
        if entries:
            entries_update = table_header + "\n".join(
                [table_item.format(**entry) for entry in entries]
            )
            rewritten = replace_chunk(rewritten, "blog", entries_update)
            print(f"✓ 博客数据更新成功 ({len(entries)} 条)")
        else:
            print("✗ 博客数据为空，跳过更新")
    except Exception as e:
        print(f"✗ 博客数据更新失败: {e}")

    # 写入 README
    readme.open("w").write(rewritten)
    print("README 更新完成")
