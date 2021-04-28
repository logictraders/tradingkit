import math
import time
from datetime import datetime
import json
import os
import numpy as np
from ccxt import Exchange

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.feeder import Feeder
from tradingkit.display.plotter import Plotter
from tradingkit.strategy.strategy import Strategy
from tradingkit.utils.config_injector import ConfigInjector
from tradingkit.utils.system import System


class Optimizer:

    def __init__(self):
        self.args = None
        self.param_names = []
        self.population_size = 10
        self.count = 0
        self.max_iterations = 100
        self.max_iteration_without_improv = 10
        self.start_time = time.time()

    def objective_function(self, genome):
        self.count += 1
        total_profit = 0
        results = []
        # select the dataset/s to optimize

        #2016
        since = datetime.fromisoformat("2016-01-01 00:00:00+00:00")
        to = datetime.fromisoformat("2017-01-01 00:00:00+00:00")
        result = self.run_simulation(since.isoformat(), to.isoformat(), genome)

        if result['start_base_balance'] == 0:
            profit = (result['end_equity'] - result['start_equity']) / result['start_equity'] * 100
        else:
            profit = (result['base_balance'] - result['start_base_balance']) / result['start_base_balance'] * 100
        if result['end_equity'] > 0:

            results.append(profit)
        else:
            return np.random.uniform(-200, -100, 1)[0]
        total_profit += profit

        # 2017
        since = datetime.fromisoformat("2017-01-01 00:00:00+00:00")
        to = datetime.fromisoformat("2018-01-01 00:00:00+00:00")
        result = self.run_simulation(since.isoformat(), to.isoformat(), genome)

        if result['start_base_balance'] == 0:
            profit = (result['end_equity'] - result['start_equity']) / result['start_equity'] * 100
        else:
            profit = (result['base_balance'] - result['start_base_balance']) / result['start_base_balance'] * 100
        if result['end_equity'] > 0:

            results.append(profit)
        else:
            return np.random.uniform(-200, -100, 1)[0]
        total_profit += profit

        # 2018
        since = datetime.fromisoformat("2018-01-01 00:00:00+00:00")
        to = datetime.fromisoformat("2019-01-01 00:00:00+00:00")
        result = self.run_simulation(since.isoformat(), to.isoformat(), genome)

        if result['start_base_balance'] == 0:
            profit = (result['end_equity'] - result['start_equity']) / result['start_equity'] * 100
        else:
            profit = (result['base_balance'] - result['start_base_balance']) / result['start_base_balance'] * 100
        if result['end_equity'] > 0:

            results.append(profit)
        else:
            return np.random.uniform(-200, -100, 1)[0]
        total_profit += profit

        # 2019
        since = datetime.fromisoformat("2019-01-01 00:00:00+00:00")
        to = datetime.fromisoformat("2020-01-01 00:00:00+00:00")
        result = self.run_simulation(since.isoformat(), to.isoformat(), genome)

        if result['start_base_balance'] == 0:
            profit = (result['end_equity'] - result['start_equity']) / result['start_equity'] * 100
        else:
            profit = (result['base_balance'] - result['start_base_balance']) / result['start_base_balance'] * 100
        if result['end_equity'] > 0:

            results.append(profit)
        else:
            return np.random.uniform(-200, -100, 1)[0]
        total_profit += profit


        median_result = np.median(results)
        min_result = min(results)
        result = (median_result + min_result * 7) / 8

        if result > 0:
            c_handle = open(str(self.start_time) + "_out.csv", 'a')
            data = []
            data.append(self.count)
            data.append("         T prof:")
            data.append(total_profit)
            data.append("%          ")
            data.append(genome.tolist())
            data.append("          ")
            data.append(datetime.now())
            data.append("   ")
            data.append(result)
            data.append(results)
            np.savetxt(c_handle, [data], delimiter="  ", fmt="%s")
            c_handle.close()
        return result

    def run_simulation(self, since, to, genome):
        config = json.loads(System.read_file("config/config.json"))
        strategy_dir = self.args['<strategy_dir>'] or '.'
        System.load_env(strategy_dir, self.args['--env'])

        main_conf = "%s/config/config.json" % os.path.abspath(strategy_dir)
        if os.path.exists(main_conf):
            config.update(json.load(open(main_conf, 'r')))

        env_conf = "%s/config/config.%s.json" % (os.path.abspath(strategy_dir), self.args['--env'])
        if os.path.exists(env_conf):
            config.update(json.load(open(env_conf, 'r')))

        config['since'] = since
        config['to'] = to
        for i in range(len(self.param_names)):
            config['config'][self.param_names[i]] = genome[i]

        injector = ConfigInjector(config)
        feeder = injector.inject('feeder', Feeder)
        exchange = injector.inject('exchange', Exchange)
        plotter = injector.inject('plotter', Plotter)

        strategy = injector.inject('strategy', Strategy)
        bridge = injector.inject('bridge', Exchange)
        feeder_adapters = injector.inject('feeder_adapters', list)

        result = Runner.run(feeder, exchange, plotter, strategy, bridge, feeder_adapters, self.args['--optimize'],
                            self.args['--plot'])
        return result

    def optimize(self, args):
        strategy_dir = args['<strategy_dir>'] or '.'
        route = "%s/config/config.json" % os.path.abspath(strategy_dir)
        if os.path.exists(route):
            config = json.load(open(route, 'r'))
        else:
            raise ValueError("The path: %s due not exist." % str(route))
        varbound = []
        vartype = []
        for param in config['optimizer_config']:
            self.param_names.append(param)
            varbound.append([config['optimizer_config'][param]['from'], config['optimizer_config'][param]['to']])
            vartype.append([config['optimizer_config'][param]['type']])
        self.args = args

        t = datetime.now()

        # first evaluation
        population = self.generate_population(varbound)
        score = {}

        for genome in population:
            genome = np.array(genome)

            _t = datetime.now()
            profit = self.objective_function(genome)
            print("Iteration Time: ", datetime.now() - _t)
            score[profit] = genome

        print("Lapsed Time: ", datetime.now() - t)

        print("Top 10 solutions:")
        best_sol = 0
        i = 0
        for key, value in sorted(score.items(), reverse=True):
            if i < 10:
                if i == 0:
                    best_sol = key
                print(i, key, value)
                i += 1

        # next n evaluations
        iteration_without_improv = 0
        for iteration in range(self.max_iterations):
            if iteration_without_improv > self.max_iteration_without_improv:
                break
            score = self.mutate_and_evaluate(varbound, score, iteration)

            print("Lapsed Time: ", datetime.now() - t)

            print(iteration, "Top 10 solutions:")
            f_handle = open(str(self.start_time) + "_best.csv", 'a')
            np.savetxt(f_handle, [[iteration]], delimiter="  ", fmt="%s")
            f_handle.close()
            i = 0
            for key, value in sorted(score.items(), reverse=True):
                if i < 10:
                    if i == 0:
                        if best_sol < key:
                            best_sol = key
                            iteration_without_improv = 0
                        else:
                            iteration_without_improv += 1
                    print(i, key, value)
                    f_handle = open(str(self.start_time) + "_best.csv", 'a')
                    np.savetxt(f_handle, [[key, value]], delimiter="  ", fmt="%s")
                    f_handle.close()
                    i += 1
        print("Start time:", t)
        print("End time:", datetime.now())

    def generate_population(self, varbound):
        population = []
        for i in range(self.population_size):
            genome = []
            for bound in varbound:
                genome.append(np.random.uniform(bound[0], bound[1], 1)[0])
            population.append(genome)
        return population

    def mutate_and_evaluate(self, varbound, score, iteration):
        new_score = {}
        i = 0
        for key, value in sorted(score.items(), reverse=True):
            if i < self.population_size:
                new_score[key] = value
                new_genome = value.tolist()
                index = np.random.randint(len(new_genome), size=1)[0]
                ratio = max(iteration - 10, 0)  # first 10 iterations use max mutation speed and decrease after
                new_genome[index] = (new_genome[index] * ratio +
                                     np.random.uniform(varbound[index][0], varbound[index][1], 1)[0]) / (ratio + 1)
                new_genome = np.array(new_genome)

                _t = datetime.now()
                profit = self.objective_function(new_genome)
                print("Iteration Time: ", datetime.now() - _t)

                new_score[profit] = new_genome
                i += 1
            else:
                return new_score

        return new_score


