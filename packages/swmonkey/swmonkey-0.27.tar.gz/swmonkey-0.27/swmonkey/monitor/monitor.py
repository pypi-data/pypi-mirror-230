import psutil
from swmonkey.log.log import logger
import time
from swmonkey.error import SystemUsageError

INTERVAL = 2


def monitor_system():
    '''
    监控monkey test执行过程中的系统资源变化,输出到日志
    '''
    cpu_usage = psutil.cpu_percent(interval=1)
    mem_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    net_info = psutil.net_io_counters()
    logger.info(
        f'CPU:  {cpu_usage}%; Memory: {mem_usage}%; Disk: {disk_usage}%; Net: {net_info.bytes_sent} bytes sent, {net_info.bytes_recv} bytes received')

    # 阈值告警
    if cpu_usage > 90:
        logger.warning(f'CPU usage is over 90%')
        raise SystemUsageError('CPU usage is over 90%')
    if mem_usage > 90:
        logger.warning(f'Memory usage is over 90%')
        raise SystemUsageError('Memory usage is over 90%')
    if disk_usage > 90:
        logger.warning(f'Disk usage is over 90%')
        raise SystemUsageError('Disk usage is over 90%')


def monkey_monitor():
    while True:
        monitor_system()
        time.sleep(INTERVAL)


if __name__ == '__main__':
    monkey_monitor()
    # Output: 'CPU:  0.0%; Memory: 0.0%; Disk: 0.0%; Net: 0 bytes sent, 0 bytes received
