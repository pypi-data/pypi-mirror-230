"""
Example Access Token:
eyJraWQiOiJqWnd6VW0xOUtOOWplK1ZpVjBLeEdvUW5kemZQXC9FVTBrVzlONzA0NEVWVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwYmRkMzQxYy0yODFmLTRlNTEtYWEzNy01MDI5MTU3NDkwNDMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9zOHBIMkt4T1AiLCJjbGllbnRfaWQiOiIydmRmOTh2cWVwb2VlMTRocXBjODQ4NmFsZSIsIm9yaWdpbl9qdGkiOiIyMzIyYmYzYi0xOTI2LTRjM2UtYmI5ZS05N2YzMmM0YTA2NWMiLCJldmVudF9pZCI6ImFkNzQ5MzQ2LTlkMGMtNDYzOC04MzMxLWViMGMyNjY3OTMyZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTcwOTgxMTgsImV4cCI6MTY1NzEwMTcxOCwiaWF0IjoxNjU3MDk4MTE4LCJqdGkiOiIxZjc2OGFkNy0wNzI3LTQ2MWYtYTJhMC00MjQzNzM5ZTZjM2EiLCJ1c2VybmFtZSI6ImZhYmlhbiJ9.g9Gz-AzAgKhVxec_faSPnhVbBFEeqeg4XaGtWPe9TgusiFkWQmQp6nBMkZAPEOIxcYJd7MFyFtv6vhPsz6PgmrXQN-FqHZ4eEvmbjJEZej-9iu535Rft5BtfIpTswqdBAUggBd9hcCqgCJgCn8nJ9PpYledPskI_7uzTxaZOkhtsoeMfr6BT8gpjHoN0GjKWN9FBLeqtN-miI_FoF4OxKfO9hPzeF0n89MkR85FNPsB8FpkwEMZe7D4fVCBreZxrc9vA8kecU9_1D2AjPujODndKn-E5tXfSufrKK2Fj7JJ51F_v1Gk8BFe6fx50dxi3-smSm0VxU7nq7MDf8L9UbQ  # noqa

Corresponding Refresh Token:
eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.Ukk0wBed6TUAIxTrUpxCNwjiglcHc2YNaH0wAsZFZSDrywYn3H0gu-vfPEp4E6z47KPEuJiQBFsCQTXZLmYS3GCJQrw3EpV8QwL5-gdqdgseCrsYjGBgStkRNTP-QqH8_EbJb5L6j0u5qYMn6MWjkCGpK_5A4N7TQ4eLCdPMxMOWTAJRJs6pvc0birVtTq6qmAAjLIVlGMz1b2DwQ89qIE950AzbSJ3uSiAOU0Q9EgEghNAgsRg6b7So202xqkwI98FjgovwG6VhvvEFlOUieH0ZTF7tQSj3ATyb33QlhSh21wjddLd_T1pomPEML5Gj7PslUA_4hxYScksVvoF4Qg.ktbthM0IS218Qqrl.d8mkGvTo9c-PYDQ1Aqd3xFwuVvi_2m0CNOPAjmyWwQQ1pFcWMbVuTIz2h6fP3OITYdHxL2TlAMpEeuE6lKJzI_dRv8YEEii-rnSLp_2Y8QZekT-b8ZLt6ByQqalVIMVXxhbooABP8qQjEPXxd4gsWSTrvgbI94ENlXb5SrqQl2X4NN5RFy_Ag6BhOZyZzc98Xa05kSBAn4EDIrAoxPmFprBMy8EUZuJ2z7WyAOuQAkH2Au14DcD8VpsZ3xgUBoWQ62rNjZovXnQLoLn1kMnWrPW51clYp0-9D6NOqVp7Bpm7UdID65hGf56o7rdGE1bM_X94DeeeDD94DNVTdy9jdxsL4oW216QPLS-p7NrDJVgDuIqWN_dJUzWJRLuQb5it_KTdGp5-ddWVtYqn0LUxZ0k0cn8sES-0D2o-DYwEcUHx3e9fbCXymdmKkMcDCB2pvCVpM7C_BhcIUKpHZ-7Z4xVncLKD2fd-PCzGULHwdrHnpFuqSJbDtURR9DO8RDhrQIy3l7jVB9CPXF41GycG5G_S9hEMD_C4wxFYKNTsr2zlpspCsQk22PtONrqkNgnnqglPSaBX6MMLzRztMARD2VblxRc4udt6X7cSXmtho1sFRpQKpoQpagHhG0adiXnb-6k9LI4-mFRJI4qFL_DNqcgPn8Bqhdj_4f5g4vF_LGkTSLgunel71DcXmY3W7TpjFUgvwWs8jc7F1W4Pe2xAXCdLvf1EPA2bIXEsMBv-Q89DNHG-VIsR_MzkbYUioJpRBCjWOpLGaNVC4fQ_lkBuBYmvZP7SU7ZR2AJFvT7DVHvUUAPhz_4dprwVV4Znq_r0cZDDmyVIi9QOZxDB17O2rVUCadtPNYU07UF-BE-3IjdI5VCotzf4PQnN486HneMDbb-hh2cD0ZNeEiGUuFrrwHNjSCL3NsSKoLbAOkQbwK6soUbxMk3x-ooS-gPsxbNh9a7b9qtwxH5nOFEKPRcFFehKsdKYB2g4CeuGRwVwgOqXshNojZEuRMt4x0qOrZsUBlcvdtfnuagqquaNGHRxnZ1-cYlKszxZ38q-jC6jKMmbqTb_DUDFgv3eYit7uB6OOLO8gW9G9fLYeRNpeOR4x-zS7pTClvoGGvYtjAPJAvNAxMmXNe4pXrX1mNTrHUjv8uThGoMSHzF1AwHvZLgtO6xj8GbgdnWNr2fVKP_bZczNSXRLYSQ03c65UFI4r1RPde-Zt2zIRJgywxBkgKZodCCtQ2BRlvKGr4KpUFh530nZeJis0or1BirrA7rr3u--9VMcAA6RSaaZdd8N.KwiXuNdKy9Jn2D8uapwVJg  # noqa


Header:
{
  "kid": "jZwzUm19KN9je+ViV0KxGoQndzfP/EU0kW9N7044EVU=",
  "alg": "RS256"
}

Payload:
{
  "sub": "0bdd341c-281f-4e51-aa37-502915749043",
  "iss": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_s8pH2KxOP",  # noqa
  "client_id": "2vdf98vqepoee14hqpc8486ale",
  "origin_jti": "2322bf3b-1926-4c3e-bb9e-97f32c4a065c",
  "event_id": "ad749346-9d0c-4638-8331-eb0c2667932f",
  "token_use": "access",
  "scope": "aws.cognito.signin.user.admin",
  "auth_time": 1657098118,
  "exp": 1657101718,
  "iat": 1657098118,
  "jti": "1f768ad7-0727-461f-a2a0-4243739e6c3a",
  "username": "fabian"
}

Issuer jwks.json file:
{
  "keys":[
    {
      "alg":"RS256",
      "e":"AQAB",
      "kid":"fG9ZI3zslGG8GH308l93bYedOYvON1Kqj/FeCmXIAZM=",
      "kty":"RSA",
      "n":"tC4LJ_vPuCf4qFkk6wXYpUb_qfnT17lnXMYQfTV3MZxXE7z6oG3SffjwYRw2RcFVO1QCIs_Lqc_03fLQB5fQp8_nQtZYTXeTGmO_6WyfcUmSS_GmISnbGbmaOQJCr8dSt06Xd3L4oqg47A5Zy7JesSP7AiVpZk-7o0Zi-S-aIpDr2fZa5bUar0hrJdETKuPMY2Kio9HY1VDGqAnLdtkhvxEYB3jNa3XLAJ4p2ZEMakJHhsIm84iGXBuxo4S1oNL1O8RP9awN6dr_5YuYLcENPOZ_OBb9fes9goAVedhfdflGB5swWVGNUEMBB8ElgFKC4IxELNbJ7XopzMCVTpJX3Q",  # noqa
      "use":"sig"
    },
    {
      "alg":"RS256",
      "e":"AQAB",
      "kid":"jZwzUm19KN9je+ViV0KxGoQndzfP/EU0kW9N7044EVU=",
      "kty":"RSA",
      "n":"rP7xiJVMB1xnutn9QX0cD0CzoVx64zWUyeOo4c0Ed1I6Mu0R0Borwqoh_u6cJd7PBYlnTme4k_ueEDm7Z4w-m-89igM5_0oo0jionmFwCuWmShjoH1dJ2J6lb9v52jiVzQV2rIqlWx2Gkq3IuwgrDIg_11BY1X0lyGhuygncp3z-tRUmnB3kcdkO_gddUyI8Uhb20g1ypeTwx-FzWGPVOXAMaAeDMOak33pWzVVzR3zAvrcw6BHVgr3gwU7nPxq5TlD_d8lhYI7NvS16aML_OQsBvoJCCXAxf4j9g3MicUWAFSysLRaTCAkxHbrKOvFdEJ9k64G3sdbCTJf5J3MAWQ",  # noqa
      "use":"sig"
    }
  ]
}
"""
import datetime
import typing as t

