import functools
import json
from datetime import UTC, datetime, timedelta
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        self._args_check(critical_count, time_to_recover)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self._count_fails: int = 0
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            func_name = f"{func.__module__}.{func.__name__}"
            self._block_time_check(func_name)
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                self._except_process(func_name, error)
                raise
            else:
                self._count_fails = 0
                self._block_time = None
                return result

        return wrapper

    def _args_check(self, critical_count: int, time_to_recover: int) -> None:
        value_erros = []
        if not (isinstance(critical_count, int) and critical_count > 0):
            value_erros.append(ValueError(INVALID_CRITICAL_COUNT))
        if not (isinstance(time_to_recover, int) and time_to_recover > 0):
            value_erros.append(ValueError(INVALID_RECOVERY_TIME))

        if value_erros:
            raise ExceptionGroup(VALIDATIONS_FAILED, value_erros)

    def _block_time_check(self, func_name: str) -> None:
        if not self._block_time:
            return

        time_when_recover = self._block_time + timedelta(seconds=self.time_to_recover)
        if self._block_time and datetime.now(UTC) < time_when_recover:
            raise BreakerError(func_name, self._block_time)

    def _except_process(self, func_name: str, error: Exception) -> None:
        if not isinstance(error, self.triggers_on):
            return

        self._count_fails += 1
        if self._count_fails >= self.critical_count:
            self._block_time = datetime.now(UTC)
            raise BreakerError(func_name, self._block_time) from error


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
