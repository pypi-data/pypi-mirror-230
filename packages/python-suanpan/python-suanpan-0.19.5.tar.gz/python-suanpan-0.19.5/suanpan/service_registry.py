from suanpan import g, error
from suanpan.graph import graph


def lookup(port_id: str):
    connections = graph.getOutputConnections(g.nodeId, port_id)
    if len(connections) != 1:
        raise error.GraphError('invalid service connection')

    service = connections[0]
    svc_node = graph.getNodeById(service.process)
    for port in svc_node.metadata['def'].ports:
        if port.uuid == service.port:
            port_info = port.description.zh_CN
            svc = f'app-{g.appId}-{service.process}'
            return f'{svc}:{port_info}' if port_info else svc
