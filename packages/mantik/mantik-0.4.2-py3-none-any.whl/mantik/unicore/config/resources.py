import dataclasses
import typing as t

import mantik.unicore.config._base as _base
import mantik.unicore.config._utils as _utils


@dataclasses.dataclass
class Resources(_base.ConfigObject):
    """The computing resources that will be requested ."""

    queue: str
    runtime: t.Optional[str] = None
    nodes: t.Optional[int] = None
    total_cpus: t.Optional[int] = None
    cpus_per_node: t.Optional[int] = None
    gpus_per_node: t.Optional[int] = None
    memory_per_node: t.Optional[str] = None
    reservation: t.Optional[str] = None
    node_constraints: t.Optional[str] = None
    qos: t.Optional[str] = None

    @classmethod
    def _from_dict(cls, config: t.Dict) -> "Resources":
        queue = _utils.get_required_config_value(
            name="Queue",
            value_type=str,
            config=config,
        )
        runtime = _utils.get_optional_config_value(
            name="Runtime",
            value_type=str,
            config=config,
        )
        nodes = _utils.get_optional_config_value(
            name="Nodes",
            value_type=int,
            config=config,
        )
        total_cpus = _utils.get_optional_config_value(
            name="TotalCPUs",
            value_type=int,
            config=config,
        )
        cpus_per_node = _utils.get_optional_config_value(
            name="CPUsPerNode",
            value_type=int,
            config=config,
        )
        gpus_per_node = _utils.get_optional_config_value(
            name="GPUsPerNode",
            value_type=int,
            config=config,
        )
        memory_per_node = _utils.get_optional_config_value(
            name="MemoryPerNode",
            value_type=str,
            config=config,
        )
        reservation = _utils.get_optional_config_value(
            name="Reservation",
            value_type=str,
            config=config,
        )
        node_constraints = _utils.get_optional_config_value(
            name="NodeConstraints",
            value_type=str,
            config=config,
        )
        qos = _utils.get_optional_config_value(
            name="QoS",
            value_type=str,
            config=config,
        )
        return cls(
            queue=queue,
            runtime=runtime,
            nodes=nodes,
            total_cpus=total_cpus,
            cpus_per_node=cpus_per_node,
            gpus_per_node=gpus_per_node,
            memory_per_node=memory_per_node,
            reservation=reservation,
            node_constraints=node_constraints,
            qos=qos,
        )

    def _to_dict(self) -> t.Dict:
        return {
            "Runtime": self.runtime,
            "Queue": self.queue,
            "Nodes": self.nodes,
            "TotalCPUs": self.total_cpus,
            "CPUsPerNode": self.cpus_per_node,
            "GPUS": self.gpus_per_node,
            "MemoryPerNode": self.memory_per_node,
            "Reservation": self.reservation,
            "NodeConstraints": self.node_constraints,
            "QoS": self.qos,
        }
