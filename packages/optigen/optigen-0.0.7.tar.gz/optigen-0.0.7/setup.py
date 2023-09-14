from setuptools import setup, find_packages

VERSION = '0.0.7'
DESCRIPTION = 'Genetic algorithms framework'

# Setting up
setup(
    name="optigen",
    version=VERSION,
    author="ShadowFlameFox",
    author_email="<shadow_flame_fox@web.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="""# Getting Started

OptiGen: A Python Genetic Algorithm Library

OptiGen is a Python library that simplifies the implementation of genetic algorithms for solving optimization problems. It provides a set of classes and functions to create, evolve, and evaluate populations of potential solutions.

## Installation
To use OptiGen, you can install it using pip:


`pip install optigen`

## Example Usage
Here's an example of how to use OptiGento evolve a population to match a predefined output pattern:

```
from OptiGen import next_generation, Phenotype

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
    print(f"Generation 0: Best score: { phenotypes[0]}")
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
```
Full Documentation: [GitHub](https://github.com/ShadowFlameFox/OptiGen/wiki/Documentation)""",
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'genetic', 'natural selection', 'algorithms', "optimation"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)