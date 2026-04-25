"""Monitor leve em memória — coleta métricas de runtime para o painel do Admin."""
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict


class RuntimeMonitor:
    def __init__(self, max_recent: int = 50, max_errors: int = 25):
        self.iniciado_em: float = time.time()
        self.iniciado_iso: str  = datetime.now(timezone.utc).isoformat()

        self.total_requests:  int = 0
        self.por_status:      Dict[str, int] = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
        self.por_metodo:      Dict[str, int] = {}
        self.por_endpoint:    Dict[str, Dict[str, Any]] = {}
        self.duracoes_ms:     Deque[float] = deque(maxlen=500)
        self.recent_requests: Deque[dict]  = deque(maxlen=max_recent)
        self.recent_errors:   Deque[dict]  = deque(maxlen=max_errors)

        # Snapshot de logins / autenticações
        self.logins_sucesso:  int = 0
        self.logins_falha:    int = 0

    def registrar_request(self, metodo: str, path: str, status: int, dur_ms: float) -> None:
        self.total_requests += 1
        bucket = f"{status // 100}xx"
        self.por_status[bucket] = self.por_status.get(bucket, 0) + 1
        self.por_metodo[metodo] = self.por_metodo.get(metodo, 0) + 1

        endpoint_key = f"{metodo} {path}"
        ep = self.por_endpoint.get(endpoint_key)
        if not ep:
            ep = {"chamadas": 0, "soma_ms": 0.0, "max_ms": 0.0, "ultimos_status": []}
            self.por_endpoint[endpoint_key] = ep
        ep["chamadas"] += 1
        ep["soma_ms"]  += dur_ms
        if dur_ms > ep["max_ms"]:
            ep["max_ms"] = dur_ms

        self.duracoes_ms.append(dur_ms)
        self.recent_requests.append({
            "ts":     datetime.now(timezone.utc).isoformat(),
            "metodo": metodo,
            "path":   path,
            "status": status,
            "ms":     round(dur_ms, 2),
        })

        if status >= 500 or (status >= 400 and status not in (401, 403, 404)):
            self.recent_errors.append({
                "ts":     datetime.now(timezone.utc).isoformat(),
                "metodo": metodo,
                "path":   path,
                "status": status,
                "ms":     round(dur_ms, 2),
            })

    def registrar_login(self, sucesso: bool) -> None:
        if sucesso:
            self.logins_sucesso += 1
        else:
            self.logins_falha += 1

    def uptime_segundos(self) -> int:
        return int(time.time() - self.iniciado_em)

    def media_ms(self) -> float:
        if not self.duracoes_ms:
            return 0.0
        return sum(self.duracoes_ms) / len(self.duracoes_ms)

    def percentil(self, pct: float) -> float:
        if not self.duracoes_ms:
            return 0.0
        ordenados = sorted(self.duracoes_ms)
        idx = max(0, min(len(ordenados) - 1, int(len(ordenados) * pct) - 1))
        return ordenados[idx]

    def top_endpoints(self, n: int = 8) -> list:
        items = []
        for k, v in self.por_endpoint.items():
            metodo, path = k.split(" ", 1)
            items.append({
                "endpoint":  path,
                "metodo":    metodo,
                "chamadas":  v["chamadas"],
                "media_ms":  round(v["soma_ms"] / v["chamadas"], 2) if v["chamadas"] else 0,
                "max_ms":    round(v["max_ms"], 2),
            })
        items.sort(key=lambda x: x["chamadas"], reverse=True)
        return items[:n]

    def slow_endpoints(self, n: int = 5) -> list:
        items = []
        for k, v in self.por_endpoint.items():
            if not v["chamadas"]:
                continue
            metodo, path = k.split(" ", 1)
            items.append({
                "endpoint":  path,
                "metodo":    metodo,
                "media_ms":  round(v["soma_ms"] / v["chamadas"], 2),
                "max_ms":    round(v["max_ms"], 2),
                "chamadas":  v["chamadas"],
            })
        items.sort(key=lambda x: x["media_ms"], reverse=True)
        return items[:n]


# Instância global
monitor = RuntimeMonitor()
