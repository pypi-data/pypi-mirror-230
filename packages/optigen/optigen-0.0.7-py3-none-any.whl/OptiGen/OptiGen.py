import random

def get_mutation_rate_round_value(mutation_rate):
    mr_str = str(mutation_rate)

    if '.' in mr_str:
        decimal_index = mr_str.index('.')
        decimal_places = len(mr_str) - decimal_index - 1
        
        return decimal_places
    
    return 0

class Phenotype:
    def __init__(self, output_size):
        self.output_size = output_size
        self.solution = []

        for x in range(self.output_size):
            self.solution.append(random.randint(0, 1))

    def __str__(self):
        return str(self.solution)  # Return the list as a string
    
class calculate_fitness:
    def __init__(self, result, solution):
        self.result = result
        self.solution = solution
        self.score = 0

        for x in range(len(self.result)):
            if self.result[x] == self.solution[x]:
                self.score += 1 / len(self.solution)

class next_generation:
    def __init__(self, phenotypes, mutation_rate):
        self.phenotypes = phenotypes
        self.mutation_rate = mutation_rate

        self.new_generation = []

        for _ in range(len(self.phenotypes)):
            self.p1 = random.choice(self.phenotypes)
            self.p2 = random.choice(self.phenotypes)
            
            self.p1_solution = self.p1[1]
            self.p2_solution = self.p2[1]

            self.child = []

            # Determine the number of genes from each parent
            crossover_point = len(self.p1_solution) // 2

            # Create the child by combining genes from both parents
            self.child.extend(self.p1_solution[:crossover_point])
            self.child.extend(self.p2_solution[crossover_point:])

            # Apply mutation to the child
            for x in range(len(self.child)):
                if random.uniform(0, 1) <= mutation_rate:
                    self.child[x] = 1 - self.child[x]  # Toggle the gene value

            self.new_generation.append(self.child)
        

class start:
    def __init__(self, population_size, generations, output, mutation_rate=0.1):
        
        self.phenotypes = []

        for __ in range(population_size):

            self.result = Phenotype(len(output)).solution
            self.fitness = calculate_fitness(self.result, output)
            self.phenotypes.append([self.fitness.score, self.result])
        self.phenotypes.sort(reverse=True)
        print(f"Generation 0: Best score: {self.phenotypes[0]}")

        for gen in range(generations):
            self.next_phenotypes = next_generation(self.phenotypes, mutation_rate).new_generation
            self.phenotypes = []
            for x in self.next_phenotypes:
                self.fitness = calculate_fitness(x, output)
                self.phenotypes.append([self.fitness.score, x])  # Use 'x' for fitness calculation
            self.phenotypes.sort(reverse=True)
            
            print(f"Generation {gen+1}: Best score: {self.phenotypes[0]}")
            if self.phenotypes[0][0] >= 0.99:
                return

#start(100, 100000, [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