import mantik.mlflow_server.tokens as tokens
import mantik.mlflow_server.tokens.cognito as _cognito
import mantik.mlflow_server.tokens.jwks as _jwks

FAKE_JWT = "eyJraWQiOiJqWnd6VW0xOUtOOWplK1ZpVjBLeEdvUW5kemZQXC9FVTBrVzlONzA0NEVWVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwYmRkMzQxYy0yODFmLTRlNTEtYWEzNy01MDI5MTU3NDkwNDMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9zOHBIMkt4T1AiLCJjbGllbnRfaWQiOiIydmRmOTh2cWVwb2VlMTRocXBjODQ4NmFsZSIsIm9yaWdpbl9qdGkiOiIyMzIyYmYzYi0xOTI2LTRjM2UtYmI5ZS05N2YzMmM0YTA2NWMiLCJldmVudF9pZCI6ImFkNzQ5MzQ2LTlkMGMtNDYzOC04MzMxLWViMGMyNjY3OTMyZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTcwOTgxMTgsImV4cCI6MTY1NzEwMTcxOCwiaWF0IjoxNjU3MDk4MTE4LCJqdGkiOiIxZjc2OGFkNy0wNzI3LTQ2MWYtYTJhMC00MjQzNzM5ZTZjM2EiLCJ1c2VybmFtZSI6ImZhYmlhbiJ9.g9Gz-AzAgKhVxec_faSPnhVbBFEeqeg4XaGtWPe9TgusiFkWQmQp6nBMkZAPEOIxcYJd7MFyFtv6vhPsz6PgmrXQN-FqHZ4eEvmbjJEZej-9iu535Rft5BtfIpTswqdBAUggBd9hcCqgCJgCn8nJ9PpYledPskI_7uzTxaZOkhtsoeMfr6BT8gpjHoN0GjKWN9FBLeqtN-miI_FoF4OxKfO9hPzeF0n89MkR85FNPsB8FpkwEMZe7D4fVCBreZxrc9vA8kecU9_1D2AjPujODndKn-E5tXfSufrKK2Fj7JJ51F_v1Gk8BFe6fx50dxi3-smSm0VxU7nq7MDf8L9UbQ"  # noqa
FAKE_JWT_INVALID_SIGNATURE = "eyJraWQiOiJqWnd6VW0xOUtOOWplK1ZpVjBLeEdvUW5kemZQXC9FVTBrVzlONzA0NEVWVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwYmRkMzQxYy0yODFmLTRlNTEtYWEzNy01MDI5MTU3NDkwNDMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9zOHBIMkt4T1AiLCJjbGllbnRfaWQiOiIydmRmOTh2cWVwb2VlMTRocXBjODQ4NmFsZSIsIm9yaWdpbl9qdGkiOiIyMzIyYmYzYi0xOTI2LTRjM2UtYmI5ZS05N2YzMmM0YTA2NWMiLCJldmVudF9pZCI6ImFkNzQ5MzQ2LTlkMGMtNDYzOC04MzMxLWViMGMyNjY3OTMyZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTcwOTgxMTgsImV4cCI6MTY1NzEwMTcxOCwiaWF0IjoxNjU3MDk4MTE4LCJqdGkiOiIxZjc2OGFkNy0wNzI3LTQ2MWYtYTJhMC00MjQzNzM5ZTZjM2EiLCJ1c2VybmFtZSI6ImZhYmlhbiJ9.G9Gz-AzAgKhVxec_faSPnhVbBFEEqeg4XaGtWPe9TgUsiFkWQmQp6nBMkZAPEOIxcYJd7MFyFtv6vhPsZ6PgmrXQN-FqHZ4eEvmbjJEZej-9iu535Rft5BtfIpTswqdBAUggbd9hcCqgCJgCn8nJ9PpYledPskI_1uzTxaZOkhtsoeMfr6BT0gpjHoN0GjKWN9FBLeqtN-LiI_FoF4OxKfO9hPzeF0n89MkR85FNPsB8FpkwEMZe7D4fVCBreZxrc9vA8kecU9_1D2AjPujODndKn-E5tXfSufrKK2Fj7JJ51F_v1Gk8BFe6fx50dxi3-smSm0VxU7nq7MDf8L9UbQ"  # noqa
FAKE_JWT_INVALID_CLIENT_ID = "eyJraWQiOiJqWnd6VW0xOUtOOWplK1ZpVjBLeEdvUW5kemZQL0VVMGtXOU43MDQ0RVZVPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwYmRkMzQxYy0yODFmLTRlNTEtYWEzNy01MDI5MTU3NDkwNDMiLCJpc3MiOiJodHRwczovL2NvZ25pdG8taWRwLmV1LWNlbnRyYWwtMS5hbWF6b25hd3MuY29tL2V1LWNlbnRyYWwtMV9zOHBIMkt4T1AiLCJjbGllbnRfaWQiOiIydmRmOTh2cWVwb0VlMTRocVBjODQ4NmFsZSIsIm9yaWdpbl9qdGkiOiIyMzIyYmYzYi0xOTI2LTRjM2UtYmI5ZS05N2YzMmM0YTA2NWMiLCJldmVudF9pZCI6ImFkNzQ5MzQ2LTlkMGMtNDYzOC04MzMxLWViMGMyNjY3OTMyZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTcwOTgxMTgsImV4cCI6MTY1NzEwMTcxOCwiaWF0IjoxNjU3MDk4MTE4LCJqdGkiOiIxZjc2OGFkNy0wNzI3LTQ2MWYtYTJhMC00MjQzNzM5ZTZjM2EiLCJ1c2VybmFtZSI6ImZhYmlhbiJ9.LbsYIONdeeSWzsgUirHcbGGl7yySIXN5WLHWNpn4GAfXTTr2_HUJli_0Cyi6nf1sJuRJL4o8r_MXwzE0rvKjXkfG9z_jCQEGu8htdmhP6ubia6AWy90uN7ZDzSRmv1tUN7Nd3_vQuqFmfIO_kyl8y0QgmDn4bNu1rKL4iZyAmwS1MGo2JUiZJH62UZA79Iv94EzrBluQ-ePq94PEzJ3rsny-6iMFDgu9WYTxrpkhix4PaNU6DHXBFVEV2VOZ8n9MOOMCmeXpmQR7iauQNRilHdAXEjg7fIa3eaxeShL5ZkRJxTc_Eod_4LY_NnN-zyu66lYQsJNG-rVv3Qt20_ufWQ"  # noqa
FAKE_JWT_INVALID_ISSUER = "eyJraWQiOiJqWnd6VW0xOUtOOWplK1ZpVjBLeEdvUW5kemZQL0VVMGtXOU43MDQ0RVZVPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwYmRkMzQxYy0yODFmLTRlNTEtYWEzNy01MDI5MTU3NDkwNDMiLCJpc3MiOiJodHRwczovL2NvZ25pdG8taWRwLmV1LWNlbnRyYWwtMS5hbWF6b25hd3MuY29tL2V1LWNlbnRyYWwtMV9zOHBIMkt4b3AiLCJjbGllbnRfaWQiOiIydmRmOTh2cWVwb2VlMTRocXBjODQ4NmFsZSIsIm9yaWdpbl9qdGkiOiIyMzIyYmYzYi0xOTI2LTRjM2UtYmI5ZS05N2YzMmM0YTA2NWMiLCJldmVudF9pZCI6ImFkNzQ5MzQ2LTlkMGMtNDYzOC04MzMxLWViMGMyNjY3OTMyZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTcwOTgxMTgsImV4cCI6MTY1NzEwMTcxOCwiaWF0IjoxNjU3MDk4MTE4LCJqdGkiOiIxZjc2OGFkNy0wNzI3LTQ2MWYtYTJhMC00MjQzNzM5ZTZjM2EiLCJ1c2VybmFtZSI6ImZhYmlhbiJ9.Xjozn1LDc75O2kEIoeVO79ThQ7WwqivgFwaLEVV32BzTNnk8Ic-8nBYmxjyS6kc7yVbO0CIKbYD5LmcFUdPbBvKLvDGXuFUHXVuabjbeT92U8M9CA5G-1SsSykklDJz8GEV0wQfCAXsa4W3XsvE9DmjQP9fl_kleRl1pzW9t4QtXVp1MvUNBsvB-VJHXMsBjtzYm9ZzIgKJAD013rkFZcbyYrNa3cf7aWgoCJ7-rUEknUyphmmBnGoFlBdWsswVReqHF75vmZcQ3xNpFE6J3Z_1piHoxCrtPMprMF5RgGRgMRYb8VzANmOeR1yfAIA_A7a13_lLcimWCSV9KYPM2mg"  # noqa
FAKE_JWT_INVALID_TOKEN_TYPE = "eyJraWQiOiJqWnd6VW0xOUtOOWplK1ZpVjBLeEdvUW5kemZQL0VVMGtXOU43MDQ0RVZVPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwYmRkMzQxYy0yODFmLTRlNTEtYWEzNy01MDI5MTU3NDkwNDMiLCJpc3MiOiJodHRwczovL2NvZ25pdG8taWRwLmV1LWNlbnRyYWwtMS5hbWF6b25hd3MuY29tL2V1LWNlbnRyYWwtMV9zOHBIMkt4T1AiLCJjbGllbnRfaWQiOiIydmRmOTh2cWVwb2VlMTRocXBjODQ4NmFsZSIsIm9yaWdpbl9qdGkiOiIyMzIyYmYzYi0xOTI2LTRjM2UtYmI5ZS05N2YzMmM0YTA2NWMiLCJldmVudF9pZCI6ImFkNzQ5MzQ2LTlkMGMtNDYzOC04MzMxLWViMGMyNjY3OTMyZiIsInRva2VuX3VzZSI6ImlkIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTY1NzA5ODExOCwiZXhwIjoxNjU3MTAxNzE4LCJpYXQiOjE2NTcwOTgxMTgsImp0aSI6IjFmNzY4YWQ3LTA3MjctNDYxZi1hMmEwLTQyNDM3MzllNmMzYSIsInVzZXJuYW1lIjoiZmFiaWFuIn0.U2JWar-tC46W4GDb5TGqIbQtE2KSoxghS8mItWCfoH1YrEkwSi_P2Ujjitamho82aGKXzWJlJseDwEO5-sPHkDKSkWlHqGxm5NKtxx7NZDZhoOD3DO2RPDto8HX8YnqDaxH0h3IMrF59KD_IU-4wtLg33jmajFnejFuifHCDvQyiqGFD88KiMbjQ8bTvoTn9w1INKYfUWqrWWLbdE6XZCZOlP-v4Q49EKNnQooKqFWASCV54a8mgfjGkRm_My2mmkmqpCcjzeQiA2rtKC_zARUTyEBngklNJmcrhS-5_hlG1dtQh71Isz2cmTTZyzA32KG-CQVd7lj8GMSbZvpE5Tg"  # noqa

