from typing import Final

KiB: Final[int] = 1024
MiB: Final[int] = KiB * 1024
GiB: Final[int] = MiB * 1024

MAX_CHUNK_SIZE = 200 * MiB  # chunk size in current api is limited by the load balancers  (100MB) so setting higher


class Headers:
    Authorization: Final[str] = "Authorization"
    Last_Modified: Final[str] = "Last-Modified"
    ETag: Final[str] = "ETag"
    Accept: Final[str] = "Accept"
    Accept_Encoding: Final[str] = "Accept-Encoding"
    Content_Type: Final[str] = "Content-Type"
    Content_Encoding: Final[str] = "Content-Encoding"
    Content_Length: Final[str] = "Content-Length"
    User_Agent: Final[str] = "User-Agent"

    Mex_From: Final[str] = "mex-From"
    Mex_FromSmtp: Final[str] = "mex-FromSmtp"
    Mex_To: Final[str] = "mex-To"
    Mex_ToSmtp: Final[str] = "mex-ToSmtp"
    Mex_Chunk_Range: Final[str] = "mex-Chunk-Range"
    Mex_StatusCode: Final[str] = "mex-StatusCode"
    Mex_StatusEvent: Final[str] = "mex-StatusEvent"
    Mex_StatusDescription: Final[str] = "mex-StatusDescription"
    Mex_StatusSuccess: Final[str] = "mex-StatusSuccess"
    Mex_StatusTimestamp: Final[str] = "mex-StatusTimestamp"
    Mex_WorkflowID: Final[str] = "mex-WorkflowID"
    Mex_Content_Compress: Final[str] = "mex-Content-Compress"
    Mex_Content_Encrypted: Final[str] = "mex-Content-Encrypted"
    Mex_Content_Compressed: Final[str] = "mex-Content-Compressed"
    Mex_Content_Checksum: Final[str] = "mex-Content-Checksum"
    Mex_MessageType: Final[str] = "mex-MessageType"
    Mex_MessageID: Final[str] = "mex-MessageID"
    Mex_LocalID: Final[str] = "mex-LocalID"
    Mex_PartnerID: Final[str] = "mex-PartnerID"
    Mex_FileName: Final[str] = "mex-FileName"
    Mex_Subject: Final[str] = "mex-Subject"
    Mex_ClientVersion: Final[str] = "mex-ClientVersion"
    Mex_OSName: Final[str] = "mex-OSName"
    Mex_OSVersion: Final[str] = "mex-OSVersion"
    Mex_OSArchitecture: Final[str] = "mex-OSArchitecture"
    Mex_JavaVersion: Final[str] = "mex-JavaVersion"
    Mex_Version: Final[str] = "mex-Version"
    Mex_LinkedMsgId = "mex-LinkedMsgID"
    Mex_AddressType = "mex-AddressType"
