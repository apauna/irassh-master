import matplotlib as mpl
from pybrain.rl.agents import LearningAgent
from pybrain.rl.experiments import Experiment
from pybrain.rl.explorers import EpsilonGreedyExplorer
from pybrain.rl.learners import SARSA
from pybrain.rl.learners.valuebased import ActionValueTable

from irassh.rl import rl_state

from rl_env import HASSHEnv
from rl_task import HASSHTask

mpl.use('Agg')

import threading


class RL:
    def __init__(self):
        self.av_table = ActionValueTable(4, 5)
        self.av_table.initialize(0.1)

        learner = SARSA()
        learner._setExplorer(EpsilonGreedyExplorer(0.0))
        self.agent = LearningAgent(self.av_table, learner)

        env = HASSHEnv()

        task = HASSHTask(env)

        self.experiment = Experiment(task, self.agent)

    def go(self):
        global rl_params
        rl_state.rl_params = self.av_table.params.reshape(4, 5)[0]
        self.experiment.doInteractions(1)
        self.agent.learn()

        # pylab.pcolor(self.av_table.params.reshape(4,5).max(1).reshape(2,2))
        # pylab.savefig('/tmp/plot.png')


def rl_start_thread():
    t = threading.Thread(target=rl_run)
    # t.daemon = True
    t.start()


if __name__ == "__main__":
    rl_run()
