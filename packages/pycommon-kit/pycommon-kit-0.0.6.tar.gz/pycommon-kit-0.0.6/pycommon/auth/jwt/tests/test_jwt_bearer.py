from pydantic import BaseModel

from pycommon.auth.jwt.jwt_bearer import JWTBearer


class TokenData(BaseModel):
    user_id: int


test_subject = JWTBearer(jwt_token_secret="supersecret",
                         token_data=TokenData)


def test_encode_and_then_decode_token():
    mock_payload = {"user_id": 100}
    assert test_subject.decode_jwt_token(test_subject.encode_jwt_token(mock_payload)).data.user_id == mock_payload["user_id"]
    assert isinstance(test_subject.decode_jwt_token(test_subject.encode_jwt_token(mock_payload)).data, TokenData)
