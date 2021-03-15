import sys
sys.path.append("..")

from src.common.DecoBase import ASSERT_RESULT

def UNIT_TEST_CreateArticle(conn, i):
    from src.C1_VoteArticle import CreateArticle
    user = "user:000" + str(i)
    title = "baiduTestTitle" + str(i)
    url = "www.baidu.com" + str(i)

    article_id = CreateArticle(conn, user, title, url)
    article_key = "article:" + str(article_id)

    ASSERT_RESULT(conn.hmget(article_key, "vote"), '==', ['0'], "vote")
    ASSERT_RESULT(conn.hmget(article_key, "publisher"), '==', [user], "publisher")
    ASSERT_RESULT(conn.hmget(article_key, "title"), '==', [title], "title")
    ASSERT_RESULT(conn.hmget(article_key, "url"), '==', [url], "url")
def UNIT_TEST_VoteArticle(conn, user):
    from src.C1_VoteArticle import VoteArticle
    i = int(user.split('user:000')[1:][0])
    article = "article:" + str(i)
    vote_key = "vote:" + str(i)
    #print article
    VoteArticle(conn, user, article)

    ASSERT_RESULT(conn.hmget(article, "vote"), '==', ['1'], "vote")
    ASSERT_RESULT(user, 'in', conn.smembers(vote_key), "vote_key")
    ASSERT_RESULT(conn.zscore("score:", article), '==', 3600 * 24 / 200 + float(conn.hmget(article, "time")[0]), "score")
def UNIT_TEST_GetTopArticleList(conn, page):
    from src.C1_VoteArticle import GetTopArticle
    articles = GetTopArticle(conn, page)
    valid_set = [i for i in range(79, 100) if (i + 1) % 2 == 0]
    for article in articles:
        article_id = int(article['article_id'].split(':')[1])
        #print article_id, valid_set
        ASSERT_RESULT(article_id, 'in', valid_set, "not in set")
        valid_set.remove(article_id)
    ASSERT_RESULT(len(valid_set), '==', 0, "top set is not empty")
def UNIT_TEST_AddMoveGroup(conn, article, addAllList, remAllList):
    from src.C1_VoteArticle import AddRemoveGroup
    addlist = addAllList
    remlist = []
    AddRemoveGroup(conn, article, addlist, remlist)

    for i in addAllList:
        ASSERT_RESULT(article, 'in', conn.smembers("group:" + str(i)), "group judge%s" % i)
    
    addlist = []
    remlist = remAllList
    AddRemoveGroup(conn, article, addlist, remlist)

    for i in addAllList:
        if i in remAllList:
            ASSERT_RESULT(article, 'not in', conn.smembers("group:" + str(i)), "group judge%s" % i)
        else:
            ASSERT_RESULT(article, 'in', conn.smembers("group:" + str(i)), "group judge%s" % i)
def UNIT_TEST_GetGroupTopArticles(conn, group_name, page, judge_articles):
    from src.C1_VoteArticle import GetGroupTopArticles
    articles = GetGroupTopArticles(conn, group_name, page)
    for i in judge_articles:
        bFind = False
        for j in range(len(articles)):
            if i in articles[j]['article_id']:
                bFind = True
                break
        ASSERT_RESULT(bFind, '==', True, "%s not in group articles" % i)
