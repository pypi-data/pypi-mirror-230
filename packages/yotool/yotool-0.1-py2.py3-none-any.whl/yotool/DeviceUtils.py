from pynvml import *
import os

class Device:
    """
    英伟达显卡设备信息
    """

    def __init__(self, did: int, name: str, total_memory: int, free_memory: int, used_memory: int, temperature: str,
                 powerStatus: int):
        self.did = did
        self.name = name
        self.total_memory = total_memory
        self.free_memory = free_memory
        self.used_memory = used_memory
        self.temperature = temperature
        self.powerStatus = powerStatus

    def get_name(self):
        return self.name

    def get_total_memory(self):
        return self.total_memory

    def get_free_memory(self):
        return self.free_memory

    def get_used_memory(self):
        return self.used_memory

    def __str__(self):
        def gatherAttrs():
            return ",".join("{}={}"
                            .format(k, getattr(self, k))
                            for k in self.__config.keys() if k != 'gid')

        return "Device {} {{{}}}".format(self.did, gatherAttrs())


def get_nvidia_info():
    """
    获取英伟达显卡的设备信息
    :return: 返回dict，存储英伟达显卡的设备信息
    """
    nvidia_dict = {
        "state": True,
        "nvidia_version": "",
        "nvidia_count": 0,
        "devices": []
    }
    try:
        nvmlInit()
        nvidia_dict["nvidia_version"] = nvmlSystemGetDriverVersion()
        nvidia_dict["nvidia_count"] = nvmlDeviceGetCount()
        for i in range(nvidia_dict["nvidia_count"]):
            handle = nvmlDeviceGetHandleByIndex(i)
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            device = Device(i, nvmlDeviceGetName(handle), memory_info.total, memory_info.free, memory_info.used,
                            f"{nvmlDeviceGetTemperature(handle, 0)}℃", nvmlDeviceGetPowerState(handle))
            nvidia_dict['devices'].append(device)
    except NVMLError as _:
        nvidia_dict["state"] = False
    except Exception as _:
        nvidia_dict["state"] = False
    finally:
        try:
            nvmlShutdown()
        except:
            pass
    return nvidia_dict


