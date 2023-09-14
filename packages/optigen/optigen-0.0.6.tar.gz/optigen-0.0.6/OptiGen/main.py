import random

class Phenotype:
    def __init__(self, output_size, result=[]):
        self.output_size = output_size
        self.result = list(result)
        self.fitness = 0
        if not result:
            for x in range(self.output_size):
                self.result.append(random.randint(0, 1))

class next_generation:
    def __init__(self, population, mutation_rate):
        self.phenotypes = population
        self.mutation_rate = mutation_rate

        self.new_generation = []

        for _ in range(len(self.phenotypes)):
            self.p1 = random.choice(self.phenotypes)
            self.p2 = random.choice(self.phenotypes)
            
            self.p1_solution = self.p1[1]
            self.p2_solution = self.p2[1]

            self.child = []

            crossover_point = len(self.p1_solution) // 2

            self.child.extend(self.p1_solution[:crossover_point])
            self.child.extend(self.p2_solution[crossover_point:])

            for x in range(len(self.child)):
                if random.uniform(0, 1) <= mutation_rate:
                    self.child[x] = 1 - self.child[x]

            self.child = Phenotype(len(self.child),self.child)
                    

            self.new_generation.append(self.child)
        

if __name__ == "__main__":
    phenotypes = []
    output= [ 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

    for __ in range(10000):

        phenotype = Phenotype(len(output))
        for x in range(len(phenotype.result)):
            if phenotype.result[x] == output[x]:
                phenotype.fitness += 1 / len(output)
        phenotypes.append([phenotype.fitness, phenotype.result])
    phenotypes.sort(reverse=True)
    print(f"Generation 0: Best score: {phenotypes[0]}")

    for gen in range(1000):
        next_phenotypes = next_generation(phenotypes, 0.01).new_generation
        phenotypes = []
        for x in next_phenotypes:
            phenotype = Phenotype(len(output),x.result)
            for y in range(len(phenotype.result)):
                if phenotype.result[y] == output[y]:
                    phenotype.fitness += 1 / len(output)
            phenotypes.append([phenotype.fitness, phenotype.result])
        phenotypes.sort(reverse=True)
                
        print(f"Generation {gen+1}: Best score: {phenotypes[0]}")
        if phenotypes[0][0] >= 0.99:
            break

