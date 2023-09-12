# coding=utf-8
import datetime
import json
import logging
import math
import pprint
import random

import string
import time
import uuid

from management import constants
from management import utils
from management.kv_store import DBController
from management import shell_utils
from management.models.compute_node import ComputeNode
from management.models.device_stat import DeviceStat
from management.models.iface import IFace
from management.models.nvme_device import NVMeDevice
from management.models.storage_node import StorageNode
from management import services
from management import spdk_installer
from management.pci_utils import get_nvme_devices, bind_nvme_driver, bind_spdk_driver
from management.rpc_client import RPCClient

logger = logging.getLogger()


class StorageOpsException(Exception):
    def __init__(self, message):
        self.message = message


def _get_ib_devices():
    return _get_data_nics([])


def _get_data_nics(data_nics):
    if not data_nics:
        return
    out, _, _ = shell_utils.run_command("ip -j address show")
    data = json.loads(out)
    logger.debug("ifaces")
    logger.debug(pprint.pformat(data))

    def _get_ip4_address(list_of_addr):
        if list_of_addr:
            for data in list_of_addr:
                if data['family'] == 'inet':
                    return data['local']
        return ""
    devices = {i["ifname"]: i for i in data}
    iface_list = []
    for nic in data_nics:
        if nic not in devices:
            continue
        device = devices[nic]
        iface = IFace({
            'uuid': str(uuid.uuid4()),
            'if_name': device['ifname'],
            'ip4_address': _get_ip4_address(device['addr_info']),
            'port_number': 1,  # TODO: check this value
            'status': device['operstate'],
            'net_type': device['link_type']})
        iface_list.append(iface)

    return iface_list


def _get_if_ip_address(ifname):
    out, _, _ = shell_utils.run_command("ip -j address show %s" % ifname)
    data = json.loads(out)
    logger.debug(pprint.pformat(data))
    if data:
        data = data[0]
        if 'addr_info' in data and data['addr_info']:
            address_info = data['addr_info']
            for adr in address_info:
                if adr['family'] == 'inet':
                    return adr['local']
    logger.error("IP not found for interface %s", ifname)
    exit(1)


def addNvmeDevices(cluster, rpc_client=None):
    devs = get_nvme_devices()
    logger.info("Getting nvme devices")
    logger.debug(devs)
    sequential_number = 0
    devices = []

    ret = rpc_client.bdev_nvme_controller_list()
    ctr_map = {i["ctrlrs"][0]['trid']['traddr']: i["name"] for i in ret}

    for index, (pcie, vid) in enumerate(devs):

        if vid in constants.SSD_VENDOR_WHITE_LIST:
            if pcie in ctr_map:
                nvme_bdev = ctr_map[pcie]+"n1"
            else:
                name = "nvme_%s" % pcie.split(":")[2].split(".")[0]
                ret, err = rpc_client.bdev_nvme_controller_attach(name, pcie)
                time.sleep(2)
                nvme_bdev = f"{name}n1"

            ret = rpc_client.get_bdevs(nvme_bdev)
            if ret:
                nvme_dict = ret[0]
                nvme_driver_data = nvme_dict['driver_specific']['nvme'][0]
                model_number = nvme_driver_data['ctrlr_data']['model_number']
                if model_number not in cluster.model_ids:
                    logger.warning("Device model ID is not recognized: %s, "
                                   "skipping device: %s", model_number)
                    continue
                size = nvme_dict['block_size'] * nvme_dict['num_blocks']
                device_partitions_count = int(size / (cluster.blk_size * cluster.page_size_in_blocks))
                devices.append(
                    NVMeDevice({
                        'uuid': str(uuid.uuid4()),
                        'device_name': nvme_dict['name'],
                        'sequential_number': sequential_number,
                        'partitions_count': device_partitions_count,
                        'capacity': size,
                        'size': size,
                        'pcie_address': nvme_driver_data['pci_address'],
                        'model_id': model_number,
                        'serial_number': nvme_driver_data['ctrlr_data']['serial_number'],
                        'nvme_bdev': nvme_bdev,
                        'alloc_bdev': nvme_bdev
                    }))
                sequential_number += device_partitions_count
    return devices


def _get_nvme_list_from_file(cluster):
    devs = get_nvme_devices()
    logger.info("Getting nvme devices")
    logger.debug(devs)
    sequential_number = 0
    devices = []
    for index, (pcie, vid) in enumerate(devs):
        name = "nvme%s" % index
        if vid in constants.SSD_VENDOR_WHITE_LIST:

            model_number = 'Amazon EC2 NVMe Instance Storage'
            if model_number not in cluster.model_ids:
                logger.warning("Device model ID is not recognized: %s, "
                               "skipping device", model_number)
                continue
            size = 7500000000000
            device_partitions_count = int(size / (cluster.blk_size * cluster.page_size_in_blocks))
            devices.append(
                NVMeDevice({
                    'uuid': str(uuid.uuid4()),
                    'device_name': name,
                    'sequential_number': sequential_number,
                    'partitions_count': device_partitions_count,
                    'capacity': size,
                    'size': size,
                    'pcie_address': pcie,
                    'model_id': model_number,
                    'serial_number': "AWS22A4E8CF2CD844ED9",
                    'status': 'Active'
                }))
            sequential_number += device_partitions_count
    return devices


def _get_nvme_list(cluster):
    out, err, _ = shell_utils.run_command("sudo nvme list -v -o json")
    data = json.loads(out)
    logger.debug("nvme list:")
    logger.debug(pprint.pformat(data))

    def _get_pcie_controller(ctrl_list):
        if ctrl_list:
            for item in ctrl_list:
                if 'Transport' in item and item['Transport'] == 'pcie':
                    return item

    def _get_size_from_namespaces(namespaces):
        size = 0
        if namespaces:
            for ns in namespaces:
                size += ns['PhysicalSize']
        return size

    sequential_number = 0
    devices = []
    if data and 'Devices' in data:
        for dev in data['Devices'][0]['Subsystems']:
            controller = _get_pcie_controller(dev['Controllers'])
            if not controller:
                continue

            if controller['ModelNumber'] not in cluster.model_ids:
                logger.info("Device model ID is not recognized: %s, skipping device: %s",
                            controller['ModelNumber'], controller['Controller'])
                continue

            size = _get_size_from_namespaces(controller['Namespaces'])
            device_partitions_count = int(size / (cluster.blk_size * cluster.page_size_in_blocks))
            devices.append(
                NVMeDevice({
                    'device_name': controller['Controller'],
                    'sequential_number': sequential_number,
                    'partitions_count': device_partitions_count,
                    'capacity': size,
                    'size': size,
                    'pcie_address': controller['Address'],
                    'model_id': controller['ModelNumber'],
                    'serial_number': controller['SerialNumber'],
                    # 'status': controller['State']
                }))
            sequential_number += device_partitions_count
    return devices


