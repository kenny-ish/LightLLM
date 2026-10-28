from types import SimpleNamespace

import rpyc.utils.server

from lightllm.server.router import profiler_service
from lightllm.utils import shm_port_args


def test_router_profiler_server_disables_pickle(monkeypatch):
    captured = {}

    class FakeServer:
        def __init__(self, service, **kwargs):
            captured["service"] = service
            captured.update(kwargs)

        def start(self):
            pass

    class FakeThread:
        def __init__(self, target, daemon):
            captured["target"] = target
            captured["daemon"] = daemon

        def start(self):
            pass

    monkeypatch.setattr(rpyc.utils.server, "ThreadedServer", FakeServer)
    monkeypatch.setattr(profiler_service.threading, "Thread", FakeThread)
    monkeypatch.setattr(
        shm_port_args,
        "get_shm_port_args",
        lambda: SimpleNamespace(router_profiler_port=12345),
    )

    queue = profiler_service.RouterProfilerCmdQueue()
    server, thread = profiler_service.start_router_profiler_server(SimpleNamespace(enable_profiling=True), queue)

    assert isinstance(server, FakeServer)
    assert isinstance(thread, FakeThread)
    assert captured["port"] == 12345
    assert captured["protocol_config"] == {"allow_pickle": False}
    assert captured["service"].profiler_cmd_queue is queue
    assert captured["daemon"] is True
