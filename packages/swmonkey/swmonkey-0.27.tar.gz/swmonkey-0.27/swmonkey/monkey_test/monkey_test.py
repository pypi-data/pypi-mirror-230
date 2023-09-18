import pyautogui
import random
import time
import os
import json
from swmonkey.util.util import KEY_NAMES
from swmonkey.data_structure.gui_action import GUIAction
from swmonkey.log.log import logger, get_out_dir
from swmonkey.monitor.monitor import monitor_system
pyautogui.FAILSAFE = False

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


class MonkeyTest():
    def __init__(self, duration):
        self.duration = duration
        self.out_path = get_out_dir()
        self.actions_json_file_path = os.path.join(
            self.out_path, 'actions.json')

    def run(self):
        self.monkey_test()

    def record_action(self, action):
        with open(self.actions_json_file_path, 'a') as f:
            f.write(json.dumps(action.__dict__) + '\n')

    def monkey_test(self):
        '''
        每次循环，随机生成一个动作，然后执行
        '''
        monitor_system()
        logger.info("Monkey started!")
        starttime = os.environ.get('START_TIME')
        assert starttime is not None
        start_time = float(starttime or time.time())

        while time.time() - start_time < self.duration:
            # Random mouse movement
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT - 1)

            if random.random() < 0.1:
                gui_action = GUIAction(
                    'click', time.time(), x, y, '', 'left', '')
            else:
                gui_action = GUIAction(
                    'double_click', time.time(), x, y, '', 'left', '')
            gui_action.execute()
            self.record_action(gui_action)

            # Random keypress
            if random.random() < 0.5:
                gui_action = GUIAction(
                    'key_press', time.time(), 0, 0, random.choice(KEY_NAMES), '', '')
            else:
                gui_action = GUIAction(
                    'write', time.time(), 0, 0, '', '', random.choice(KEY_NAMES))
            gui_action.execute()
            self.record_action(gui_action)
            time.sleep(0.5) # 为了避免频繁的操作，每次操作后sleep 0.5s
        logger.info("Monkey finished!")
