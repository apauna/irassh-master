import os
import random
import time

import pygeoip

from irassh.rl import rl_state
from irassh.rl import rl
from irassh.actions import dao

RL = rl.RL()

class Action(object):
    def __init__(self, write):
        self.is_allowed = True
        self.write = write

    def process(self):
        """
        """

    def isPassed(self):
        return self.is_allowed

    def setPassed(self, passed):
        self.passed = passed

    def write(self, text):
        self.write(text)


class BlockedAction(Action):
    def __init__(self, write):
        super(BlockedAction, self).__init__(write)

        self.setPassed(False)

    def process(self):
        self.write("Blocked command!\n")


class DelayAction(Action):
    def process(self):
        time.sleep(3)
        self.setPassed(True)
        self.write("delay ...\n")


class AllowAction(Action):
    def process(self):
        self.setPassed(True)


class InsultAction(Action):
    def __init__(self, clientIp, write):
        super(InsultAction, self).__init__(write)

        self.clientIp = clientIp
        self.setPassed(False)

    def process(self):
        location = self.getCountryCode()
        self.write("Insult Message! IP= %s/location=%s\n" % (self.clientIp, location))
        self.write(dao.getIRasshDao().getInsultMsg(location) + "\n")

    def getCountryCode(self):
        path, file = os.path.split(__file__)
        file_name = os.path.join(path, "geo_ip.dat")
        print("Load geo_ip.dat from " + file_name)
        geo_ip = pygeoip.GeoIP(file_name)
        return geo_ip.country_code_by_addr(self.clientIp)


class FakeAction(Action):
    def __init__(self, command, write):
        super(FakeAction, self).__init__(write)

        self.command = command
        self.setPassed(False)

    def process(self):
        fake_output = dao.getIRasshDao().getFakeOutput(self.command)
        if fake_output is not None:
            self.write(fake_output + "\n")


class ActionGenerator(object):
    def generate(self):
        '''
        :return: action
        '''


class RandomActionGenerator(ActionGenerator):
    def generate(self):
        return random.randrange(0, 4)


class RlActionGenerator(ActionGenerator):
    def generate(self):
        print ("getAction start", rl_state.current_command)
        global RL
        RL.go()
        while True:
            if rl_state.rl_action is not None:
                print("********************", rl_state.rl_params)
                return rl_state.rl_action[0]
            else:
                print("action not foud. going to wait ....", rl_state.current_command)
                time.sleep(1)


class ActionFactory(object):

    def __init__(self, write, listener, generator):
        self.write = write
        self.listener = listener
        self.generator = generator
        pass

    def getAction(self, cmd, clientIp):
        action = self.generator.generate()
        self.listener.handle(action)
        if action == 0:
            return AllowAction(self.write)
        elif action == 1:
            return DelayAction(self.write)
        elif action == 2:
            return FakeAction(cmd, self.write)
        elif action == 3:
            return InsultAction(clientIp, self.write)
        elif action == 4:
            return BlockedAction(self.write)


class ActionValidator(object):
    def __init__(self, write, listener, generator):
        self.write = write
        self.listener = listener
        self.generator = generator
        pass

    def validate(self, cmd, clientIp):
        action = ActionFactory(self.write, self.listener, self.generator).getAction(cmd, clientIp)
        action.process()
        return action.isPassed()


class ActionPersister(object):
    def save(self, actionState, cmd):
        if "initial_cmd" in actionState.keys():
            print("Save next_cmd: " + cmd)
            actionState["next_cmd"] = cmd
            dao.getIRasshDao().saveCase(actionState)

        print("Save initial_cmd: " + cmd)
        actionState["initial_cmd"] = cmd


class ActionListener(object):
    def __init__(self, store):
        self.store = store
        pass

    def handle(self, action):
        self.store["action"] = action