def generate_rpc_user_and_pass():
    def _generate_string(length):
        return ''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(length))
    return _generate_string(8), _generate_string(16)


def create_partitions_arrays(global_settings, nvme_devs):
    sequential_number = 0
    device_to_partition = {}
    for index, nvme in enumerate(nvme_devs):
        device_number = index+1
        device_size = nvme.size
        device_partitions_count = int(device_size / (global_settings.NS_LB_SIZE * global_settings.NS_SIZE_IN_LBS))
        for device_partition_index in range(device_partitions_count):
            device_to_partition[sequential_number+device_partition_index] = (
                device_number, (global_settings.NS_SIZE_IN_LBS*device_partition_index))
        sequential_number += device_partitions_count
    status_ns = {i: 'Active' for i in range(sequential_number)}
    return device_to_partition, status_ns


def _run_nvme_smart_log(dev_name):
    out, _, _ = shell_utils.run_command("sudo nvme smart-log /dev/%s -o json" % dev_name)
    data = json.loads(out)
    logger.debug(out)
    return data


def _run_nvme_smart_log_add(dev_name):
    out, _, _ = shell_utils.run_command("sudo nvme intel smart-log-add /dev/%s --json" % dev_name)
    data = json.loads(out)
    logger.debug(out)
    return data


def add_storage_node(cluster_id, iface_name, data_nics):
    db_controller = DBController()
    kv_store = db_controller.kv_store

    clusters = db_controller.get_clusters(cluster_id)
    if not clusters:
        logging.error("Cluster not found: %s", cluster_id)
        return False
    cluster = clusters[0]

    logging.info("Add Storage node")

    hostname = utils.get_hostname()
    snode = db_controller.get_storage_node_by_hostname(hostname)
    if snode:
        logger.error("Node already exists")
        #exit(1)
    else:
        snode = StorageNode()
        snode.uuid = str(uuid.uuid4())

    mgmt_ip = _get_if_ip_address(iface_name)
    system_id = utils.get_system_id()

    BASE_NQN = cluster.nqn.split(":")[0]
    subsystem_nqn = f"{BASE_NQN}:{hostname}"

    if data_nics:
        data_nics = _get_data_nics(data_nics)
    else:
        data_nics = _get_data_nics([iface_name])

    # install spdk
    # logger.info("Installing SPDK")
    # spdk_installer.install_spdk()
    # #
    # logger.info("Creating spdk_nvmf_tgt service")
    # spdk_nvmf_tgt = services.spdk_nvmf_tgt
    # spdk_nvmf_tgt.init_service()
    # time.sleep(3)
    # logger.info(f"spdk_nvmf_tgt service is running: {spdk_nvmf_tgt.is_service_running()}")
    # snode.services = ["spdk_nvmf_tgt"]
    #
    # logger.info("Creating rpc_http_proxy service")
    rpc_user, rpc_pass = generate_rpc_user_and_pass()
    # rpc_srv = services.rpc_http_proxy
    # rpc_srv.args = [mgmt_ip, str(constants.RPC_HTTP_PROXY_PORT), rpc_user,  rpc_pass]
    # rpc_srv.service_remove()
    # time.sleep(3)
    # rpc_srv.init_service()
    # time.sleep(1)
    # logger.info(f"rpc_http_proxy service is running: {rpc_srv.is_service_running()}")
    # snode.services.append("rpc_http_proxy")

    # creating storage node object
    snode.status = StorageNode.STATUS_IN_CREATION
    snode.baseboard_sn = utils.get_baseboard_sn()
    snode.system_uuid = system_id
    snode.hostname = hostname
    snode.host_nqn = subsystem_nqn
    snode.subsystem = subsystem_nqn
    snode.data_nics = data_nics
    snode.mgmt_ip = mgmt_ip
    snode.rpc_port = constants.RPC_HTTP_PROXY_PORT
    snode.rpc_username = rpc_user
    snode.rpc_password = rpc_pass
    snode.write_to_db(kv_store)

    # creating RPCClient instance
    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    #TODO check if online else retry

    nvme_devs = addNvmeDevices(cluster, rpc_client)
    if not nvme_devs:
        logger.error("No NVMe devices was found!")

    logger.debug(nvme_devs)
    snode.nvme_devices = nvme_devs

    # # add subsystems
    # logger.info("getting subsystem list")
    # subsystem_list = rpc_client.subsystem_list()
    # logger.debug(subsystem_list)
    # subsystem = [x for x in subsystem_list if x['nqn'] == subsystem_nqn]
    # if subsystem:
    #     logger.info("subsystem exist, skipping creation")
    # else:
    #     logger.info("creating subsystem %s", subsystem_nqn)
    #     ret = rpc_client.subsystem_create(subsystem_nqn, nvme_devs[0].serial_number, nvme_devs[0].model_id)
    #     logger.debug(ret)
    #     ret = rpc_client.subsystem_list()
    #     logger.debug(ret)
    #
    # # add listeners
    # logger.info("adding listeners")
    # for iface in data_nics:
    #     if iface.ip4_address:
    #         tr_type = iface.get_transport_type()
    #         ret = rpc_client.transport_create(tr_type)
    #         logger.debug(ret)
    #         logger.info("adding listener for %s on IP %s" % (subsystem_nqn, iface.ip4_address))
    #         ret = rpc_client.listeners_create(subsystem_nqn, tr_type, iface.ip4_address, "4420")
    #         logger.debug(ret)
    #
    # logger.debug("getting listeners")
    # ret = rpc_client.listeners_list(subsystem_nqn)
    # logger.debug(ret)
    #
    # # add compute nodes to allowed hosts
    # logger.info("Adding Active Compute nodes to the node's whitelist")
    # cnodes = ComputeNode().read_from_db(kv_store)
    #
    # for node in cnodes:
    #     if node.status == node.STATUS_ONLINE:
    #         logger.info("Active compute node found on host: %s" % node.hostname)
    #         ret = rpc_client.subsystem_add_host(subsystem_nqn, node.host_nqn)
    #         logger.debug(ret)
    #

    # logger.debug("controllers list")
    # ret = rpc_client.bdev_nvme_controller_list()
    # logger.debug(ret)
    # ctr_names = [i["name"] for i in ret]
    nvme_bdevs = []
    # attach bdev controllers
    for index, nvme in enumerate(nvme_devs):
        nvme_bdevs.append(nvme.nvme_bdev)

    snode.nvme_devices = nvme_devs


    if len(nvme_bdevs) == 1:
        lvstore_base_bdev = nvme_bdevs[0]
    else:
        lvstore_base_bdev = "raid0"
        ret = rpc_client.bdev_raid_create(lvstore_base_bdev, nvme_bdevs)
        time.sleep(3)

    lvs = "lvs_" + snode.uuid.split("-")[0]
    ret = rpc_client.create_lvstore(lvs, lvstore_base_bdev)
    snode.node_lvs = lvs

    logging.info("Setting node status to Active")
    snode.status = StorageNode.STATUS_ONLINE
    snode.write_to_db(kv_store)
    logger.info("Done")
    return "Success"



