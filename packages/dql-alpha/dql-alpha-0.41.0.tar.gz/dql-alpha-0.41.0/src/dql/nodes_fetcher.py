import logging

from dql.nodes_thread_pool import NodesThreadPool

logger = logging.getLogger("dql")


class NodesFetcher(NodesThreadPool):
    def __init__(self, client, max_threads, cache):
        super().__init__(max_threads)
        self.client = client
        self.cache = cache

    def done_task(self, done):
        updated_nodes = []
        for d in done:
            lst = d.result()
            for node, checksum in lst:
                node.checksum = checksum
                self.cache.set_checksum(node.as_uid(self.client.uri), checksum)
                updated_nodes.append(node)
        return updated_nodes

    def do_task(self, chunk):
        from dvc_objects.fs.callbacks import Callback

        class _CB(Callback):
            def relative_update(  # pylint: disable=no-self-argument
                _, inc: int = 1  # noqa: disable=no-self-argument
            ):
                self.increase_counter(inc)

        res = []
        for node in chunk:
            if self.cache.exists(node.checksum):
                self.increase_counter(node.size)
                continue

            uid = node.as_uid(self.client.name)
            hash_value = self.client.put_in_cache(uid, callback=_CB())
            res.append((node, hash_value))
        return res
