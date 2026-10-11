
"""Gerenciamento central de processos do Polvo Negro Live."""

import logging
import subprocess
import threading

logger = logging.getLogger(__name__)


class EngineManager:
    def __init__(self):
        self._processes = {}
        self._lock = threading.RLock()
        self._closed = False

    def register_process(self, process, name=None):
        """Registra somente um processo iniciado pelo aplicativo."""
        if process is None:
            return None

        with self._lock:
            if self._closed:
                self.stop_process(process)
                raise RuntimeError("O motor já foi encerrado.")

            key = id(process)
            self._processes[key] = {
                "process": process,
                "name": name or "processo",
            }

        return process

    def start_process(self, command, name=None, **kwargs):
        """Inicia e registra um processo filho."""
        with self._lock:
            if self._closed:
                raise RuntimeError("O motor já foi encerrado.")

            process = subprocess.Popen(command, **kwargs)
            self._processes[id(process)] = {
                "process": process,
                "name": name or "processo",
            }
            return process

    def stop_process(self, process, timeout=5):
        """Tenta encerrar o processo gradualmente."""
        if process is None:
            return

        try:
            if process.poll() is not None:
                return

            process.terminate()

            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                logger.warning(
                    "Processo não encerrou no prazo; finalizando."
                )
                process.kill()
                process.wait(timeout=timeout)

        except (OSError, ValueError):
            logger.exception("Erro ao encerrar processo.")

    def shutdown_all(self, timeout=5):
        """Encerra os processos registrados."""
        with self._lock:
            if self._closed:
                return

            self._closed = True
            processes = list(self._processes.values())
            self._processes.clear()

        for item in reversed(processes):
            process = item["process"]
            name = item["name"]

            logger.info("Encerrando componente: %s", name)
            self.stop_process(process, timeout=timeout)

    def shutdown(self, timeout=5):
        """Executa o encerramento geral."""
        self.shutdown_all(timeout=timeout)


engine = EngineManager()