def remove_storage_node(kv_store, node_id):
    db_controller = DBController(kv_store)
    logging.info("removing storage node")
    snode = db_controller.get_storage_node_by_id(node_id)
    if not snode:
        logger.error(f"can not find storage node: {node_id}")
        return False
    if snode.lvols:
        logger.error(f"Remove all lVols first")
        return False
    # logger.info("Leaving swarm...")
    #
    # node_docker = utils.get_docker_client()
    # node_docker.swarm.leave(force=True)
    #
    # nodes = node_docker.containers.list(all=True)
    # for node in nodes:
    #     if node.attrs["Name"] == "/spdk":
    #         logger.info("SPD container found, removing...")
    #         node.stop()
    #         node.remove(force=True)
    #         break

    snode.remove(kv_store)
    logging.info("done")


def restart_storage_node(cluster_id, run_tests):
    db_controller = DBController()
    kv_store = db_controller.kv_store

    clusters = db_controller.get_clusters(cluster_id)
    if not clusters:
        logging.error("Cluster not found: %s", cluster_id)
        return False
    cluster = clusters[0]

    logging.info("Restarting node")
    baseboard_sn = utils.get_baseboard_sn()
    snode = db_controller.get_storage_node_by_id(baseboard_sn)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        exit(1)

    logging.info("Node found: %s in state: %s", snode.hostname, snode.status)
    if snode.status != StorageNode.STATUS_OFFLINE:
        logging.error("Node is not in offline state")
        exit(1)

    logger.info("Checking spdk_nvmf_tgt service status")
    nvmf_service = services.spdk_nvmf_tgt
    if nvmf_service.is_service_running():
        logging.error("Can not restart node: %s, service spdk_nvmf_tgt is running", snode.hostname)
        exit(1)
    logger.info("Service spdk_nvmf_tgt is inactive")

    logging.info("Setting node state to restarting")
    snode.status = StorageNode.STATUS_RESTARTING
    snode.write_to_db(kv_store)

    devs = get_nvme_devices()
    logger.info("binding nvme drivers")
    for dv in devs:
        bind_nvme_driver(dv[0])
        time.sleep(1)

    logger.info("Getting NVMe drives info")
    nvme_devs = _get_nvme_list(cluster)
    logging.debug(nvme_devs)

    logger.info("Comparing node drives and local drives")
    for node_nvme_device in snode.nvme_devices:
        logger.info("checking device: %s ,status: %s", node_nvme_device.serial_number, node_nvme_device.status)
        if node_nvme_device in nvme_devs:
            local_nvme_device = nvme_devs[nvme_devs.index(node_nvme_device)]
            if node_nvme_device.status == local_nvme_device.status:
                logger.info("No status update needed")
            else:
                logger.info("Updating status to: %s", local_nvme_device.status)
                node_nvme_device.status = local_nvme_device.status
        else:
            logger.info("device was not found on the node, status will be set to removed")
            node_nvme_device.status = NVMeDevice.STATUS_REMOVED
    logger.debug(snode.nvme_devices)

    # run smart log test
    if run_tests:
        logger.info("Running tests")
        for node_nvme_device in snode.nvme_devices:
            device_name = node_nvme_device.device_name
            logger.debug("Running smart-log on device: %s", device_name)
            smart_log_data = _run_nvme_smart_log(device_name)
            if "critical_warning" in smart_log_data:
                critical_warnings = smart_log_data["critical_warning"]
                if critical_warnings > 0:
                    logger.info("Critical warnings found: %s on device: %s, setting drive to failed state" %
                                (critical_warnings, device_name))
                    node_nvme_device.status = NVMeDevice.STATUS_FAILED
            logger.debug("Running smart-log-add on device: %s", device_name)
            additional_smart_log = _run_nvme_smart_log_add(device_name)
            program_fail_count = additional_smart_log['Device stats']['program_fail_count']['normalized']
            erase_fail_count = additional_smart_log['Device stats']['erase_fail_count']['normalized']
            crc_error_count = additional_smart_log['Device stats']['crc_error_count']['normalized']
            if program_fail_count < constants.NVME_PROGRAM_FAIL_COUNT:
                node_nvme_device.status = NVMeDevice.STATUS_FAILED
                logger.info("program_fail_count: %s is below %s on drive: %s, setting drive to failed state",
                            program_fail_count, constants.NVME_PROGRAM_FAIL_COUNT, device_name)
            if erase_fail_count < constants.NVME_ERASE_FAIL_COUNT:
                node_nvme_device.status = NVMeDevice.STATUS_FAILED
                logger.info("erase_fail_count: %s is below %s on drive: %s, setting drive to failed state",
                            erase_fail_count, constants.NVME_ERASE_FAIL_COUNT, device_name)
            if crc_error_count < constants.NVME_CRC_ERROR_COUNT:
                node_nvme_device.status = NVMeDevice.STATUS_FAILED
                logger.info("crc_error_count: %s is below %s on drive: %s, setting drive to failed state",
                            crc_error_count, constants.NVME_CRC_ERROR_COUNT, device_name)

    snode.write_to_db(kv_store)

    # Reinstall spdk service
    nvmf_service.service_remove()
    nvmf_service.init_service()

    # Reinstall spdk rpc service
    rpc_ip = snode.mgmt_ip
    rpc_user = snode.rpc_username
    rpc_pass = snode.rpc_password
    rpc_srv = services.rpc_http_proxy
    rpc_srv.args = [rpc_ip, str(constants.RPC_HTTP_PROXY_PORT), rpc_user,  rpc_pass]
    rpc_srv.service_remove()
    time.sleep(3)
    rpc_srv.init_service()


    # Creating monitors services
    logger.info("Creating ultra_node_monitor service")
    nm_srv = services.ultra_node_monitor
    nm_srv.service_remove()
    nm_srv.init_service()
    dm_srv = services.ultra_device_monitor
    dm_srv.service_remove()
    dm_srv.init_service()
    sc_srv = services.ultra_stat_collector
    sc_srv.service_remove()
    sc_srv.init_service()

    logger.info("binding spdk drivers")
    for dv in devs:
        bind_spdk_driver(dv[0])
        time.sleep(1)

    subsystem_nqn = snode.subsystem
    # creating RPCClient instance
    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    # add subsystems
    logger.info("getting subsystem list")
    subsystem_list = rpc_client.subsystem_list()
    logger.debug(subsystem_list)
    subsystem = [x for x in subsystem_list if x['nqn'] == subsystem_nqn]
    if subsystem:
        logger.info("subsystem exist, skipping creation")
    else:
        logger.info("creating subsystem %s", subsystem_nqn)
        ret = rpc_client.subsystem_create(
            subsystem_nqn, snode.nvme_devices[0].serial_number, snode.nvme_devices[0].model_id)
        logger.debug(ret)
        ret = rpc_client.subsystem_list()
        logger.debug(ret)

    # add rdma transport
    logger.info("getting transport list")
    ret = rpc_client.transport_list()
    logger.debug(ret)
    rdma_tr = [x for x in ret if x['trtype'] == "RDMA"]
    if rdma_tr:
        logger.info("RDMA transport exist, skipping creation")
    else:
        logger.info("creating RDMA transport")
        ret = rpc_client.transport_create('RDMA')
        logger.debug(ret)

    # add listeners
    logger.info("adding listeners")
    for iface in snode.ib_devices:
        if iface.ip4_address:
            logger.info("adding listener for %s on IP %s" % (subsystem_nqn, iface.ip4_address))
            ret = rpc_client.listeners_create(subsystem_nqn, "RDMA", iface.ip4_address, "4420")
            logger.debug(ret)

    logger.debug("getting listeners")
    ret = rpc_client.listeners_list(subsystem_nqn)
    logger.debug(ret)

    # add compute nodes to allowed hosts
    logger.info("Adding Active Compute nodes to the node's whitelist")
    cnodes = ComputeNode().read_from_db(kv_store)

    for node in cnodes:
        if node.status == node.STATUS_ONLINE:
            logger.info("Active compute node found on host: %s" % node.hostname)
            ret = rpc_client.subsystem_add_host(subsystem_nqn, node.host_nqn)
            logger.debug(ret)

    # attach bdev controllers
    for index, nvme in enumerate(snode.nvme_devices):
        if nvme.status in [NVMeDevice.STATUS_AVAILABLE, NVMeDevice.STATUS_READONLY,
                           NVMeDevice.STATUS_REMOVED, NVMeDevice.STATUS_UNRECOGNIZED]:
            logger.info("adding controller")
            ret = rpc_client.bdev_nvme_controller_attach("nvme_ultr21a_%s" % nvme.sequential_number, nvme.pcie_address)
            logger.debug(ret)

    logger.debug("controllers list")
    ret = rpc_client.bdev_nvme_controller_list()
    logger.debug(ret)

   # TODO: Don't create nvme partitions
   #  device_to_partition, status_ns = create_partitions_arrays(global_settings, snode.nvme_devices)
   #  out_data = {
   #      'device_to_partition': device_to_partition,
   #      'status_ns': status_ns,
   #      'NS_LB_SIZE': global_settings.NS_LB_SIZE,
   #      'NS_SIZE_IN_LBS': global_settings.NS_SIZE_IN_LBS}
   #  rpc_client.create_nvme_partitions(out_data)

    # allocate bdevs
    logger.info("Allocating bdevs")
    for index, nvme in enumerate(snode.nvme_devices):
        if nvme.status in [NVMeDevice.STATUS_AVAILABLE, NVMeDevice.STATUS_READONLY,
                           NVMeDevice.STATUS_REMOVED, NVMeDevice.STATUS_UNRECOGNIZED]:
            ret = rpc_client.allocate_bdev(nvme.device_name, nvme.sequential_number)
            logger.debug(ret)

    # creating namespaces
    logger.info("Creating namespaces")
    for index, nvme in enumerate(snode.nvme_devices):
        if nvme.status in [NVMeDevice.STATUS_AVAILABLE, NVMeDevice.STATUS_READONLY,
                           NVMeDevice.STATUS_REMOVED, NVMeDevice.STATUS_UNRECOGNIZED]:
            ret = rpc_client.nvmf_subsystem_add_ns(subsystem_nqn, nvme.device_name)
            logger.debug(ret)

    logging.info("Setting node status to Active")
    snode.status = StorageNode.STATUS_ONLINE
    snode.write_to_db(kv_store)
    logger.info("Done")


