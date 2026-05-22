from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, code: int, message: str, status_code: int = 400):
        self.error_code = code
        super().__init__(status_code=status_code, detail={"code": code, "message": message, "data": None})


class ValidationError(AppError):
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(code=1001, message=message, status_code=422)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "未认证"):
        super().__init__(code=1002, message=message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "无权限"):
        super().__init__(code=1003, message=message, status_code=403)


class NotFoundError(AppError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=1004, message=message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "操作冲突"):
        super().__init__(code=1005, message=message, status_code=409)


class UsernameExistsError(AppError):
    def __init__(self):
        super().__init__(code=2001, message="用户名已存在", status_code=409)


class EmailExistsError(AppError):
    def __init__(self):
        super().__init__(code=2002, message="邮箱已存在", status_code=409)


class LoginError(AppError):
    def __init__(self):
        super().__init__(code=2003, message="用户名或密码错误", status_code=401)


class AccountLockedError(AppError):
    def __init__(self):
        super().__init__(code=2004, message="账户已锁定，请稍后再试", status_code=423)


class InternalError(AppError):
    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(code=9999, message=message, status_code=500)
