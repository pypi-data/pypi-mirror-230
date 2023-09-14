import subprocess
import os
import argparse
import time
from .main import run_monkey
import multiprocessing
from swmonkey.log.log import logger


DURATION = 10  # Duration in seconds


def run_monkey_test():
    duration = int(os.getenv('DURATION'))
    # check child process status every 5 seconds
    starttime = float(os.environ.get('START_TIME'))
    while time.time() - starttime < duration:
        logger.info(f'[Main process] start swmonkey {starttime}')
        # 使用multiprocessing的原因：
        #  1. subprocess.open在一些情况下会找不到swmonkey，原因未知
        #  2. multiprocess.Process 子进程会继承父进程的环境变量，不需要再传入
        p = multiprocessing.Process(target=run_monkey, args=(duration,), daemon=True)
        p.daemon = True
        p.start()
        p.join()
        if time.time() - starttime < duration:
            logger.info(
                "[Main process]Monkey test stopped unexpectedly, restarting...")
        time.sleep(3)
    logger.info("[Main process]Monkey test finished!")


def main():
    parser = argparse.ArgumentParser(
        description='A tool for monkey test on Linux GUI')

    parser.add_argument('-d', '--duration', type=int,
                        default=DURATION, help='Duration in seconds')
    args = parser.parse_args()

    duration = args.duration
    if duration is not None:
        os.environ['DURATION'] = str(duration)
    # 控制进程不需要传入starttime，默认为当前时间
    starttime = time.time()
    os.environ['START_TIME'] = str(starttime)

    run_monkey_test()


if __name__ == '__main__':
    main()