def list_storage_nodes(kv_store, is_json):
    db_controller = DBController(kv_store)
    nodes = db_controller.get_storage_nodes()
    data = []
    output = ""

    for node in nodes:
        logging.debug(node)
        logging.debug("*" * 20)
        data.append({
            "UUID": node.uuid,
            "Hostname": node.hostname,
            "Management IP": node.mgmt_ip,
            "Subsystem": node.subsystem,
            "NVMe Devs": f"{len(node.nvme_devices)}",
            "LVOLs": f"{len(node.lvols)}",
            "Data NICs": "\n".join([d.if_name for d in node.data_nics]),
            "Status": node.status,
            "Updated At": datetime.datetime.strptime(node.updated_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S, %d/%m/%Y"),
        })

    if not data:
        return output

    if is_json:
        output = json.dumps(data, indent=2)
    else:
        output = utils.print_table(data)
    return output


def list_storage_devices(kv_store, node_id, sort, is_json):
    db_controller = DBController(kv_store)
    snode = db_controller.get_storage_node_by_id(node_id)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        return False


    data = []
    for device in snode.nvme_devices:
        logging.debug(device)
        logging.debug("*" * 20)
        data.append({
            "UUID": device.uuid,
            "Name": device.device_name,
            "Hostname": snode.hostname,
            "Size": device.size,
            "Sequential Number": device.sequential_number,
            "Partitions Count": device.partitions_count,
            "Model ID": device.model_id,
            "Serial Number": device.serial_number,
            "PCIe": device.pcie_address,
            "Status": device.status,
        })

    if sort and sort in ['node-seq', 'dev-seq', 'serial']:
        if sort == 'serial':
            sort_key = "Serial Number"
        elif sort == 'dev-seq':
            sort_key = "Sequential Number"
        elif sort == 'node-seq':
            # TODO: check this key
            sort_key = "Sequential Number"
        sorted_data = sorted(data, key=lambda d: d[sort_key])
        data = sorted_data

    if is_json:
        return json.dumps(data, indent=2)
    else:
        return utils.print_table(data)


def shutdown_storage_node(kv_store):
    db_controller = DBController(kv_store)
    baseboard_sn = utils.get_baseboard_sn()
    snode = db_controller.get_storage_node_by_id(baseboard_sn)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        exit(1)

    logging.info("Node found: %s in state: %s", snode.hostname, snode.status)
    if snode.status != StorageNode.STATUS_ONLINE:
        logging.error("Node is not in online state")
        exit(1)

    logging.info("Shutting down node")
    snode.status = StorageNode.STATUS_IN_SHUTDOWN
    snode.write_to_db(kv_store)

    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    logger.info("Stopping spdk_nvmf_tgt service")
    nvmf_service = services.spdk_nvmf_tgt
    if nvmf_service.is_service_running():
        nvmf_service.service_stop()

    # make shutdown request
    response = rpc_client.shutdown_node(snode.get_id())
    if 'result' in response and response['result']:
        logging.info("Setting node status to Offline")
        snode.status = StorageNode.STATUS_OFFLINE
        snode.write_to_db(kv_store)
        logger.info("Done")
        return True
    else:
        logger.error("Error shutting down node")
        logger.debug(response)
        exit(1)


def suspend_storage_node(kv_store):
    #  in this case all process must be running
    db_controller = DBController(kv_store)
    baseboard_sn = utils.get_baseboard_sn()
    snode = db_controller.get_storage_node_by_id(baseboard_sn)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        exit(1)

    logging.info("Node found: %s in state: %s", snode.hostname, snode.status)
    if snode.status != StorageNode.STATUS_ONLINE:
        logging.error("Node is not in online state")
        exit(1)

    logging.info("Suspending node")

    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    # make suspend request
    response = rpc_client.suspend_node(snode.get_id())
    if 'result' in response and response['result']:
        logging.info("Setting node status to suspended")
        snode.status = StorageNode.STATUS_SUSPENDED
        snode.write_to_db(kv_store)
        logger.info("Done")
        return True
    else:
        logger.error("Error suspending node")
        logger.debug(response)
        exit(1)


def resume_storage_node(kv_store):
    db_controller = DBController(kv_store)
    baseboard_sn = utils.get_baseboard_sn()
    snode = db_controller.get_storage_node_by_id(baseboard_sn)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        exit(1)

    logging.info("Node found: %s in state: %s", snode.hostname, snode.status)
    if snode.status != StorageNode.STATUS_SUSPENDED:
        logging.error("Node is not in suspended state")
        exit(1)

    logging.info("Resuming node")

    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    # make suspend request
    response = rpc_client.resume_node(snode.get_id())
    if 'result' in response and response['result']:
        logging.info("Setting node status to online")
        snode.status = StorageNode.STATUS_ONLINE
        snode.write_to_db(kv_store)
        logger.info("Done")
        return True
    else:
        logger.error("Error suspending node")
        logger.debug(response)
        exit(1)


def reset_storage_device(kv_store, dev_name):
    db_controller = DBController(kv_store)
    baseboard_sn = utils.get_baseboard_sn()
    snode = db_controller.get_storage_node_by_id(baseboard_sn)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        exit(1)

    nvme_device = None
    for node_nvme_device in snode.nvme_devices:
        if node_nvme_device.device_name == dev_name:
            nvme_device = node_nvme_device
            break

    if nvme_device is None:
        logging.error("Device not found")
        exit(1)

    logging.info("Resetting device")

    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    # make suspend request
    response = rpc_client.reset_device(nvme_device.device_name)
    if 'result' in response and response['result']:
        logging.info("Setting device status to resetting")
        nvme_device.status = NVMeDevice.STATUS_RESETTING
        snode.write_to_db(kv_store)
        logger.info("Done")
        return True
    else:
        logger.error("Error resetting device")
        logger.debug(response)
        exit(1)


def run_test_storage_device(kv_store, dev_name):
    db_controller = DBController(kv_store)
    baseboard_sn = utils.get_baseboard_sn()
    snode = db_controller.get_storage_node_by_id(baseboard_sn)
    if not snode:
        logger.error("This storage node is not part of the cluster")
        exit(1)

    nvme_device = None
    for node_nvme_device in snode.nvme_devices:
        if node_nvme_device.device_name == dev_name:
            nvme_device = node_nvme_device
            break

    if nvme_device is None:
        logging.error("Device not found")
        exit(1)

    global_settings = db_controller.get_global_settings()
    logger.debug("Running smart-log on device: %s", dev_name)
    smart_log_data = _run_nvme_smart_log(dev_name)
    if "critical_warning" in smart_log_data:
        critical_warnings = smart_log_data["critical_warning"]
        if critical_warnings > 0:
            logger.info("Critical warnings found: %s on device: %s, setting drive to failed state" %
                        (critical_warnings, dev_name))
            nvme_device.status = NVMeDevice.STATUS_FAILED
    logger.debug("Running smart-log-add on device: %s", dev_name)
    additional_smart_log = _run_nvme_smart_log_add(dev_name)
    program_fail_count = additional_smart_log['Device stats']['program_fail_count']['normalized']
    erase_fail_count = additional_smart_log['Device stats']['erase_fail_count']['normalized']
    crc_error_count = additional_smart_log['Device stats']['crc_error_count']['normalized']
    if program_fail_count < global_settings.NVME_PROGRAM_FAIL_COUNT:
        nvme_device.status = NVMeDevice.STATUS_FAILED
        logger.info("program_fail_count: %s is below %s on drive: %s, setting drive to failed state",
                    program_fail_count, global_settings.NVME_PROGRAM_FAIL_COUNT, dev_name)
    if erase_fail_count < global_settings.NVME_ERASE_FAIL_COUNT:
        nvme_device.status = NVMeDevice.STATUS_FAILED
        logger.info("erase_fail_count: %s is below %s on drive: %s, setting drive to failed state",
                    erase_fail_count, global_settings.NVME_ERASE_FAIL_COUNT, dev_name)
    if crc_error_count < global_settings.NVME_CRC_ERROR_COUNT:
        nvme_device.status = NVMeDevice.STATUS_FAILED
        logger.info("crc_error_count: %s is below %s on drive: %s, setting drive to failed state",
                    crc_error_count, global_settings.NVME_CRC_ERROR_COUNT, dev_name)

    snode.write_to_db(kv_store)
    logger.info("Done")


def add_storage_device(dev_name, node_id, cluster_id):
    db_controller = DBController()
    kv_store = db_controller.kv_store
    clusters = db_controller.get_clusters(cluster_id)
    if not clusters:
        logging.error("Cluster not found: %s", cluster_id)
        return False
    cluster = clusters[0]

    snode = db_controller.get_storage_node_by_id(node_id)
    if not snode:
        logger.error("Node is not part of the cluster: %s", node_id)
        exit(1)

    for node_nvme_device in snode.nvme_devices:
        if node_nvme_device.device_name == dev_name:
            logging.error("Device already added to the cluster")
            exit(1)

    nvme_devs = _get_nvme_list(cluster)
    for device in nvme_devs:
        if device.device_name == dev_name:
            nvme_device = device
            break
    else:
        logging.error("Device not found: %s", dev_name)
        exit(1)

    # running smart tests
    logger.debug("Running smart-log on device: %s", dev_name)
    smart_log_data = _run_nvme_smart_log(dev_name)
    if "critical_warning" in smart_log_data:
        critical_warnings = smart_log_data["critical_warning"]
        if critical_warnings > 0:
            logger.info("Critical warnings found: %s on device: %s" % (critical_warnings, dev_name))
            exit(1)

    logger.debug("Running smart-log-add on device: %s", dev_name)
    additional_smart_log = _run_nvme_smart_log_add(dev_name)
    program_fail_count = additional_smart_log['Device stats']['program_fail_count']['normalized']
    erase_fail_count = additional_smart_log['Device stats']['erase_fail_count']['normalized']
    crc_error_count = additional_smart_log['Device stats']['crc_error_count']['normalized']
    if program_fail_count < constants.NVME_PROGRAM_FAIL_COUNT:
        logger.info("program_fail_count: %s is below %s on drive: %s",
                    program_fail_count, constants.NVME_PROGRAM_FAIL_COUNT, dev_name)
        exit(1)
    if erase_fail_count < constants.NVME_ERASE_FAIL_COUNT:
        logger.info("erase_fail_count: %s is below %s on drive: %s",
                    erase_fail_count, constants.NVME_ERASE_FAIL_COUNT, dev_name)
        exit(1)
    if crc_error_count < constants.NVME_CRC_ERROR_COUNT:
        logger.info("crc_error_count: %s is below %s on drive: %s",
                    crc_error_count, constants.NVME_CRC_ERROR_COUNT, dev_name)
        exit(1)

    logger.info("binding spdk drivers")
    bind_spdk_driver(nvme_device.pcie_address)
    time.sleep(1)

    logger.info("init device in spdk")
    # creating RPCClient instance
    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    # attach bdev controllers
    logger.info("adding controller")
    ret = rpc_client.bdev_nvme_controller_attach("nvme_ultr21a_%s" % nvme_device.sequential_number, nvme_device.pcie_address)
    logger.debug(ret)

    logger.debug("controllers list")
    ret = rpc_client.bdev_nvme_controller_list()
    logger.debug(ret)

    # # create nvme partitions
    # device_to_partition, status_ns = create_partitions_arrays(global_settings, nvme_devs)
    # out_data = {
    #     'device_to_partition': device_to_partition,
    #     'status_ns': status_ns,
    #     'NS_LB_SIZE': global_settings.NS_LB_SIZE,
    #     'NS_SIZE_IN_LBS': global_settings.NS_SIZE_IN_LBS}
    # rpc_client.create_nvme_partitions(out_data)

    # allocate bdevs
    logger.info("Allocating bdevs")
    ret = rpc_client.allocate_bdev(nvme_device.device_name, nvme_device.sequential_number)
    logger.debug(ret)

    # creating namespaces
    logger.info("Creating namespaces")
    ret = rpc_client.nvmf_subsystem_add_ns(snode.subsystem, nvme_device.device_name)
    logger.debug(ret)

    # set device new sequential number, increase node device count
    nvme_device.sequential_number = snode.sequential_number
    snode.sequential_number += nvme_device.partitions_count
    snode.partitions_count += nvme_device.partitions_count
    snode.nvme_devices.append(nvme_device)
    snode.write_to_db(kv_store)

    # create or update cluster map
    logger.info("Updating cluster map")
    cmap = db_controller.get_cluster_map()
    cmap.recalculate_partitions()
    logger.debug(cmap)
    cmap.write_to_db(kv_store)

    logger.info("Done")
    return True


def replace_node(kv_store, old_node_name, iface_name):
    db_controller = DBController(kv_store)
    baseboard_sn = utils.get_baseboard_sn()
    this_node = db_controller.get_storage_node_by_id(baseboard_sn)
    if this_node:
        logger.error("This storage node is part of the cluster")
        exit(1)

    old_node = db_controller.get_storage_node_by_hostname(old_node_name)
    if old_node is None:
        logging.error("Old node was not found in the cluster")
        exit(1)

    logging.info("Old node found: %s in state: %s", old_node.hostname, old_node.status)
    if old_node.status != StorageNode.STATUS_OFFLINE:
        logging.error("Node is not in offline state")
        exit(1)

    logging.info("Setting old node status to removed")
    old_node.status = StorageNode.STATUS_REMOVED
    old_node.write_to_db(kv_store)

    logging.info("Replacing node")

    mgmt_ip = _get_if_ip_address(iface_name)

    # install spdk
    logger.info("Installing SPDK")
    spdk_installer.install_spdk()

    system_id = utils.get_system_id()
    hostname = utils.get_hostname()
    ib_devices = _get_data_nics([iface_name])

    nvme_devs = old_node.nvme_devices
    logger.info("binding spdk drivers")
    for dv in nvme_devs:
        bind_spdk_driver(dv.pcie_address)
        time.sleep(1)

    logger.info("Creating spdk_nvmf_tgt service")
    nvmf_srv = services.spdk_nvmf_tgt
    nvmf_srv.init_service()

    logger.info("Creating rpc_http_proxy service")
    rpc_user, rpc_pass = generate_rpc_user_and_pass()
    rpc_srv = services.rpc_http_proxy
    rpc_srv.args = [mgmt_ip, str(constants.RPC_HTTP_PROXY_PORT), rpc_user,  rpc_pass]
    rpc_srv.service_remove()
    time.sleep(3)
    rpc_srv.init_service()

    # Creating monitors services
    logger.info("Creating ultra_node_monitor service")
    nm_srv = services.ultra_node_monitor
    nm_srv.init_service()
    dm_srv = services.ultra_device_monitor
    dm_srv.init_service()
    sc_srv = services.ultra_stat_collector
    sc_srv.init_service()

    # creating storage node object
    snode = StorageNode()
    snode.status = StorageNode.STATUS_IN_CREATION
    snode.baseboard_sn = baseboard_sn
    snode.system_uuid = system_id
    snode.hostname = hostname
    snode.host_nqn = old_node.host_nqn
    snode.subsystem = old_node.subsystem
    snode.nvme_devices = nvme_devs
    snode.ib_devices = ib_devices
    snode.mgmt_ip = mgmt_ip
    snode.rpc_port = constants.RPC_HTTP_PROXY_PORT
    snode.rpc_username = rpc_user
    snode.rpc_password = rpc_pass
    snode.sequential_number = old_node.sequential_number
    snode.partitions_count = old_node.partitions_count
    snode.write_to_db(kv_store)

    # creating RPCClient instance
    rpc_client = RPCClient(
        snode.mgmt_ip,
        snode.rpc_port,
        snode.rpc_username,
        snode.rpc_password)

    subsystem_nqn = snode.subsystem

    # add subsystems
    logger.info("getting subsystem list")
    subsystem_list = rpc_client.subsystem_list()
    logger.debug(subsystem_list)
    subsystem = [x for x in subsystem_list if x['nqn'] == subsystem_nqn]
    if subsystem:
        logger.info("subsystem exist, skipping creation")
    else:
        logger.info("creating subsystem %s", subsystem_nqn)
        ret = rpc_client.subsystem_create(subsystem_nqn, nvme_devs[0].serial_number, nvme_devs[0].model_id)
        logger.debug(ret)
        ret = rpc_client.subsystem_list()
        logger.debug(ret)

    # add rdma transport
    logger.info("getting transport list")
    ret = rpc_client.transport_list()
    logger.debug(ret)
    rdma_tr = [x for x in ret if x['trtype'] == "RDMA"]
    if rdma_tr:
        logger.info("RDMA transport exist, skipping creation")
    else:
        logger.info("creating RDMA transport")
        ret = rpc_client.transport_create('RDMA')
        logger.debug(ret)

    # add listeners
    logger.info("adding listeners")
    for iface in ib_devices:
        if iface.ip4_address:
            logger.info("adding listener for %s on IP %s" % (subsystem_nqn, iface.ip4_address))
            ret = rpc_client.listeners_create(subsystem_nqn, "RDMA", iface.ip4_address, "4420")
            logger.debug(ret)

    logger.debug("getting listeners")
    ret = rpc_client.listeners_list(subsystem_nqn)
    logger.debug(ret)

    # add compute nodes to allowed hosts
    logger.info("Adding Active Compute nodes to the node's whitelist")
    cnodes = ComputeNode().read_from_db(kv_store)
    for node in cnodes:
        if node.status == node.STATUS_ONLINE:
            logger.info("Active compute node found on host: %s" % node.hostname)
            ret = rpc_client.subsystem_add_host(subsystem_nqn, node.host_nqn)
            logger.debug(ret)

    # attach bdev controllers
    for index, nvme in enumerate(nvme_devs):
        logger.info("adding controller")
        ret = rpc_client.bdev_nvme_controller_attach("nvme_ultr21a_%s" % nvme.sequential_number, nvme.pcie_address)
        logger.debug(ret)

    logger.info("controllers list")
    ret = rpc_client.bdev_nvme_controller_list()
    logger.debug(ret)

    # create nvme partitions
    global_settings = db_controller.get_global_settings()

    device_to_partition = {}
    status_ns = {}
    for index, nvme in enumerate(nvme_devs):
        device_number = index + 1
        device_size = nvme.size
        sequential_number = nvme.sequential_number
        device_partitions_count = int(device_size / (global_settings.NS_LB_SIZE * global_settings.NS_SIZE_IN_LBS))
        for device_partition_index in range(device_partitions_count):
            device_to_partition[sequential_number + device_partition_index] = (
                device_number, (global_settings.NS_SIZE_IN_LBS * device_partition_index))
        status_ns.update(
            {i: 'Active' for i in range(sequential_number, sequential_number + device_partitions_count)})

    out_data = {
        'device_to_partition': device_to_partition,
        'status_ns': status_ns,
        'NS_LB_SIZE': global_settings.NS_LB_SIZE,
        'NS_SIZE_IN_LBS': global_settings.NS_SIZE_IN_LBS}
    rpc_client.create_nvme_partitions(out_data)

    # allocate bdevs
    logger.info("Allocating bdevs")
    for index, nvme in enumerate(nvme_devs):
        ret = rpc_client.allocate_bdev(nvme.device_name, nvme.sequential_number)
        logger.debug(ret)

    # creating namespaces
    logger.info("Creating namespaces")
    for index, nvme in enumerate(nvme_devs):
        ret = rpc_client.nvmf_subsystem_add_ns(subsystem_nqn, nvme.device_name)
        logger.debug(ret)

    logging.info("Setting node status to Active")
    snode.status = StorageNode.STATUS_ONLINE
    snode.write_to_db(kv_store)
    logger.info("Done")


def get_device_capacity(device_id, history):
    db_controller = DBController()
    device = db_controller.get_storage_devices(device_id)
    if not device:
        logger.error("device not found")

    data = db_controller.get_device_stats(device)
    out = []
    if not history:
        data = data[:1]

    for record in data:
        total_size = record.data_nr * record.pagesz
        free_size = record.freepg_cnt * record.pagesz
        util = int((total_size/free_size)*100)
        out.append({
            "Date": time.strftime("%H:%M:%S, %d/%m/%Y", time.gmtime(record.date)),
            "drive size": utils.humanbytes(device.size),
            "provisioned": utils.humanbytes(total_size),
            "util": utils.humanbytes(free_size),
            "util_percent": f"{util}%",
        })
    return utils.print_table(out)


def get_device(device_id):
    db_controller = DBController()
    device = db_controller.get_storage_devices(device_id)
    if not device:
        logger.error("device not found")
    out = [device.get_clean_dict()]
    return utils.print_table(out)


def get_device_iostats(device_id, history):
    db_controller = DBController()
    device = db_controller.get_storage_devices(device_id)
    if not device:
        logger.error("device not found")
        return False

    data = db_controller.get_device_stats(device)
    out = []
    if not history:
        data = data[:1]

    for record in data:
        out.append({
            "Date": time.strftime("%H:%M:%S, %d/%m/%Y", time.gmtime(record.date)),
            "bytes_read": record.stats["bytes_read"],
            "read_ops": record.stats["num_read_ops"],
            "read speed /s": utils.humanbytes(record.read_bytes_per_sec),
            "read_ops /s": record.read_iops,
            "bytes_write": record.stats["bytes_written"],
            "write_ops": record.stats["num_write_ops"],
            "write speed /s": utils.humanbytes(record.write_bytes_per_sec),
            "write_ops /s": record.write_iops,
            "read_lat_ticks": record.read_latency_ticks,
            "write_lat_ticks": record.write_latency_ticks,
            "IO Error": record.stats["io_error"],
        })
    return utils.print_table(out)


def get_node_capacity(node_id, history):
    db_controller = DBController()
    this_node = db_controller.get_storage_node_by_id(node_id)
    if not this_node:
        logger.error("This storage node is not part of the cluster")
        return

    devices = this_node.nvme_devices
    out = []
    t_size = t_prov = t_util = t_perc = 0
    for dev in devices:
        record = db_controller.get_device_stats(dev)[:1]
        total_size = record.data_nr * record.pagesz
        free_size = record.freepg_cnt * record.pagesz
        util = int((total_size / free_size) * 100)
        out.append({
            "Name": dev.device_name,
            "drive size": utils.humanbytes(dev.size),
            "provisioned": utils.humanbytes(total_size),
            "util": utils.humanbytes(free_size),
            "util_percent": f"{util}%",
        })
        t_size += dev.size
        t_prov += total_size
        t_util += free_size
        t_perc += util
    if devices:
        utp = int(t_perc/len(out))
        out.append({
            "Name": "Total",
            "drive size": utils.humanbytes(t_size),
            "provisioned": utils.humanbytes(t_prov),
            "util":  utils.humanbytes(t_util),
            "util_percent": f"{utp}%",
        })
    return utils.print_table(out)


def get_node_iostats(node_id, history):
    db_controller = DBController()

    node = db_controller.get_storage_node_by_id(node_id)
    if not node:
        logger.error("node not found")
        return False

    out = []
    limit = 20
    if history and history > 1:
        limit = history
    stats = DeviceStat().read_from_db(db_controller.kv_store, id="%s/%s" % (node.get_id(), node.get_id()), limit=limit, reverse=True)
    for record in stats:
        out.append({
            "Date": time.strftime("%H:%M:%S, %d/%m/%Y", time.gmtime(record.date)),
            "bytes_read": record.stats["bytes_read"],
            "read_ops": record.stats["num_read_ops"],
            "read speed /s": utils.humanbytes(record.read_bytes_per_sec),
            "read_ops /s": record.read_iops,
            "bytes_write": record.stats["bytes_written"],
            "write_ops": record.stats["num_write_ops"],
            "write speed /s": utils.humanbytes(record.write_bytes_per_sec),
            "write_ops /s": record.write_iops,
            "read_lat_ticks": record.read_latency_ticks,
            "write_lat_ticks": record.write_latency_ticks,
            "IO Error": record.stats["io_error"],
        })
    return utils.print_table(out)


def get_node_ports(node_id):
    db_controller = DBController()
    node = db_controller.get_storage_node_by_id(node_id)
    if not node:
        logger.error("node not found")
        return False

    out = []
    for nic in node.data_nics:
        out.append({
            "ID": nic.get_id(),
            "Device name": nic.if_name,
            "Address": nic.ip4_address,
            "Net type": nic.get_transport_type(),
            "Status": nic.status,
        })
    return utils.print_table(out)


def get_node_port_iostats(port_id, history=None):
    db_controller = DBController()
    nodes = db_controller.get_storage_nodes()
    nd = None
    port = None
    for node in nodes:
        for nic in node.data_nics:
            if nic.get_id() == port_id:
                port = nic
                nd = node
                break

    if not port:
        logger.error("Port not found")
        return False

    limit = 20
    if history and history > 1:
        limit = history
    data = db_controller.get_port_stats(nd.get_id(), port.get_id(), limit=limit)
    out = []

    for record in data:
        out.append({
            "Date": time.strftime("%H:%M:%S, %d/%m/%Y", time.gmtime(record.date)),
            "out_speed": utils.humanbytes(record.out_speed),
            "in_speed": utils.humanbytes(record.in_speed),
            "bytes_sent": utils.humanbytes(record.bytes_sent),
            "bytes_received": utils.humanbytes(record.bytes_received),
        })
    return utils.print_table(out)