class DeviceUtil:
    """
    设备管理工具
    """

    info_info = "[DeviceUtils] "
    warning_info = "[DeviceUtils] Warning: "
    error_info = "[DeviceUtils] Error: "

    def __init__(self):
        self.nvidia_info = None
        self.refresh_nvidia_info()
        self.devices = self.nvidia_info['devices']

    def refresh_nvidia_info(self):
        """
        获取设备信息
        """
        self.nvidia_info = get_nvidia_info()

    def get_device_num(self) -> int:
        """
        获取设备数量
        :return: 设备数量
        """
        return len(self.devices)

    def device(self, gid: int) -> dict:
        """
        根据ID获取设备信息
        :param gid: 设备ID
        :return: 设备信息
        """
        if gid > len(self.devices):
            raise IndexError(self.info_info + "There is no Device:{}".format(gid))
        return self.devices[gid]

    def check_device_status(self, did: int, threshold: int = 5) -> bool:
        """
        检查设备状态。如果设备的显存使用小于阈值{threshold}，则认为是可用的。
        :param did: 设备ID
        :param threshold: 阈值
        :return: 是否可用
        """
        device = self.device(did)
        used, tot = device.get_used_memory(), device.get_total_memory()
        return (used / tot) * 100 < threshold

    def get_available_device(self, device_num: int = None, is_strict: bool = True, threshold: int = 5) -> Array:
        """
        获取可用设备的ID列表
        :param device_num: 获取设备数量，非空
        :param is_strict: 是否严格按照设备数量获取可用设备
        :param threshold: 设备可用状态阈值
        :return: ID列表
        """
        if device_num is None:
            device_num = self.get_device_num()
        available_device = []
        for gid in range(self.get_device_num()):
            if self.check_device_status(gid, threshold):
                available_device.append(gid)
                if len(available_device) == device_num:
                    break
        if len(available_device) < device_num:
            if is_strict:
                raise ValueError(
                    self.error_info + "Require {} devices, but only {} available devices.".format(
                        device_num, len(available_device)))
            print(
                self.warning_info + "Require {} devices, but only {} available devices.".format(
                    len(available_device), device_num))
        return available_device

    def train_on_devices(self, device_num: int, is_strict: bool = True, threshold: int = 5):
        """
        在特定数量设备上训练
        :param device_num: 设备数量
        :param is_strict: 是否严格按照设备数量获取可用设备
        :param threshold: 设备可用状态阈值
        """
        self.print()
        if device_num > self.get_device_num():
            raise ValueError(
                self.error_info + "Require {} devices, but only {} available devices.".format(
                    device_num,
                    self.get_device_num()))
        device = self.get_available_device(device_num, is_strict, threshold)
        device_ids = [str(gid) for gid in device]
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(device_ids)
        sent = "[DeviceUtils] Train on {} device(s): cuda:{}.".format(len(device_ids), ',cuda:'.join(device_ids))
        print(sent)

    def train_on_target_devices(self, device_ids: Array):
        """
        在指定设备上训练
        :param device_ids: 设备ID列表
        """
        if device_ids is None or len(device_ids) == 0:
            raise ValueError(
                self.error_info + "Param \'device_ids\' is empty.")
        for did in device_ids:
            if not isinstance(did, int):
                raise ValueError(
                    self.error_info + "Param \'device_ids\' has non-integer value {}.".format(did))
        device_ids = [str(id) for id in device_ids]
        self.print()
        if len(device_ids) > self.get_device_num():
            raise ValueError(
                self.error_info + "Require {} devices, but only {} available devices.".format(
                    len(device_ids),
                    self.get_device_num()))
        available_devices = self.get_available_device()
        available_device_ids = [str(gid) for gid in available_devices]
        for did in device_ids:
            if did not in available_device_ids:
                raise ValueError(
                    self.error_info + "Device:{} is not available. The required devices are {{{}}} while the available devices are {{{}}}.".format(
                        did,
                        ','.join(device_ids),
                        ','.join(available_device_ids)))
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(device_ids)
        sent = self.info_info + "Train on {} device(s): device:{}.".format(len(device_ids), ',device:'.join(device_ids))
        print(sent)

    def print(self):
        """
        打印设备信息
        """
        self.refresh_nvidia_info()
        print(
            "[DeviceUtils] Device Memory Usage:")
        for device_id, device_info in enumerate(self.nvidia_info['devices']):
            per = device_info.get_used_memory() / device_info.get_total_memory() * 100
            print("\r(%.f) %s [%s]%.2f%s" % (
                device_id, device_info.get_name(), '#' * int(per) + ' ' * int(100 - per), per, '%'), flush=False,
                  end='\n')


def train_on_devices(device_num: int, is_strict: bool = True, threshold: int = 5):
    """
    在特定数量设备上训练的函数修饰器
    :param device_num: 设备数量
    :param is_strict: 是否严格按照设备数量获取可用设备
    :param threshold: 设备可用状态阈值
    :return: 函数修饰器
    """
    if callable(device_num):
        raise ValueError(
            "Please use this function decorator with parameters.")

    def wrapper(func):
        def inner(*args, **kwargs):
            util = DeviceUtil()
            util.train_on_devices(device_num=device_num, is_strict=is_strict, threshold=threshold)
            func(*args, **kwargs)

        return inner

    return wrapper


def train_on_target_devices(device_ids: list):
    """
    在指定设备上训练的函数修饰器
    :param device_ids: 设备的ID列表
    :return: 函数修饰器
    """
    if callable(device_ids):
        raise ValueError(
            "Please use this function decorator with parameters.")

    def wrapper(func):
        def inner(*args, **kwargs):
            util = DeviceUtil()
            util.train_on_target_devices(device_ids=device_ids)
            func(*args, **kwargs)

        return inner

    return wrapper


# Test
@train_on_target_devices([2,3])
def test():
    import torch
    print(torch.cuda.device_count())
    print(torch.cuda.get_device_name(1))

if __name__ == "__main__":
    test()