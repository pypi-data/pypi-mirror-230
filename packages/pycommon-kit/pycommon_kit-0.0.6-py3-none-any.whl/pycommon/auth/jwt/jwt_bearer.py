from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from pycommon.utils.result import Result


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        jwt_token_secret: str,
        token_data: BaseModel,
        jwt_algorithm: str = "HS256",
        jwt_token_expire_in_minute: int = 30,
        auto_error: bool = True,
        logger=None,
    ):
        """JWTBearer auth class.

        Args:
            jwt_token_secret (str): secret word for encoding.
            token_data (BaseModel): class with payload based on BaseModel.
            jwt_algorithm (str, optional): Encryption algorithm Default is "HS256".
            jwt_token_expire_in_minute (int, optional): Time to token`s life. Default is 30.
            auto_error (bool, optional): related to HttpBearer.auto_error. Default is True.
            logger (Any, optional): logger object with method error. Default is None.
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.jwt_token_secret = jwt_token_secret
        self.token_data = token_data
        self.jwt_algorithm = jwt_algorithm
        self.jwt_token_expire_in_minute = jwt_token_expire_in_minute
        self.logger = logger

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            decode_token_result = self.decode_jwt_token(
                credentials.credentials, self.jwt_token_secret
            )
            if decode_token_result.is_failure():
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return decode_token_result.data
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def encode_jwt_token(self, payload: dict) -> str:
        """create JWT token with payload.

        Args:
            payload (dict): data to encode.

        Returns:
            str: encoded JWT token.
        """
        to_encode = payload.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_token_expire_in_minute)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.jwt_token_secret, algorithm=self.jwt_algorithm
        )
        return encoded_jwt

    def decode_jwt_token(self, token: str) -> Result:
        """Retrieve payload from token.

        Args:
            token (str): encrypted JWT token

        Returns:
            Result[TokenData]: TokenData (token_data) is class based on pydantic.BaseModel.
        """
        try:
            payload = jwt.decode(
                token, self.jwt_token_secret, algorithms=[self.jwt_algorithm]
            )
            del payload["exp"]
            token_data = self.token_data(**payload)
            return Result.success(data=token_data)
        except JWTError as error:
            self.__log_error(str(error))
            return Result.failure(error="Token is invalid.")

    def __log_error(self, error: str) -> None:
        if self.logger:
            try:
                self.logger.error(error)
            except Exception:
                return
        return
