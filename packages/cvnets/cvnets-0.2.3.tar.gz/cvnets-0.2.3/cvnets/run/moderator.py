import torch
from tqdm import tqdm


class Moderator():
    def __init__(self) -> None:
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            # self.device = torch.device("mps")
            self.device = "mps"
        else:
            self.device = "cpu"
        self.logs = {"train_loss": [], "test_loss": [], "test_correct": []}

    def train(self, dataloader, model, loss_fn, optimizer, stamp_itr=100):
        size = len(dataloader.dataset)
        model.train()
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(self.device), y.to(self.device)

            # Compute prediction error
            pred = model(X)
            loss = loss_fn(pred, y)

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % stamp_itr == 0:
                loss, current = loss.item(), batch * len(X)
                print(
                    f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]", end='\r')
        self.logs["train_loss"].append(loss.item())

    def test(self, dataloader, model, loss_fn, get_result=False):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0
        if get_result:
            y_true = []
            y_pred = []

        with torch.no_grad():
            for X, y in tqdm(dataloader, desc="test"):
                X, y = X.to(self.device), y.to(self.device)
                pred = model(X)
                test_loss += loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()

                if get_result:
                    y_true.extend(y.detach().cpu().numpy())
                    y_pred.extend(pred.argmax(1).detach().cpu().numpy())

        test_loss /= num_batches
        correct /= size
        print(
            f"Test : Accuracy: {(100*correct):>0.2f}%, Avg loss: {test_loss:>8f} \n")
        self.logs["test_loss"].append(test_loss)
        self.logs["test_correct"].append(correct)
        if get_result:
            return y_true, y_pred

    def get_log(self, log_name):
        if log_name in self.logs.keys():
            return self.logs[log_name]
        else:
            raise ValueError(
                f"'{log_name}' is not valid. Valid log names are {self.logs.keys()}")
