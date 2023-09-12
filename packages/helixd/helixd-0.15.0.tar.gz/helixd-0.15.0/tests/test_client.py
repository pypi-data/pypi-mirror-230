import subprocess
import time

import pytest

from helixd import ResourceType


def test_exists_storage_pool(client):
    config = {"name": "test-storage-pool"}

    assert not client.exists(config, ResourceType.STORAGE_POOLS)
    subprocess.run("lxc storage create test-storage-pool dir", shell=True)
    assert client.exists(config, ResourceType.STORAGE_POOLS)


def test_exists_volume(client):
    # first, checking for a volume without a storage pool shouldn't fail
    config = {"name": "test-volume", "parent": "test-storage-pool"}
    assert not client.exists(config, ResourceType.VOLUMES)

    subprocess.run("lxc storage create test-storage-pool dir", shell=True)  # given

    assert not client.exists(config, ResourceType.VOLUMES)
    subprocess.run("lxc storage volume create test-storage-pool test-volume", shell=True)
    assert client.exists(config, ResourceType.VOLUMES)


def test_exists_network(client):
    config = {"name": "test-network"}

    assert not client.exists(config, ResourceType.NETWORKS)
    subprocess.run("lxc network create test-network", shell=True)
    assert client.exists(config, ResourceType.NETWORKS)


def test_exists_profile(client):
    config = {"name": "test-profile"}

    assert not client.exists(config, ResourceType.PROFILES)
    subprocess.run("lxc profile create test-profile", shell=True)
    assert client.exists(config, ResourceType.PROFILES)


def test_exists_instance(client):
    config = {"name": "test-instance"}

    assert not client.exists(config, ResourceType.INSTANCES)
    subprocess.run("lxc launch test-instance --empty", shell=True)
    assert client.exists(config, ResourceType.INSTANCES)


CREATE_STORAGE_POOL_OUTPUT = """
creating /1.0/storage-pools/test-storage-pool
""".lstrip()


def test_create_storage_pool(client, capsys):
    config = {"name": "test-storage-pool", "driver": "dir"}

    client.create(config, ResourceType.STORAGE_POOLS)
    assert client.exists(config, ResourceType.STORAGE_POOLS)

    assert capsys.readouterr().out == CREATE_STORAGE_POOL_OUTPUT


CREATE_VOLUME_OUTPUT = """
creating /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
""".lstrip()


def test_create_volume(client, capsys):
    subprocess.run("lxc storage create test-storage-pool dir", shell=True)  # given

    config = {"name": "test-volume", "parent": "test-storage-pool"}

    client.create(config, ResourceType.VOLUMES)
    assert client.exists(config, ResourceType.VOLUMES)

    assert capsys.readouterr().out == CREATE_VOLUME_OUTPUT


CREATE_NETWORK_OUTPUT = """
creating /1.0/networks/test-network
""".lstrip()


def test_create_network(client, capsys):
    config = {"name": "test-network"}

    client.create(config, ResourceType.NETWORKS)
    assert client.exists(config, ResourceType.NETWORKS)

    assert capsys.readouterr().out == CREATE_NETWORK_OUTPUT


CREATE_PROFILE_OUTPUT = """
creating /1.0/profiles/test-profile
""".lstrip()


def test_create_profile(client, capsys):
    config = {"name": "test-profile"}

    client.create(config, ResourceType.PROFILES)
    assert client.exists(config, ResourceType.PROFILES)

    assert capsys.readouterr().out == CREATE_PROFILE_OUTPUT


CREATE_INSTANCE_OUTPUT = """
creating /1.0/instances/test-instance
""".lstrip()


def test_create_instance(client, capsys):
    config = {"name": "test-instance", "source": {"type": "none"}}

    client.create(config, ResourceType.INSTANCES)
    assert client.exists(config, ResourceType.INSTANCES)

    assert capsys.readouterr().out == CREATE_INSTANCE_OUTPUT


DELETE_STORAGE_POOL_OUTPUT = """
creating /1.0/storage-pools/test-storage-pool
deleting /1.0/storage-pools/test-storage-pool
""".lstrip()


def test_delete_storage_pool(client, capsys):
    config = {"name": "test-storage-pool", "driver": "dir"}

    client.create(config, ResourceType.STORAGE_POOLS)  # given

    client.delete(config, ResourceType.STORAGE_POOLS)
    assert not client.exists(config, ResourceType.STORAGE_POOLS)

    assert capsys.readouterr().out == DELETE_STORAGE_POOL_OUTPUT


DELETE_VOLUME_OUTPUT = """
creating /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
deleting /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
""".lstrip()


