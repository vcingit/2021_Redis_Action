from common.ConnBase import GetRedisConn

'''
vote func
1.each time we should get top 100 famous ariticle
2.if ariticle get 200 up vote, we think it is interestring
3.each day we will publish 1000 ariticles, 50 of them was interestring, and we should put them to the toplist at least 1 day
4.if ariticle's publish time more than 7 days ago, it cannot be voted any more

slove
as we can see, each article has it's own score, we can calculate top 100 return back to user.
we can use zset, the key is combine of "article" and articleid, like this:
    (article:10000, score:100) ... (article:99999, score:200)
we should not only take care of up vote, also consider of time. the simple way is to use linux timestamp, now the score is:
    score = linux_time + 3600 * 24 / 200 * up_vote // 1 day 200 up vote
we should use set to record article vote status, forbid someone vote same article muti-times,and we can set expire time 7 days to delete set, and use code logic forbid user to vote
    article:10000 (user:0001 user:0002 ... user:9999)
at last, we design article info with hashmap:
    title:string url:string publisher:string time:uint32 votes:uint32

process
1.create an article
    get articleid by incr
    create article hashmap
    create article voteset
    create article scorezset

2.vote an article
    check can vote
    update article voteset
    update article scorezet
'''

import time
import logging

ARTICLE_MAPINFO_PREFIX = 'article:'
VOTE_SET_PREFIX = 'vote:'
SCORE_ZSET_PREFIX = 'score:'
GROUP_SET_PREFIX = 'group:'

VOTE_SCORE = 3600 * 24 / 200
VOTE_EXPIRE_TIME = 7 * 3600 * 24
ARTICLE_PER_PAGE = 10


def CreateArticle(conn, user, title, url):
    #create new id
    article_id = str(conn.incr('article:'))
    vote_key = VOTE_SET_PREFIX + article_id
    article_key = ARTICLE_MAPINFO_PREFIX + article_id
    score_db = SCORE_ZSET_PREFIX

    now_time = time.time()
    init_score = now_time + 0 * VOTE_SCORE
    #create hashmap
    conn.hmset(article_key,{
        'title':title,
        'url':url,
        'publisher':user,
        'time':now_time,
        'vote':0,
    })
    #create vote set
    #conn.sadd(vote_key, user)
    conn.expire(vote_key, VOTE_EXPIRE_TIME)
    #create score zset
    conn.zadd(score_db, {article_key:init_score})
    #get article id
    return article_id

def VoteArticle(conn, user, article):
    vote_expire_time = time.time() - VOTE_EXPIRE_TIME
    article_id = article.partition(':')[-1]
    article_key = ARTICLE_MAPINFO_PREFIX + article_id
    vote_key = VOTE_SET_PREFIX + article_id
    article_time = conn.hmget(article_key, 'time')
    score_db = SCORE_ZSET_PREFIX
    #article is too old
    if article_time < vote_expire_time:
        logging.debug('article %s cannot be voted' % article_time)
        return
    #if user not in vote set
    if conn.sadd(vote_key, user):
        #add score
        conn.zincrby(score_db, VOTE_SCORE, article_key)
        #add one vote
        conn.hincrby(article_key, 'vote', 1)
        logging.debug('user:%s vote article:%s success' % (user, article))
        return
    logging.debug('user:%s vote article:%s failed, muti voted' % (user, article))

def GetTopArticle(conn, page, score_db = SCORE_ZSET_PREFIX):
    start = (page - 1) * ARTICLE_PER_PAGE
    end = start + ARTICLE_PER_PAGE
    ids = conn.zrevrange(score_db, start, end)
    articles = []
    for one_id in ids:
        article_data = conn.hgetall(one_id)
        article_data['article_id'] = one_id
        articles.append(article_data)

    return articles

'''
extra func
1.add group for each articles
2.get top famous articles with group
'''
def AddRemoveGroup(conn, article, addlist = [], remlist = []):
    for one_group in addlist:
        group_key = GROUP_SET_PREFIX + str(one_group)
        conn.sadd(group_key, article)
    
    for one_group in remlist:
        group_key = GROUP_SET_PREFIX + str(one_group)
        conn.srem(group_key, article)

def GetGroupTopArticles(conn, group, page):
    score_db = SCORE_ZSET_PREFIX
    inter_group_key = score_db + str(group)
    group_key = GROUP_SET_PREFIX + str(group)
    if not conn.exists(inter_group_key):
        conn.zinterstore(inter_group_key, [group_key, score_db], aggregate='max')
        conn.expire(inter_group_key, 60)#60s expire

    return GetTopArticle(conn, page, inter_group_key)