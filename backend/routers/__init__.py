from routers.usuario import router as usuario
from routers.auth import router as auth
from routers.skills import router as skills
from routers.math import router as math
from routers.contracts import router as contracts

__all__ = ["usuario", "auth", "skills", "math", "contracts"]
