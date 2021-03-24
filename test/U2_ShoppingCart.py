import sys
sys.path.append("..")

import time
from src.common.DecoBase import ASSERT_RESULT

def UNIT_TEST_UpdateToken(conn, i, item = None):
    from src.C2_ShoppingCart import UpdateToken
    user = "user:000" + str(i)
    token = "abcdefghijklmn_token" + str(i)
    if item != None:
        item = item + str(i)

    UpdateToken(conn, token, user, item)

    login_token = 'login_token:'
    update_token = 'update_token:'

    ASSERT_RESULT(conn.hget(login_token, token), '==', user, "login_token")
    ASSERT_RESULT(conn.zscore(update_token, token), '!=', None, "update_token")

def UNIT_TEST_CheckToken(conn, token, checkExist):
    from src.C2_ShoppingCart import CheckToken
    if checkExist:
        ASSERT_RESULT(CheckToken(conn, token), '!=', None, "check_token")
    else:
        ASSERT_RESULT(CheckToken(conn, token), '==', None, "check_token")

def UNIT_TEST_SetItemNumToCart(conn, session, item, num):
    from src.C2_ShoppingCart import SetItemNumToCart
    SetItemNumToCart(conn, session, item, num)
    if num < 0:
        ASSERT_RESULT(conn.hget('cart:' + str(session), item), '==', None, "check_delete_item")
    else:
        ASSERT_RESULT(conn.hget('cart:' + str(session), item), '==', str(num), "check_set_item")

def UNIT_TEST_CacheRequest(conn, request):
    from src.C2_ShoppingCart import CacheRequest
    CacheRequest(conn, request)
    ASSERT_RESULT(conn.get("cache:" + str(request)), '!=', None, "check_cache_expire")
    time.sleep(0.1)#sleep 100ms, expire
    ASSERT_RESULT(conn.get("cache:" + str(request)), '==', None, "check_cache_expire")

def UNIT_TEST_CacheRows(conn):
    from src.C2_ShoppingCart import CacheRows
    from src.C2_ShoppingCart import SetCacheRows
    for i in range(0,10):
        SetCacheRows(conn, i, time.time() + (10 - i) / 10.0)
    # set 10 tasks and each round deal with 3 tasks
    CacheRows(conn, 3)

def UNIT_TEST_CacheViews(conn):
    from src.C2_ShoppingCart import CacheViews
    CacheViews(conn)
