# -*-coding:utf-8 -*-
"""
:创建时间: 2023/7/30 21:06
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division
import random
from abc import ABC, abstractmethod
from typing import Type, List


class Individual(ABC):
    @abstractmethod
    def fitness(self) -> float:
        pass

    @abstractmethod
    def mutate(self, mutation_amount: float) -> None:
        pass

    @abstractmethod
    def crossover(self, other: 'Individual') -> 'Individual':
        pass


class GeneticAlgorithm:
    def __init__(self,
                 individual_type: Type[Individual],
                 population_size: int,
                 mutation_strength: float,
                 death_rate: float) -> None:
        self.individual_type = individual_type
        self.population_size = population_size
        self.mutation_strength = mutation_strength
        self.death_rate = death_rate
        self.population: List = [self.individual_type() for _ in range(population_size)]

    def step(self) -> None:
        # 计算所有个体的适应度
        fitness_values: List[float] = self.fitness_values()
        # 获取最大适应度值
        max_fitness: float = max(fitness_values) if fitness_values else 1

        # 随机清除适应度较低的个体
        self.population = [individual for individual, fitness in zip(self.population, fitness_values)
                           if fitness / max_fitness > random.random() * self.death_rate]

        # 通过遗传操作生成新的个体来填补被清除的对象
        for _ in range(self.population_size - len(self.population)):
            # 随机选择两个父母
            parent1: Individual = self.population[random.randint(0, len(self.population) - 1)]
            parent2: Individual = self.population[random.randint(0, len(self.population) - 1)]
            # 进行交叉操作生成孩子
            child: Individual = parent1.crossover(parent2)
            # 所有的孩子都进行突变，突变的量由高斯随机数决定
            mutation_amount: float = random.gauss(0, self.mutation_strength)
            child.mutate(mutation_amount)
            # 将孩子添加到种群中
            self.population.append(child)

    def run(self, generations: int) -> None:
        for _ in range(generations):
            self.step()

    def fitness_values(self) -> List[float]:
        return [individual.fitness() for individual in self.population]

    def min_fitness(self) -> float:
        return min(self.fitness_values()) if self.population else 0

    def max_fitness(self) -> float:
        return max(self.fitness_values()) if self.population else 0

    def average_fitness(self) -> float:
        fitness_values = self.fitness_values()
        return sum(fitness_values) / len(fitness_values) if fitness_values else 0
