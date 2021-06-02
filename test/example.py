import casbin
import redis_watcher

def update_callback():
    print("this func is called,because policy is changed!")

if __name__=="__main__":
    red_watcher=redis_watcher.RedisWatcher(host='localhost',db=0,password="")
    e=casbin.Enforcer("../examples/rbac_model.conf","../examples/rbac_policy.csv")
    e.set_watcher(red_watcher)
    red_watcher.set_update_callback(update_callback)
    e.save_policy()

