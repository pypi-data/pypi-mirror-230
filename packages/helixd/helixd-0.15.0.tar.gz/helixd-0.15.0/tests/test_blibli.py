import helixd


def test_ok():
    helixd.main("stop -u http://localhost:8000 --failover http://10.0.1.1:8000".split())
    helixd.main("delete -u http://localhost:8000 --failover http://10.0.1.1:8000".split())
#    helixd.main("create -u http://localhost:8000 --failover http://10.0.1.1:8000".split())
 #   helixd.main("start -u http://localhost:8000 --failover http://10.0.1.1:8000".split())
