from src.common.LogBase import InitLog
from src.common.DecoBase import ASSERT_RESULT
from src.common.DecoBase import RunFunc

from src.common.ConnBase import GetRedisConn
conn = GetRedisConn()
#conn.set("x1", "hello", ex=5)
#print conn.get("x1")

import time
import logging
# clear all redis data
def FLUSH_ALL():
    conn.flushall()

@RunFunc
def UNIT_TEST_VOTEARTICLE():
    from test.U1_VoteArticle import UNIT_TEST_CreateArticle
    from test.U1_VoteArticle import UNIT_TEST_VoteArticle
    from test.U1_VoteArticle import UNIT_TEST_GetTopArticleList
    from test.U1_VoteArticle import UNIT_TEST_AddMoveGroup
    from test.U1_VoteArticle import UNIT_TEST_GetGroupTopArticles
    for i in range(0,100):
        #create 100 articles
        UNIT_TEST_CreateArticle(conn, i + 1)
    for i in range(0, 100):
        if i % 2 == 0:
            #vote 50 articles
            user = "user:000" + str(i + 1)
            UNIT_TEST_VoteArticle(conn, user)
    #test top 0-10 article if correct
    UNIT_TEST_GetTopArticleList(conn, 1)

    UNIT_TEST_AddMoveGroup(conn, "article:1", ["A", "B"], ["A"])
    UNIT_TEST_AddMoveGroup(conn, "article:2", ["A", "B"], ["A"])
    UNIT_TEST_AddMoveGroup(conn, "article:3", ["A", "B"], ["B"])

    UNIT_TEST_GetGroupTopArticles(conn, "B", 1, ["article:1", "article:2"])

@RunFunc
def UNIT_TEST_SHOPPINGCART():
    from test.U2_ShoppingCart import UNIT_TEST_UpdateToken
    from test.U2_ShoppingCart import UNIT_TEST_CheckToken
    from test.U2_ShoppingCart import UNIT_TEST_SetItemNumToCart
    from test.U2_ShoppingCart import UNIT_TEST_CacheRequest
    from test.U2_ShoppingCart import UNIT_TEST_CacheRows
    from test.U2_ShoppingCart import UNIT_TEST_CacheViews
    
    for i in range(0,31):
        UNIT_TEST_UpdateToken(conn, i, "item_xxx")
        if i == 30:
            #when add item31, check del item1
            UNIT_TEST_CheckToken(conn, "abcdefghijklmn_token" + str(i - 30), False)
            #check item2 exist
            UNIT_TEST_CheckToken(conn, "abcdefghijklmn_token" + str(i - 29), True)
            #check item30 exist
            UNIT_TEST_CheckToken(conn, "abcdefghijklmn_token" + str(i), True)
    #set item 3 and check 3
    UNIT_TEST_SetItemNumToCart(conn, "abcdefghijklmn_token0", "item_xxx0", 3)
    #delete item and check exist
    UNIT_TEST_SetItemNumToCart(conn, "abcdefghijklmn_token0", "item_xxx0", -1)

    #check cache request expire
    UNIT_TEST_CacheRequest(conn, "test_request")
    #check cache rows
    UNIT_TEST_CacheRows(conn)
    #check cache views
    UNIT_TEST_CacheViews(conn)

def BeforeTest():
    #call = raw_input().split()
    #funcs[call[0]](*call[1:])
    InitLog()
    FLUSH_ALL()
    #test start, init db

def AfterTest():
    #test end, wait a few seconds
    cnt = 0
    while True:
        time.sleep(1)
        cnt += 1
        if cnt == 1:
            logging.debug("UNIT_TEST break")
            break

if __name__ == "__main__":
    
    BeforeTest()

    UNIT_TEST_VOTEARTICLE()

    UNIT_TEST_SHOPPINGCART()

    AfterTest()
