from enum import IntEnum, auto
from logging import Logger, getLogger
from typing import Any, Self

from clean_base.settings import LOGGER

from .either import Left, left


class ErrorCodes(IntEnum):
    # Default option
    UNDEFINED_ERROR = 0

    # Crud errors
    CREATION_ERROR = auto()
    FETCHING_ERROR = auto()
    UPDATING_ERROR = auto()
    DELETING_ERROR = auto()

    # Clean architecture errors
    EXECUTION_ERROR = auto()
    DTO_ERROR = auto()
    ENTITY_ERROR = auto()
    USE_CASE_ERROR = auto()
    LOCK_FILE_ERROR = auto()


class MappedErrors:
    """The base class for mapped errors.

    Attributes:
        __code (ErrorCodes): A enumerator representation of the error classes.
        __exp (bool): True if error was dispatched as part of the expected
            application behavior. False otherwise.
        __msg (Any): The string message to be propagated.
    """

    # ? ------------------------------------------------------------------------
    # ? CLASS PROPERTIES
    # ? ------------------------------------------------------------------------

    __code: ErrorCodes | None = None
    __exp: bool = True
    __msg: Any = None

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init__(
        self,
        msg: Any,
        exp: bool = False,
        code: ErrorCodes = ErrorCodes.UNDEFINED_ERROR,
        logger: Logger | None = None,
    ) -> None:
        self.msg = msg
        self.exp = exp
        self.code = code

        if logger is None:
            logger = getLogger(code.name)

        if exp is True:
            logger.error(msg)
        else:
            logger.exception(msg)

    def __call__(self) -> Left[Self]:
        return left(self)

    def __str__(self) -> str:
        return self.msg

    __repr__ = __str__

    # ? ------------------------------------------------------------------------
    # ? GETTERS AND SETTERS
    # ? ------------------------------------------------------------------------

    @property
    def code(self) -> ErrorCodes | None:
        return self.__code

    @code.setter
    def code(self, code: ErrorCodes) -> None:
        if not isinstance(code, ErrorCodes):
            raise ValueError(f"{code} is not a valid instance of ErrorCodes.")

        self.__code = code

    @property
    def msg(self) -> str:
        return self.__msg

    @msg.setter
    def msg(self, msg: str) -> None:
        if not isinstance(msg, str):
            raise ValueError(f"{msg} is not a string.")

        self.__msg = msg

    @property
    def exp(self) -> bool:
        return self.__exp

    @exp.setter
    def exp(self, exp: bool) -> None:
        if not isinstance(exp, bool):
            raise ValueError(f"{exp} is not a boolean.")

        self.__exp = exp

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def update_msg(self, msg: Any, prev: Any = None) -> str:
        base_msg = "MappedErrors({type} {code}): {{msg}}".format(
            type=type(self).__name__, code=self.code
        )

        updated_msg = base_msg.format(msg=self.__stringify_msg(msg))

        if prev:
            prev_error = self.__stringify_msg(prev)
            updated_msg = f"{prev_error}\n{updated_msg}"

        return updated_msg

    # ? ------------------------------------------------------------------------
    # ? PRIVATE METHODS
    # ? ------------------------------------------------------------------------

    def __stringify_msg(self, msg: Any) -> str:
        if isinstance(msg, str):
            return msg

        elif isinstance(msg, Exception):
            args = getattr(msg, "args")
            if len(args) > 0:
                args = [str(m) for m in args]
                return ". ".join(args)
            return str(msg)

        elif isinstance(msg, MappedErrors):
            return msg.msg

        else:
            return str(msg)


# ? ----------------------------------------------------------------------------
# ? CRUD LEVEL ERRORS
# ? ----------------------------------------------------------------------------


class CreationError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during record creation.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.CREATION_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


class DeletionError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during record deletion.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.DELETING_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


class FetchingError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during record fetching.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.FETCHING_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


class UpdatingError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during record updating.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.UPDATING_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


# ? ----------------------------------------------------------------------------
# ? ARCHITECTURE LEVEL ERRORS
# ? ----------------------------------------------------------------------------


class ExecutionError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during generic execution.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.EXECUTION_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


class DadaTransferObjectError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during DTO life cycle execution.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.DTO_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


class UseCaseError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during use-case execution.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.USE_CASE_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


class EntityError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during entity life cycle.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.ENTITY_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


# ? ----------------------------------------------------------------------------
# ? OTHER ERRORS
# ? ----------------------------------------------------------------------------


class LockFileError(MappedErrors):
    def __init__(
        self,
        msg: Any = "Error detected during use-case execution.",
        exp: bool = False,
        prev: Any = None,
        logger: Logger | None = None,
    ) -> None:
        self.code = ErrorCodes.LOCK_FILE_ERROR

        super().__init__(
            msg=self.update_msg(msg, prev),
            code=self.code,
            exp=exp,
            logger=LOGGER if logger is None else logger,
        )


# ? ----------------------------------------------------------------------------
# ? SETUP DEFAULT EXPORTS
# ? ----------------------------------------------------------------------------


__all__ = [
    "ErrorCodes",
    "MappedErrors",
    "CreationError",
    "DeletionError",
    "FetchingError",
    "UpdatingError",
    "ExecutionError",
    "UseCaseError",
    "InvalidArgumentError",
    "InvalidRecordInstanceError",
    "InvalidRepositoryError",
    "LockFileError",
]
