# MLxploit: AI/ML Exploitation Framework

This is a CLI of an exploitation framework for machine learning models.

## Status

- This project is heavily under development. Existing functionalities may change frequently.
- It's still alpha, so the result may not be correct.

<br />

## Usage

```sh
mlx --help
```

To list attacks, use **`list`** positional argument.

```sh
mlx list
```

### :boom: Adversarial Attack

Currently support only **Image Classification** models.  
Supported techniques are as follow:

- **FGSM (Fast Gradient Sign Method)**
- **LBFGS**

```sh
# Attack ML model from file path (`-m`)
mlx adv -m mymodel.pt

# Attack Hugging Face model (`-hf`)
mlx adv -hf owner/repo
```

### :boom: Membership Inference Attack

Currently support only **Image Classification** models.

```sh
# Attack ML model from file path (`-m`)
mlx mia -m mymodel.pt

# Attack Hugging Face model (`-hf`)
mlx mia -hf owner/repo
```

<br />

## Installation

### Using PIP

It's the easiest way to install **MLxploit** with **`pip`**.

```sh
pip install mlxploit
mlx --help
```

### From Source Code

If you want to install directly from this repository, execute the following commands.

```sh
git clone https://github.com/hideckies/mlxploit.git
cd mlxploit
poetry shell
poetry install
mlx --help
```

<br />

## Recommendations

- If you use **Hugging Face** model (**`--model-hf/-hf`**), the repository will be downloaded under **`~/.cache/huggingface/`** by default. This can put pressure on the space on your system.

If you're worried about the above, it's encourage to use **MLxploit** on **Google Colab**, **SageMaker**, etc.

