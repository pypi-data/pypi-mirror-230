import random
import tkinter as tk

class Training_Data:
    def __init__(self):
        self.data = []
        self.original_data = []
        self.downsample_factor = 10

    def downsample_data(self, factor):
        return [self.original_data[i] for i in range(0, len(self.original_data), factor)]

    def plot_graph(self, canvas, data):
        canvas.delete("all")
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        max_x = len(data)
        
        canvas.create_line(40, canvas_height - 40, canvas_width - 40, canvas_height - 40)
        
        prev_x = None
        prev_y = None
        for i, value in enumerate(data):
            x = 40 + (i / max_x) * (canvas_width - 80)
            y = canvas_height - 40 - (value * (canvas_height - 80))
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")
            if prev_x is not None and prev_y is not None:
                canvas.create_line(prev_x, prev_y, x, y, fill="blue")
            prev_x = x
            prev_y = y
        
        canvas.create_text(20, canvas_height - 40, anchor="e", text="0.0")
        canvas.create_text(20, 20, anchor="e", text="1.0")
        canvas.create_text(20, canvas_height // 2, anchor="e", text="0.5")
        
        canvas.create_line(40, 20, 40, canvas_height - 40)
        canvas.create_line(40, canvas_height - 40, canvas_width - 40, canvas_height - 40) 
        
        for i in range(max_x):
            x_label = 40 + (i / max_x) * (canvas_width - 80)
            canvas.create_text(x_label, canvas_height - 20, anchor="n", text=str(i*self.downsample_factor))
    
    def update_graph(self, canvas):
        self.plot_graph(canvas, self.downsample_data(self.downsample_factor))

    def show_graph(self):
        def on_downsample_factor_change(value):
            self.downsample_factor = int(value)
            entry.delete(0, tk.END)
            entry.insert(0, str(self.downsample_factor))
            self.update_graph(canvas)

        def update_graph_after_typing(event):
            try:
                factor = int(entry.get())
                self.downsample_factor = factor
                slider.set(self.downsample_factor)
                self.update_graph(canvas)
            except ValueError:
                pass

        root = tk.Tk()
        root.title("Fitness")

        canvas = tk.Canvas(root, width=800, height=400)
        entry_label = tk.Label(root, text="Downsample Factor:")
        entry = tk.Entry(root)
        slider = tk.Scale(root, from_=1, to=len(self.original_data), orient="horizontal", command=on_downsample_factor_change)

        canvas.pack(fill=tk.BOTH, expand=True)
        entry_label.pack(pady=10)
        entry.pack()
        slider.pack()

        entry.insert(0, str(self.downsample_factor))

        canvas.bind("<Configure>", lambda event, canvas=canvas: self.update_graph(canvas))
        entry.bind("<KeyRelease>", update_graph_after_typing)

        self.update_graph(canvas)

        root.mainloop()

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

        total_fitness = sum(phenotype[0] for phenotype in self.phenotypes)

        for _ in range(len(self.phenotypes)):
            p1 = random.choices(self.phenotypes, weights=[phenotype[0] / total_fitness for phenotype in self.phenotypes])[0]
            p2 = random.choices(self.phenotypes, weights=[phenotype[0] / total_fitness for phenotype in self.phenotypes])[0]

            p1_solution = p1[1]
            p2_solution = p2[1]

            child = []

            crossover_point = len(p1_solution) // 2

            child.extend(p1_solution[:crossover_point])
            child.extend(p2_solution[crossover_point:])

            for x in range(len(child)):
                if random.uniform(0, 1) <= mutation_rate:
                    child[x] = 1 - child[x]

            child = Phenotype(len(child), child)

            self.new_generation.append(child)

if __name__ == "__main__":

    training_data = Training_Data()

    phenotypes = []

    output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    thresh_hold = 0.99
    population_size = 100
    mutation_rate = 0.001
    max_generations = 1000

    for __ in range(population_size):
        phenotype = Phenotype(len(output),[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        for x in range(len(phenotype.result)):
            if phenotype.result[x] == output[x]:
                phenotype.fitness += 1 / len(output)
        phenotypes.append([phenotype.fitness, phenotype.result])
    phenotypes.sort(reverse=True)
    print(f"Generation 0: Best score: {phenotypes[0]}")
    training_data.original_data.append(phenotypes[0][0])

    for gen in range(max_generations):
        next_phenotypes = next_generation(phenotypes, mutation_rate).new_generation
        phenotypes = []
        for x in next_phenotypes:
            phenotype = Phenotype(len(output), x.result)
            for y in range(len(phenotype.result)):
                if phenotype.result[y] == output[y]:
                    phenotype.fitness += 1 / len(output)
            phenotypes.append([phenotype.fitness, phenotype.result])
        phenotypes.sort(reverse=True)

        print(f"Generation {gen + 1}: Best score: {phenotypes[0][0]} Result: {phenotypes[0][1]}")
        training_data.original_data.append(phenotypes[0][0])
        if phenotypes[0][0] >= thresh_hold:
            break
    training_data.show_graph()