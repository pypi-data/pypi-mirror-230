import numpy as np
import torch
from torch.autograd import grad
from tqdm import tqdm


# generate random batches of data
def batch_generator(data, batch_size):
    n = len(data[0])
    while True:
        # shuffle the data and grab batches of batch_size
        shuffle_idx = np.random.permutation(n)
        data = (data[0][shuffle_idx], data[1][shuffle_idx])
        for i in range(0, n, batch_size)[:-1]:
            yield (data[0][i : i + batch_size], data[1][i : i + batch_size])

        # on the last round, fill empty slots from the front
        i = n // batch_size * batch_size
        yield (
            torch.cat((data[0][i:n], data[0][0 : i + batch_size - n])),
            torch.cat((data[1][i:n], data[1][0 : i + batch_size - n])),
        )


# training protocol
def IGA(
    model: torch.nn.Module,
    optimizer: torch.optim,
    criterion,
    data,
    num_epochs,
    batch_size,
    lamda,
    verbose=10,
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
):
    """A pytorch model training protocol to minimize variance in the gradients of the loss function
    across multiple environments. The goal is to optimize out of distribution performance by learning
    from the differences in data collection environments.

    Parameters:
    model (torch.nn.Module): neural network model to be trained/tuned
    optimizer (torch.optim): pytorch optimizer object such as torch.optim.SGD
    criterion (function): loss function for model evaluation
    data (list(torch.utils.Dataset)): a list of Datasets for each environment
    num_epochs (int): number of training epochs
    batch_size (int): number of data points per batch
    lamda (float): importance weight of inter-environmental variance
    verbose (int): number of iterations in each progress log
    device (torch.device): optional, torch.device object, defaults to 'cuda' or 'cpu'

    Returns:
    model (torch.nn.Module): updated torch model
    IGA_loss (float): ending loss value
    """
    n_environments = len(data)

    # initialize batch generators
    batch_generators = [batch_generator(environment, batch_size) for environment in data]
    num_batches = max([len(patient[0]) for patient in data]) // batch_size + 1

    # training loop
    for epoch in range(num_epochs):
        # one batch at a time (one 'epoch' is once thorugh the largest environment, the others will shuffle)
        for k in range(num_batches):
            losses = torch.zeros(n_environments)
            loss_grads = list()
            # iterate through the environments
            for i, environment in enumerate(tqdm(batch_generators, desc="Environments")):
                inputs, labels = next(environment)
                inputs = inputs.to(device)
                labels = labels.to(device)

                # get the loss in this environment and its gradient
                outputs = torch.squeeze(model(inputs))
                losses[i] = criterion(outputs, labels)
                optimizer.zero_grad()
                loss_grads.append(grad(losses[i], model.parameters(), retain_graph=True))

            # get the average loss across environments and its gradient
            env_loss = torch.mean(losses)
            optimizer.zero_grad()
            env_loss_grad = grad(env_loss, model.parameters(), retain_graph=True)

            # get the variance in loss gradients (for each set of model parameters)
            n_params = len(loss_grads[0])
            variances = torch.zeros(n_params)
            for j in range(n_params):
                variances[j] = sum(
                    [torch.norm(loss_grads[i][j] - env_loss_grad[j], 2) ** 2 for i in range(n_environments)]
                )
            variance = torch.mean(variances)

            # equation 6
            Loss = env_loss + lamda * variance

            # backward pass, step
            optimizer.zero_grad()
            Loss.backward()
            optimizer.step()

            if (k + 1) % verbose == 0:
                print(f"epoch [{epoch+1}/{num_epochs}], step {i+1}/{num_batches}, loss: {Loss.item():.4f}")

    return model, Loss.item()