def test_delete_volume(client, capsys):
    # given
    subprocess.run("lxc storage create test-storage-pool dir", shell=True)
    config = {"name": "test-volume", "parent": "test-storage-pool"}
    client.create(config, ResourceType.VOLUMES)

    client.delete(config, ResourceType.VOLUMES)
    assert not client.exists(config, ResourceType.VOLUMES)

    assert capsys.readouterr().out == DELETE_VOLUME_OUTPUT


DELETE_NETWORK_OUTPUT = """
creating /1.0/networks/test-network
deleting /1.0/networks/test-network
""".lstrip()


def test_delete_network(client, capsys):
    config = {"name": "test-network"}

    client.create(config, ResourceType.NETWORKS)  # given

    client.delete(config, ResourceType.NETWORKS)
    assert not client.exists(config, ResourceType.NETWORKS)

    assert capsys.readouterr().out == DELETE_NETWORK_OUTPUT


DELETE_PROFILE_OUTPUT = """
creating /1.0/profiles/test-profile
deleting /1.0/profiles/test-profile
""".lstrip()


def test_delete_profile(client, capsys):
    config = {"name": "test-profile"}

    client.create(config, ResourceType.PROFILES)  # given

    client.delete(config, ResourceType.PROFILES)
    assert not client.exists(config, ResourceType.PROFILES)

    assert capsys.readouterr().out == DELETE_PROFILE_OUTPUT


DELETE_INSTANCE_OUTPUT = """
creating /1.0/instances/test-instance
deleting /1.0/instances/test-instance
""".lstrip()


def test_delete_instance(client, capsys):
    config = {"name": "test-instance", "source": {"type": "none"}}

    client.create(config, ResourceType.INSTANCES)  # given

    client.delete(config, ResourceType.INSTANCES)
    assert not client.exists(config, ResourceType.INSTANCES)

    assert capsys.readouterr().out == DELETE_INSTANCE_OUTPUT


TEST_INSTANCE_CONFIG = {
    "name": "test-instance",
    "profiles": ["default"],
    "source": {
        "type": "image",
        "mode": "pull",
        "server": "https://images.linuxcontainers.org",
        "protocol": "simplestreams",
        "alias": "ubuntu/jammy/cloud"
    }
}

IS_RUNNING_OUTPUT = """
creating /1.0/instances/test-instance
""".lstrip()


def test_is_running(client, capsys):
    client.create(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)

    assert not client.is_running(TEST_INSTANCE_CONFIG)
    subprocess.run("lxc start test-instance", shell=True)
    time.sleep(0.2)
    assert client.is_running(TEST_INSTANCE_CONFIG)

    assert capsys.readouterr().out == IS_RUNNING_OUTPUT


START_OUTPUT = """
creating /1.0/instances/test-instance
starting /1.0/instances/test-instance
""".lstrip()


def test_start(client, capsys):
    client.create(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)

    client.start(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)
    time.sleep(0.2)
    assert client.is_running(TEST_INSTANCE_CONFIG)

    assert capsys.readouterr().out == START_OUTPUT


STOP_OUTPUT = """
creating /1.0/instances/test-instance
starting /1.0/instances/test-instance
stopping /1.0/instances/test-instance
""".lstrip()


def test_stop(client, capsys):
    client.create(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)
    client.start(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)
    time.sleep(0.2)

    client.stop(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)
    assert not client.is_running(TEST_INSTANCE_CONFIG)

    assert capsys.readouterr().out == STOP_OUTPUT


def test_get_ip_address_ok(client, capsys):
    client.create(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)
    client.start(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)

    assert client.get_ip_address(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES).startswith("10.0.0.")


def test_get_ip_address_ko_not_started(client, capsys):
    client.create(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES)

    assert client.get_ip_address(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES) is None


def test_get_ip_address_ko_not_exists(client, capsys):
    assert client.get_ip_address(TEST_INSTANCE_CONFIG, ResourceType.INSTANCES) is None


def test_ko_create_sync(client):
    with pytest.raises(Exception) as exception:
        client.create({"name": "test-storage-pool"}, ResourceType.STORAGE_POOLS)

    assert str(exception.value) == "No driver provided"


def test_ko_create_async(client):
    with pytest.raises(Exception) as exception:
        client.create({"name": "test-instance", "source": {"type": "none"}, "devices": {"backup": {"type": "disk"}}}, ResourceType.INSTANCES)

    assert str(exception.value) == 'Failed creating instance record: Failed initialising instance: Invalid devices: Device validation failed for "backup": Disk entry is missing the required "source" or "path" property'
