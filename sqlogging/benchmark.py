import time
from sqlogging import logging

elapsed = 0
n_iter = int(1e3)
n_cols = int(1e2)

columns = []
for i in range(n_cols):
    columns.append(f"col_{i}")
data = {}
for col in columns:
    data[col] = 1.0

logger = logging.create_logger(columns=columns)

for i in range(n_iter):
    start = time.monotonic()
    logger.info(data)
    elapsed += time.monotonic() - start

print()
print(f"{n_iter} rows")
print(f"{n_cols} columns")
print(f"{int(elapsed)} sec total write time")
print(f"{elapsed / n_iter} sec write time per row")
# ~6ms per row overhead
# ~9ms per row at 2000 columns
print(f"{elapsed / (n_iter * n_cols)} sec write time per element")

logger.delete()