FAKE_COGNITO_REGION = "eu-central-1"
FAKE_COGNITO_USER_POOL_ID = "eu-central-1_s8pH2KxOP"
FAKE_COGNITO_APP_CLIENT_ID = "2vdf98vqepoee14hqpc8486ale"
FAKE_COGNITO_APP_CLIENT_SECRET = (
    "1cvd3babj7lriqnr2i8d7r16kpfftfk1jpf6d6phutj9aa5l4qb6"
)

ISSUED_AT = datetime.datetime(2022, 7, 6, 9, 1, 58)
EXPIRES_AT = datetime.datetime(2022, 7, 6, 10, 1, 58)
NON_EXPIRED_DATETIME = ISSUED_AT + datetime.timedelta(minutes=10)
EXPIRED_DATETIME = EXPIRES_AT + datetime.timedelta(minutes=1)


class FakeJWKS(tokens.jwks.JWKS):
    @classmethod
    def create(cls) -> "FakeJWKS":
        fake_keys = [
            {
                "alg": "RS256",
                "e": "AQAB",
                "kid": "fG9ZI3zslGG8GH308l93bYedOYvON1Kqj/FeCmXIAZM=",
                "kty": "RSA",
                "n": "tC4LJ_vPuCf4qFkk6wXYpUb_qfnT17lnXMYQfTV3MZxXE7z6oG3SffjwYRw2RcFVO1QCIs_Lqc_03fLQB5fQp8_nQtZYTXeTGmO_6WyfcUmSS_GmISnbGbmaOQJCr8dSt06Xd3L4oqg47A5Zy7JesSP7AiVpZk-7o0Zi-S-aIpDr2fZa5bUar0hrJdETKuPMY2Kio9HY1VDGqAnLdtkhvxEYB3jNa3XLAJ4p2ZEMakJHhsIm84iGXBuxo4S1oNL1O8RP9awN6dr_5YuYLcENPOZ_OBb9fes9goAVedhfdflGB5swWVGNUEMBB8ElgFKC4IxELNbJ7XopzMCVTpJX3Q",  # noqa
                "use": "sig",
            },
            {
                "alg": "RS256",
                "e": "AQAB",
                "kid": "jZwzUm19KN9je+ViV0KxGoQndzfP/EU0kW9N7044EVU=",
                "kty": "RSA",
                "n": "rP7xiJVMB1xnutn9QX0cD0CzoVx64zWUyeOo4c0Ed1I6Mu0R0Borwqoh_u6cJd7PBYlnTme4k_ueEDm7Z4w-m-89igM5_0oo0jionmFwCuWmShjoH1dJ2J6lb9v52jiVzQV2rIqlWx2Gkq3IuwgrDIg_11BY1X0lyGhuygncp3z-tRUmnB3kcdkO_gddUyI8Uhb20g1ypeTwx-FzWGPVOXAMaAeDMOak33pWzVVzR3zAvrcw6BHVgr3gwU7nPxq5TlD_d8lhYI7NvS16aML_OQsBvoJCCXAxf4j9g3MicUWAFSysLRaTCAkxHbrKOvFdEJ9k64G3sdbCTJf5J3MAWQ",  # noqa
                "use": "sig",
            },
        ]
        return cls(keys=fake_keys)


class FakeTokenVerifier(tokens.verifier.TokenVerifier):
    def __init__(
        self,
        cognito: t.Optional[_cognito.client.Properties] = None,
        jwks: t.Optional[_jwks.JWKS] = None,
        secret_required: t.Optional[bool] = None,
    ):
        self._ensure_secret_required_parameter_is_set(secret_required)

    def verify_token(self, token: str) -> None:
        if not token == "test-valid-token":
            raise tokens.exceptions.VerificationFailedException("Invalid token")
