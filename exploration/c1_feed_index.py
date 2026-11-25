# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""C1: feed-style query in SQLite - without an index, with an index, and with a cache.

Query: "the 20 newest posts from the people user 1 follows".
Run: python exploration/c1_feed_index.py
"""
import random
import sqlite3
import time

random.seed(0)
N_USERS, FOLLOWS_EACH, POSTS = 5_000, 100, 400_000
con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE posts   (id INTEGER PRIMARY KEY, author_id INTEGER, created_at INTEGER, body TEXT);
CREATE TABLE follows (follower_id INTEGER, followee_id INTEGER);
""")
con.executemany("INSERT INTO posts(author_id, created_at, body) VALUES (?,?,?)",
                ((random.randint(1, N_USERS), random.randint(0, 10**7), "x") for _ in range(POSTS)))
con.executemany("INSERT INTO follows VALUES (?,?)",
                ((u, random.randint(1, N_USERS)) for u in range(1, N_USERS + 1) for _ in range(FOLLOWS_EACH)))
con.commit()

FEED = """
SELECT p.id, p.author_id, p.created_at
FROM posts p JOIN follows f ON f.followee_id = p.author_id
WHERE f.follower_id = ?
ORDER BY p.created_at DESC LIMIT 20"""


def timed(label, n=20):
    t = time.perf_counter()
    for u in range(1, n + 1):
        con.execute(FEED, (u,)).fetchall()
    ms = (time.perf_counter() - t) / n * 1000
    print(f"{label}: {ms:.2f} ms per feed query")
    return ms


def plan(label):
    print(f"\nEXPLAIN QUERY PLAN ({label}):")
    for row in con.execute("EXPLAIN QUERY PLAN " + FEED, (1,)):
        print("  ", row[-1])


plan("no index"); t0 = timed("no index")
con.execute("CREATE INDEX idx_posts_author_time ON posts(author_id, created_at DESC)")
con.execute("CREATE INDEX idx_follows ON follows(follower_id)")
plan("with index"); t1 = timed("with index")
print(f"speed-up from indexes: {t0 / t1:.1f}x")

cache = {}


def cached_feed(u):
    if u not in cache:
        cache[u] = con.execute(FEED, (u,)).fetchall()
    return cache[u]


for u in range(1, 21):
    cached_feed(u)           # warm the cache (first request per user is a miss)
t = time.perf_counter()
for u in range(1, 21):
    cached_feed(u)
print(f"\nwith in-memory cache (hit): {(time.perf_counter() - t) / 20 * 1000:.4f} ms per feed")
