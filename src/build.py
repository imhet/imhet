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
    return [
        {
            "action": item["title"][0:2],
            "title": item["title"][2:],
            "url": item["link"].split("#")[0],
            "published": format_date(item["published"])
        }
        for item in feedparser.parse("https://www.douban.com/feed/people/heyitao/interests")["entries"]
    ]


def fetch_blog_entries():
    return [
        {
            "action": "发布",
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["updated"].split("T")[0],
        }
        for entry in feedparser.parse("https://heyitao.com/feed")["entries"]
    ]


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
    juzi_update = fetch_random_juzi(real_root / "src" / "juzi.txt")
    print(juzi_update)
    rewritten = replace_chunk(readme_contents, "juzi", "```\n" + juzi_update + "\n```")

    # 豆瓣   
    doubans = fetch_douban()[:10]
    doubans_update = table_header + "\n".join(
        [table_item.format(**item) for item in doubans]
    )
    rewritten = replace_chunk(readme_contents, "douban", doubans_update)

    # 博客更新
    entries = fetch_blog_entries()[:10]
    entries_update = table_header + "\n".join(
        [table_item.format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_update)

    print(rewritten)
    # 写入 README    
    readme.open("w").write(rewritten)
