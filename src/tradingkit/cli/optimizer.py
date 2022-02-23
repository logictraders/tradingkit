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

import multiprocessing as mp
import os.path


class Optimizer:

    def __init__(self):
        self.args = None
        self.param_names = []
        self.population_size = 10
        self.count = 0
        self.max_iterations = None
        self.max_iteration_without_improv = 10
        self.start_time = int(time.time())
        self.config = None

    def objective_function(self, genome, _results, i, results_data):
        self.count += 1
        total_profit = 0
        results = []
        results_ = []

        result = self.run_simulation(genome)

        if result['start_base_balance'] == 0:
            profit = (result['end_equity'] - result['start_equity']) / result['start_equity'] * 100
        else:
            profit = (result['base_balance'] - result['start_base_balance']) / result['start_base_balance'] * 100
        if result['end_equity'] > 0:

            results.append(profit)
            mdd_penalty = 1
            results_.append(profit * (1 - abs(result['max_drawdown'])) ** mdd_penalty)
        else:
            return np.random.uniform(-200, -100, 1)[0]
        total_profit += profit

        score = sum(results_)

        if score > 0:
            data = []
            data.append("  T prof:")
            data.append(round(total_profit, 2))
            data.append("%  ")
            data.append(score)
            data.append(" ")
            data.append(results)
            data.append(" MDD  ")
            data.append(result['max_drawdown'])
            data.append("   ")
            data.append(genome)
            data.append("      ")
            data.append(datetime.now())
            results_data[i] = data
        else:
            results_data[i] = None

        if _results is not None:
            _results[i] = score
        return score

    def run_simulation(self, genome):

        for i in range(len(self.param_names)):
            self.config['config'][self.param_names[i]] = genome[i]

        injector = ConfigInjector(self.config)
        feeder = injector.inject('feeder', Feeder)
        exchange = injector.inject('exchange', Exchange)
        plotter = injector.inject('plotter', Plotter)

        strategy = injector.inject('strategy', Strategy)
        bridge = injector.inject('bridge', Exchange)
        feeder_adapters = injector.inject('feeder_adapters', list)

        result = Runner.run(feeder, exchange, plotter, strategy, bridge, feeder_adapters, self.args['--optimize'],
                            self.args['--plot'])
        return result

    def get_config(self):
        config = json.loads(System.read_file("config/config.json"))
        strategy_dir = self.args['<strategy_dir>'] or '.'
        System.load_env(strategy_dir, self.args['--env'])
        main_conf = "%s/config/config.json" % os.path.abspath(strategy_dir)
        if os.path.exists(main_conf):
            config.update(json.load(open(main_conf, 'r')))
        env_conf = "%s/config/config.%s.json" % (os.path.abspath(strategy_dir), self.args['--env'])
        if os.path.exists(env_conf):
            config.update(json.load(open(env_conf, 'r')))
        return config

    def optimize(self, args):

        strategy_dir = args['<strategy_dir>'] or '.'
        route = "%s/config/config.json" % os.path.abspath(strategy_dir)
        if os.path.exists(route):
            config = json.load(open(route, 'r'))
        else:
            raise ValueError("The path: %s due not exist." % str(route))
        c_handle = open(strategy_dir + '/' + str(self.start_time) + "_out.csv", 'a')
        c_handle.close()
        varbound = []
        vartype = []
        for param in config['optimizer_config']:
            self.param_names.append(param)
            varbound.append([config['optimizer_config'][param]['from'], config['optimizer_config'][param]['to']])
            vartype.append([config['optimizer_config'][param]['type']])
        self.max_iterations = len(self.param_names) * 10
        self.args = args
        self.config = self.get_config()
        t = datetime.now()

        # first evaluation
        population = self.generate_population(varbound)
        score = {}

        manager = mp.Manager()
        process_list = [None] * self.population_size
        results_values = [None] * self.population_size
        results = manager.dict()
        results_data = manager.dict()

        i = 0
        for genome in population:
            process_list[i] = mp.Process(target=self.objective_function, args=(genome, results, i, results_data))
            process_list[i].start()
            results_values[i] = genome
            i += 1

        _t = datetime.now()
        for i in range(len(process_list)):
            process_list[i].join()
            score[results[i]] = results_values[i]
            if results_data[i] is not None:
                c_handle = open(strategy_dir + '/' + str(self.start_time) + "_out.csv", 'a')
                np.savetxt(c_handle, [results_data[i]], delimiter="  ", fmt="%s")
                c_handle.close()

        print("Iteration Time.: ", datetime.now() - _t)
        print("Lapsed Time.: ", datetime.now() - t)
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
            f_handle = open(strategy_dir + '/' + str(self.start_time) + "_best.csv", 'a')
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
                    f_handle = open(strategy_dir + '/' + str(self.start_time) + "_best.csv", 'a')
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
                if (type(bound[0]) == int and type(bound[1]) == int):
                    genome.append(np.random.randint(bound[0], bound[1]))
                else:
                    genome.append(np.random.uniform(bound[0], bound[1], 1)[0])
            population.append(genome)
        return population

    def mutate_and_evaluate(self, varbound, score, iteration):
        strategy_dir = self.args['<strategy_dir>'] or '.'
        new_score = {}
        i = 0
        manager = mp.Manager()
        process_list = [None] * self.population_size
        results_values = [None] * self.population_size
        results = manager.dict()
        results_data = manager.dict()
        for key, genome in sorted(score.items(), reverse=True):
            if i < self.population_size:
                new_score[key] = genome
                new_genome = genome.copy()
                index = np.random.randint(len(new_genome), size=1)[0]
                ratio = 1 - iteration / self.max_iterations
                print("ratio", ratio)
                adding = bool(np.random.choice([True, False]))
                if adding:
                    value = new_genome[index] + ratio * np.random.uniform(0, varbound[index][1] - new_genome[index], 1)[0]
                else:
                    value = new_genome[index] - ratio * np.random.uniform(0, new_genome[index] - varbound[index][0], 1)[0]
                if (type(new_genome[index]) == int):
                    value = int(value)
                new_genome[index] = value

                process_list[i] = mp.Process(target=self.objective_function, args=(new_genome, results, i, results_data))
                process_list[i].start()
                results_values[i] = new_genome

                i += 1
            else:
                # return new_score
                break
        _t = datetime.now()
        for i in range(len(process_list)):
            process_list[i].join()
            new_score[results[i]] = results_values[i]
            if results_data[i] is not None:
                c_handle = open(strategy_dir + '/' + str(self.start_time) + "_out.csv", 'a')
                np.savetxt(c_handle, [results_data[i]], delimiter="  ", fmt="%s")
                c_handle.close()

        print("Iteration Time: ", datetime.now() - _t)
        return new_score
