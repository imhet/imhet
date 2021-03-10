from python_graphql_client import GraphqlClient
import feedparser
import pathlib
import re
import os
import datetime

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
    return datetime.datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S GMT') + datetime.timedelta(hours=8).date()


def fetch_douban():
    return [
        {
            "title": item["title"],
            "url": item["link"].split("#")[0],
            "published": format_date(item["published"])
        }
        for item in feedparser.parse("https://www.douban.com/feed/people/heyitao/interests")["entries"]
    ]


def fetch_blog_entries():
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["updated"].split("T")[0],
        }
        for entry in feedparser.parse("https://heyitao.com/feed")["entries"]
    ]


if __name__ == "__main__":
    real_root = pathlib.Path(__file__).parent.parent.resolve()
    readme = real_root / "README.md"
    readme_contents = readme.open().read()

    # 豆瓣   
    doubans = fetch_douban()[:10]
    doubans_md = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in doubans]
    )
    rewritten = replace_chunk(readme_contents, "douban", doubans_md)

    # 博客更新
    entries = fetch_blog_entries()[:10]
    entries_md = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    # 写入 README    
    readme.open("w").write(rewritten)
