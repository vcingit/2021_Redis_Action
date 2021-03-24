
'''
login token
each person's token is owned by himself
use redis to get/set/update login token

1.login, set token
2.op,update token
3.token expire time
'''

import time
import logging

LOGIN_TOKEN_PREFIX = 'login_token:'
UPDATE_TOKEN_PREFIX = 'update_token:'
VIEW_ITEM_PREFIX = 'view_item:'
VIEW_ITEM_LIMIT_NUM = 25
CART_PREFIX = 'cart:'


def CheckToken(conn, token):
    return conn.hget(LOGIN_TOKEN_PREFIX, token)

def UpdateToken(conn, token, user, item = None):
    now_time = time.time()
    #record token to logindata
    conn.hset(LOGIN_TOKEN_PREFIX, token, user)
    # update token refresh time
    conn.zadd(UPDATE_TOKEN_PREFIX, {token:now_time})

    if item:
        # record viewed item
        VIEW_ITEM_KEY = VIEW_ITEM_PREFIX + str(item)
        conn.zadd(VIEW_ITEM_KEY, {item:now_time})
        # only save last 25 records
        conn.zremrangebyrank(VIEW_ITEM_KEY, 0, -(VIEW_ITEM_LIMIT_NUM + 1))
    
    logging.debug('user %s, token %s, updatetime %s' % (user, token, str(now_time)))
    #each op run clear toekn
    ClearToken(conn)

'''
clear session
delete token data when login or update
this op will delay response to client, so set a small delete_num value
'''
LIMIT_UPDATE_TOKEN_NUM = 30
ONCE_DELETE_TOKEN_NUM = 10

def ClearToken(conn):
    token_size = conn.zcard(UPDATE_TOKEN_PREFIX)
    if token_size <= LIMIT_UPDATE_TOKEN_NUM:
        return
    end_idx = min(token_size - LIMIT_UPDATE_TOKEN_NUM, ONCE_DELETE_TOKEN_NUM)
    tokens = conn.zrange(UPDATE_TOKEN_PREFIX, 0, end_idx - 1)
    logging.debug('clear %s' % tokens)

    #viewed_keys = [VIEW_ITEM_PREFIX + str(i) for i in tokens]
    #delete token and session
    viewed_keys = []
    for i in tokens:
        viewed_keys.append(VIEW_ITEM_PREFIX + str(i))
        viewed_keys.append(CART_PREFIX + str(i))
    #batch delete
    conn.delete(*viewed_keys)
    conn.hdel(LOGIN_TOKEN_PREFIX, *tokens)
    conn.zrem(UPDATE_TOKEN_PREFIX, *tokens)

'''
set cart item num
or del item from cart
'''
def SetItemNumToCart(conn, session, item, num):
    if num < 0:
        conn.hdel(CART_PREFIX + str(session), item)
        logging.debug('delete item %s from cart %s' % (item, CART_PREFIX + str(session)))
        return
    
    conn.hset(CART_PREFIX + str(session), item, num)
    logging.debug('set item %s num %d from cart %s' % (item, num, CART_PREFIX + str(session)))


CACHE_PREFIX = 'cache:'
CACHE_EXPIRE_TIME = 50

'''
simple cache request
'''
def CacheRequest(conn, request):
    cache_key = CACHE_PREFIX + request

    content = conn.get(cache_key)
    if not content:
        content = "content_of_" + str(request)
        #expire 50 ms
        conn.psetex(cache_key, CACHE_EXPIRE_TIME, content)
        logging.debug('set cache_key %s, content %s' % (cache_key, content))

SCHEDULE_PREFIX = 'schedule:'
ONCE_UPDATE_NUM = 10

'''
simple cache rows
"2.4 Database row caching" use redis implement a delay queue
it uses zset sort task with acceptTime and delayTime
but each 50ms only update top 1 info
we can extend update time and get more rows in one update
'''
def CacheRows(conn, test_count):
    while True and test_count > 0:
        infos = conn.zrange(SCHEDULE_PREFIX, 0, ONCE_UPDATE_NUM - 1, withscores=True)
        now = time.time()
        for i in infos:
            row_id = i[0]
            row_time = i[1]
            #it was not yet
            if row_time > now:
                continue
            
            #delete
            conn.zrem(SCHEDULE_PREFIX, row_id)
            logging.debug('run task %s time %s' % (str(row_id), str(row_time)))
            
            test_count -= 1


def SetCacheRows(conn, row_id, update_time):
    conn.zadd(SCHEDULE_PREFIX, {row_id:update_time})


'''
2.5 Web page analytics
record user's viewing info, then make a recommand list to show famous items
we need to reduce the score frequently to avoid the products staying on the list for a long time
its function is similar to C1_VoteArticle, only change the useage of zinterstore, so skip
'''
def CacheViews(conn):
    pass