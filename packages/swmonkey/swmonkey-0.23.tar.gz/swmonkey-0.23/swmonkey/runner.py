import subprocess
import os
import argparse
import time

from swmonkey.log.log import logger


DURATION = 10  # Duration in seconds


def run_monkey_test():
    custom_env = {
        'DISPLAY': ':0',
    }
    existing_env = os.environ.copy()
    existing_env.update(custom_env)
    duration = int(os.getenv('DURATION'))
    # check child process status every 5 seconds
    starttime = float(os.environ.get('START_TIME'))
    while time.time() - starttime < duration:
        logger.info(f'[Main process] start swmonkey {starttime}')
        result = subprocess.Popen(
            ['swmonkey', '-d', f'{duration}', '--start-time', f'{starttime}'], env=existing_env)
        result.wait()
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
