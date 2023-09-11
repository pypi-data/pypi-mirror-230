import numpy as np

rmse = lambda x, xhat:np.sqrt(np.mean((x - xhat) ** 2, axis = 1)) if len(xhat.shape)==2 else np.sqrt(np.mean((x - xhat) ** 2))
mse = lambda x, xhat:np.mean((x - xhat) ** 2, axis = 1) if len(xhat.shape)==2 else np.mean((x - xhat) ** 2)
mae = lambda x, xhat:np.mean(np.abs(x - xhat), axis = 1) if len(xhat.shape)==2 else np.mean(np.abs(x - xhat))
