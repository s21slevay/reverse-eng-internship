import torch

a = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(-3.0, requires_grad=True)
c = torch.tensor(10.0, requires_grad=True)

f = (a * b + c) ** 2
f.backward()

print(a.grad, b.grad, c.grad)  # expect -24, 16, 8