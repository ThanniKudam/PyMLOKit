from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class AwsCreds:
     access_key: str
     secret_key: str
 
 
def parse_creds(credential: str) -> AwsCreds:
     parts = credential.split(";")
     if len(parts) < 2:
         raise ValueError("Invalid credential format. Expected ACCESS_KEY;SECRET_KEY")
     return AwsCreds(access_key=parts[0], secret_key=parts[1])
 
 
def boto3_clients(credential: str, region: str):
     try:
         import boto3
     except Exception as e:
         raise RuntimeError("Missing dependency: boto3 (install with `pip install pymlokit[aws]`)") from e
 
     c = parse_creds(credential)
     session = boto3.session.Session(
         aws_access_key_id=c.access_key,
         aws_secret_access_key=c.secret_key,
         region_name=region,
     )
     return session.client("sagemaker"), session.client("s3")
 
