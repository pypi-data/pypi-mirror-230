# test.py
# cSpell:disable
# pylama:ignore=W0611,E501

# import json
import os

from dotenv import load_dotenv

from pyonms import PyONMS
from pyonms.dao.nodes import NodeComponents

# from tqdm import tqdm

# from pyonms.models import foreign_source, requisition
# from pyonms.models.event import Event, Severity
# from pyonms.models.foreign_source import Parameter
# from pyonms.models.udl import UserDefinedLink
# from pyonms.utils import normalize_dict

# try:
#     import pyroscope

#     pyroscope.configure(
#         application_name="pyonms.test",  # replace this with some name for your application
#         server_address="http://192.168.86.160:4040",  # replace this with the address of your pyroscope server
#     )
# except ModuleNotFoundError:
#     pass

load_dotenv()

# This test file utilizes environment variables to store server name and
# credentials as an alternative to including them in your code.

# You can set the following environment variables or create an `.env` file
# to provide credentials for accessing a Meridian/Horizon server.

# Set the following values in the file:

# * `hostname` (Example: `\http://localhost:8980/opennms`)
# * `username`
# * `password`


my_server = PyONMS(
    hostname=os.getenv("hostname"),
    username=os.getenv("user"),
    password=os.getenv("password"),
)
print(my_server.health.probe())
if __name__ == "__main__":
    # my_server.reload_daemon(name="eventd")
    # for _ in [37, 36, 62, 44]:
    #        my_server.udl.create_link(
    #            link=UserDefinedLink(
    #                node_id_a=43,
    #                node_id_z=_,
    #                component_label_a="eth0",
    #                component_label_z="eth1",
    #                owner="me",
    #            )
    #        )
    # x = my_server.udl.create_link(link=new_link)
    # x = my_server.udl.get_link(id=1377)
    # links = my_server.udl.get_links()
    # for link in links:
    #    my_server.udl.delete_link(id=link.db_id)
    # print(links)
    nodes = my_server.nodes.get_nodes(
        limit=5000,
        batch_size=100,
        components=[NodeComponents.ALL],
        threads=100,
        fiql="ford==Main",
    )
    print(f"Devices found: {len(nodes)}")
    print(nodes)

    # events = my_server.events.get_events(limit=50, batch_size=25, fiql="eventUei==uei.opennms.org/squadcast/resolve")
    # print(f"\nEvents found: {len(events)}")
    # print(events)
    # alarms = my_server.alarms.get_alarms(limit=5000, batch_size=25, fiql="severity==Minor")
    # for alarm in tqdm(alarms):
    #    my_server.alarms.ack_alarm(id=alarm.id, ack=False)
    #    my_server.alarms.clear_alarm(id=alarm.id)
    # print(f"\nAlarms found: {len(alarms)}")
    # pass
    # for alarm in alarms:
    #    print([alarm, my_server.nodes.get_node(alarm.nodeId)])

    # fs = my_server.fs.get_foreign_sources()
    # req = my_server.requisitions.get_requisitions()
    # act = my_server.requisitions.get_requisition_active_count()
    # dep = my_server.requisitions.get_requisition_deployed_count()
    # print(main)

    # bsms = my_server.bsm.get_bsms()
    # for bsm in bsms:
    #    new = bsm.request()
    #    new.name = new.name + "1"
    #   my_server.bsm.create_bsm(new)
    # status = my_server.info.get_info()
    # health = my_server.health.get_health()
    # print(my_server.health.probe())
    # my_server.reload_daemon(name="blarg")

    # sample = requisition.Requisition(foreign_source="Example")

    # new_node = requisition.RequisitionNode(foreign_id="py", node_label="text")
    # new_node.asset.append(requisition.AssetField(name="region", value="Blarg"))
    # new_node.meta_data.append(
    #     requisition.Metadata(context="requisition", key="key", value="value")
    # )
    # new_node.set_metadata(key="hello", value="there")
    # new_node.set_metadata(key="key", value="new_value")

    # my_interface = requisition.Interface(ip_addr="127.4.3.2", snmp_primary="P")

    # new_service = requisition.Service(
    #     service_name="SNMP",
    #     meta_data=[
    #         requisition.Metadata(context="requisition", key="key", value="value")
    #     ],
    # )
    # my_interface.monitored_service.append(new_service)

    # new_node.add_interface(my_interface, merge=False)

    # node2 = requisition.RequisitionNode(foreign_id="two", node_label="text2")
    # node2.add_interface(my_interface, merge=False)
    # node2.change_ip(old_ip="127.4.3.2", new_ip="127.7.8.9")

    # sample.add_node(new_node, merge=False)
    # sample.add_node(node2, merge=False)
    # text = json.dumps(sample._to_dict(), indent=3)
    # update = my_server.requisitions.update_requisition(sample)
    # my_server.requisitions.import_requisition(name=sample.foreign_source, rescan=False)
    # print(text)
    # new_fs = foreign_source.ForeignSource(name="Example")
    # new_fs.add_detector(
    #     foreign_source.Detector(
    #         name="ICMP",
    #         class_type="org.opennms.netmgt.provision.detector.icmp.IcmpDetector",
    #     ),
    #     merge=False,
    # )
    # new_fs.add_detector(
    #     foreign_source.Detector(
    #         name="ICMP2",
    #         class_type="org.opennms.netmgt.provision.detector.icmp.IcmpDetector",
    #         parameters=[Parameter(key="ipMatch", value="~.*")],
    #     ),
    #     merge=False,
    # )
    # new_fs.add_policy(
    #     foreign_source.Policy(
    #         name="blork",
    #         class_type="org.opennms.netmgt.provision.persist.policies.MatchingSnmpInterfacePolicy",
    #         parameters=[Parameter(key="ifType", value="6")],
    #     ),
    #     merge=False,
    # )
    # new_fs.add_policy(
    #     foreign_source.Policy(
    #         name="blosfdgrk",
    #         class_type="org.opennms.netmgt.provision.persist.policies.MatchingSnmpInterfacePolicy",
    #         parameters=[
    #             Parameter(key="ifType", value="6"),
    #             Parameter(key="ifAlias", value="~.*"),
    #         ],
    #     ),
    #     merge=False,
    # )
    # update_fs = my_server.fs.update_foreign_source(new_fs)
    # my_server.requisitions.import_requisition(name=new_fs.name, rescan=False)
    pass
