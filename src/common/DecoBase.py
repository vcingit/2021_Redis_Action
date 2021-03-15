import sys

#deco print func run info
def RunFunc(func):
    def wrapper(*args, **kw):
        try:
            print("RUN TEST %s" % func.__name__)
            func(*args, **kw)
        except Exception, err:
            #sys.stderr.write("Robot %d finish with error. Check <%s>\n" % (args[1].uin, args[1].casename))
            #logging.error("Robot %s err:%s. case:%s", args[1].openid, str(repr(err)), args[1].casename)
            #print("[FAILED], REASON : %s" % (str(repr(err))))
            print("[FAILED] %s" % (str(err)))
            pass
        else:
            print("\t\t\t\t[PASS]")

    return wrapper

#assert output is valid
def ASSERT_RESULT(out_result, symbol, need_result, err_msg):
    call_name = sys._getframe(1).f_code.co_name
    call_line = sys._getframe(0).f_back.f_lineno
    err_msg = "[" + str(call_name) + ":" + str(call_line) + "] " + err_msg + ". output:" + str(out_result) + " vs need:" + str(need_result)
    if symbol == '==':
        assert out_result == need_result, err_msg
    elif symbol == '<':
        assert out_result < need_result, err_msg
    elif symbol == '>':
        assert out_result > need_result, err_msg
    elif symbol == 'in':
        assert out_result in need_result, err_msg
    elif symbol == 'not in':
        assert out_result not in need_result, err_msg
