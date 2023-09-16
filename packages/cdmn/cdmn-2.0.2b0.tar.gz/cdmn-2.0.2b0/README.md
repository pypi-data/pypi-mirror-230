# cDMN

## Welcome to the cDMN solver's code repository.

cDMN stands for Constraint Decision and Model Notation.
It is an extension to the [DMN](https://www.omg.org/spec/DMN/About-DMN/) standard, managed by the Object Management Group (OMG).
cDMN combines the readability and straighforwardness of DMN and the expressiveness and flexibility of constraint reasoning.
For more specific details, please visit our [cDMN documentation](https://cdmn.readthedocs.io/en/latest/notation.html).

## Examples

Example implementations can also be found in the [cDMN documentation](https://cdmn.readthedocs.io/en/latest/examples.html).

## Installation and usage

The full installation and usage guide for the cDMN solver can be found [here](https://cdmn.readthedocs.io/en/latest/solver.html).
In short for Linux: after cloning this repo, install the Python dependencies.

```
git clone https://gitlab.com/EAVISE/cdmn/cdmn-solver
cd cdmn-solver
pip3 install -r requirements.txt
```

After this, you can run the solver. Example usage is as follows:

```
python3 -O solver.py Name_Of_XLSX.xlsx -n "Name_Of_Sheet" -o output_name.idp
```

## Reference

If you used cDMN in a publication or in other works, reference us as follows:

BibTeX:
```

@article{cDMN,
  title = {Tackling the {{DM}} Challenges with {{cDMN}}: {{A}} Tight Integration of {{DMN}} and Constraint Reasoning},
  author = {Vandevelde, Simon and Aerts, Bram and Vennekens, Joost},
  year = {2021},
  journal = {Theory and Practice of Logic Programming},
  pages = {1--24},
  publisher = {{Cambridge University Press}},
  doi = {10.1017/S1471068421000491}
}


```

or direct cite:

```
Vandevelde, S., Aerts, B., & Vennekens, J. (2021). Tackling the DM challenges with cDMN: A tight integration of DMN and constraint reasoning. Theory and Practice of Logic Programming, 1–24. https://doi.org/10.1017/S1471068421000491

```

# Contributors

We would also like to thank all contributors who have developed code or given suggestions to us, such as Marjolein Deryck, Pierre Carbonnelle, Jo Devriendt, and many more!
