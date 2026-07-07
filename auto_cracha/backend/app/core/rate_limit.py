import time
from collections import defaultdict
from typing import Dict, List

JANELA_SEGUNDOS = 600  # 10 minutos
MAX_TENTATIVAS = 3

_tentativas: Dict[str, List[float]] = defaultdict(list)


def _tentativas_na_janela(chave: str) -> List[float]:
    agora = time.time()
    validas = [t for t in _tentativas[chave] if agora - t < JANELA_SEGUNDOS]
    _tentativas[chave] = validas
    return validas


def registrar_tentativa(chave: str) -> None:
    _tentativas_na_janela(chave)
    _tentativas[chave].append(time.time())


def tentativas_restantes(chave: str) -> int:
    return max(0, MAX_TENTATIVAS - len(_tentativas_na_janela(chave)))


def bloqueado_por_segundos(chave: str) -> int:
    tentativas = _tentativas_na_janela(chave)
    if len(tentativas) < MAX_TENTATIVAS:
        return 0
    mais_antiga = min(tentativas)
    return max(0, int(JANELA_SEGUNDOS - (time.time() - mais_antiga)))


def limpar(chave: str) -> None:
    _tentativas.pop(chave, None)
