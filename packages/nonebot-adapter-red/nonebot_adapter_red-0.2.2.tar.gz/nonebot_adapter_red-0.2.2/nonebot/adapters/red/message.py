import os
import re
import json
import uuid
import random
import hashlib
import tempfile
import subprocess
from io import BytesIO
from pathlib import Path
from datetime import datetime
from typing_extensions import override
from dataclasses import field, dataclass
from typing import TYPE_CHECKING, Dict, List, Type, Union, Iterable, Optional

from nonebot.exception import NetworkError
from nonebot.internal.driver import Request

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .api.model import Element
from .utils import log, is_amr

if TYPE_CHECKING:
    from .bot import Bot


TMP_DIR: str = tempfile.gettempdir()


def _handle_audio(buffer: bytes) -> Dict[str, Union[str, int]]:
    head: str = buffer[:7].decode()

    if not is_amr(buffer):
        uuid_str: str = str(uuid.uuid4())
        save_path: str = os.path.join(TMP_DIR, uuid_str)
        with open(save_path, "wb") as f:
            f.write(buffer)
        buffer = _audio_trans(save_path)
        os.remove(save_path)

    md5: str = hashlib.md5(buffer).hexdigest()

    save_path = os.path.join(TMP_DIR, md5)
    with open(save_path, "wb") as f:
        f.write(buffer)

    duration: int = 0 if "SILK" in head else _get_duration(save_path)
    os.remove(f"{save_path}.mp3")

    return {
        "md5": md5,
        "fileSize": len(buffer),
        "filePath": save_path,
        "duration": duration,
    }


def _audio_trans(file: str, ffmpeg: str = "ffmpeg") -> bytes:
    tmpfile: str = os.path.join(TMP_DIR, str(uuid.uuid4()))
    cmd: str = f"{ffmpeg} -y -i {file} -ac 1 -ar 8000 -ab 12.2k -f amr {tmpfile}"

    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        with open(tmpfile, "rb") as f:
            amr: bytes = f.read()
        return amr
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "音频转码到 amr 失败, 请确认你的 ffmpeg 可以处理此转换",
        ) from e
    finally:
        os.remove(tmpfile)


def _get_duration(file: str, ffmpeg: str = "ffmpeg") -> int:
    cmd: str = f"{ffmpeg} -i {file} {file}.mp3"
    result = subprocess.run(
        cmd, shell=True, check=False, capture_output=True, input=b"y"
    )
    out_str: str = result.stderr.decode()
    reg_duration: str = r"Duration: ([0-9:.]+),"
    rs = re.search(reg_duration, out_str)
    if not rs:
        raise RuntimeError("获取音频时长失败, 请确认你的 ffmpeg 可用")
    time_str: str = rs[1]
    parts: List[str] = time_str.split(":")
    return int(int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2]))


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        # 返回适配器的 Message 类型本身
        return Message

    @override
    def __str__(self) -> str:
        # 返回该消息段的纯文本表现形式，通常在日志中展示
        return self.data["text"] if self.is_text() else f"[{self.type}: {self.data}]"

    @override
    def is_text(self) -> bool:
        # 判断该消息段是否为纯文本
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "MessageSegment":
        return MessageSegment("text", {"text": text})

    @staticmethod
    def at(user_id: str) -> "MessageSegment":
        return MessageSegment("at", {"user_id": user_id})

    @staticmethod
    def at_all() -> "MessageSegment":
        return MessageSegment("at_all")

    @staticmethod
    def image(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MediaMessageSegment("image", {"file": file})

    @staticmethod
    def file(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MediaMessageSegment("file", {"file": file})

    @staticmethod
    def voice(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MediaMessageSegment("voice", {"file": file})

    @staticmethod
    def video(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MediaMessageSegment("video", {"file": file})

    @staticmethod
    def face(face_id: str) -> "MessageSegment":
        return MessageSegment("face", {"face_id": face_id})

    @staticmethod
    def reply(
        message_seq: str,
        message_id: Optional[str] = None,
        sender_uid: Optional[str] = None,
    ) -> "MessageSegment":
        return MessageSegment(
            "reply",
            {"msg_id": message_id, "msg_seq": message_seq, "sender_uid": sender_uid},
        )

    @staticmethod
    def ark(data: str) -> "MessageSegment":
        return MessageSegment("ark", {"data": data})

    @staticmethod
    def market_face(
        package_id: str, emoji_id: str, face_name: str, key: str, face_path: str
    ) -> "MessageSegment":
        log("WARNING", "market_face only can be received!")
        return MessageSegment(
            "market_face",
            {
                "package_id": package_id,
                "emoji_id": emoji_id,
                "face_name": face_name,
                "key": key,
                "face_path": face_path,
            },
        )

    @staticmethod
    def forward(xml: str, id: str, file_name: str) -> "MessageSegment":
        log(
            "WARNING",
            "forward only can be received!\n"
            "using `bot.send_fake_forward` to send a fake forward msg",
        )
        return MessageSegment(
            "forward",
            {"xml": xml, "id": id, "name": file_name},
        )


class MediaMessageSegment(MessageSegment):
    async def download(self, bot: "Bot") -> bytes:
        path = Path(self.data["path"])
        if path.exists():
            with path.open("rb") as f:
                return f.read()
        resp = await bot.adapter.request(
            Request(
                "POST",
                bot.info.api_base / "message" / "fetchRichMedia",
                headers={"Authorization": f"Bearer {bot.info.token}"},
                json={
                    "msgId": self.data["_msg_id"],
                    "chatType": self.data["_chat_type"],
                    "peerUid": self.data["_peer_uin"],
                    "elementId": self.data["id"],
                    "thumbSize": 0,
                    "downloadType": 2,
                },
            )
        )
        if resp.status_code == 200:
            return resp.content  # type: ignore
        raise NetworkError("red", resp)

    async def upload(self, bot: "Bot") -> dict:
        data = self.data["file"] if self.data.get("file") else await self.download(bot)
        resp = await bot.adapter.request(
            Request(
                "POST",
                bot.info.api_base / "upload",
                headers={
                    "Authorization": f"Bearer {bot.info.token}",
                },
                files={"file_image": ("file_image", data)},
            )
        )
        return json.loads(resp.content)  # type: ignore


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        # 返回适配器的 MessageSegment 类型本身
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    @classmethod
    def from_red_message(
        cls, message: List[Element], msg_id: str, chat_type: int, peer_uin: str
    ) -> "Message":
        msg = Message()
        for element in message:
            if element.elementType == 1:
                if TYPE_CHECKING:
                    assert element.textElement
                text = element.textElement
                if not text.atType:
                    msg.append(MessageSegment.text(text.content))
                elif text.atType == 1:
                    msg.append(MessageSegment.at_all())
                elif text.atType == 2:
                    msg.append(MessageSegment.at(text.atNtUin or text.atNtUid))  # type: ignore  # noqa: E501
            if element.elementType == 2:
                if TYPE_CHECKING:
                    assert element.picElement
                pic = element.picElement
                msg.append(
                    MediaMessageSegment(
                        "image",
                        {
                            "md5": pic.md5HexStr,
                            "size": pic.fileSize,
                            "id": element.elementId,
                            "uuid": pic.fileUuid,
                            "path": pic.sourcePath,
                            "width": pic.picWidth,
                            "height": pic.picHeight,
                            "_msg_id": msg_id,
                            "_chat_type": chat_type,
                            "_peer_uin": peer_uin,
                        },
                    )
                )
            if element.elementType == 3:
                if TYPE_CHECKING:
                    assert element.fileElement
                file = element.fileElement
                msg.append(
                    MediaMessageSegment(
                        "file",
                        {
                            "id": element.elementId,
                            "md5": file.fileMd5,
                            "name": file.fileName,
                            "size": file.fileSize,
                            "uuid": file.fileUuid,
                            "_msg_id": msg_id,
                            "_chat_type": chat_type,
                            "_peer_uin": peer_uin,
                        },
                    )
                )
            if element.elementType == 4:
                if TYPE_CHECKING:
                    assert element.pttElement
                ptt = element.pttElement
                msg.append(
                    MediaMessageSegment(
                        "voice",
                        {
                            "id": element.elementId,
                            "name": ptt.fileName,
                            "path": ptt.filePath,
                            "md5": ptt.md5HexStr,
                            "type": ptt.voiceChangeType,
                            "can_convert_to_text": ptt.canConvert2Text,
                            "text": ptt.text,
                            "wave_amplitudes": ptt.waveAmplitudes,
                            "uuid": ptt.fileUuid,
                            "_msg_id": msg_id,
                            "_chat_type": chat_type,
                            "_peer_uin": peer_uin,
                        },
                    )
                )
            if element.elementType == 5:
                if TYPE_CHECKING:
                    assert element.videoElement
                video = element.videoElement
                msg.append(
                    MediaMessageSegment(
                        "video",
                        {
                            "id": element.elementId,
                            "path": video.filePath,
                            "name": video.fileName,
                            "md5": video.videoMd5,
                            "format": video.fileFormat,
                            "time": video.fileTime,
                            "size": video.fileSize,
                            "uuid": video.fileUuid,
                            "thumb_md5": video.thumbMd5,
                            "thumb_size": video.thumbSize,
                            "thumb_width": video.thumbWidth,
                            "thumb_height": video.thumbHeight,
                            "thumb_path": video.thumbPath,
                            "busiType": video.busiType,
                            "subBusiType": video.subBusiType,
                            "transferStatus": video.transferStatus,
                            "progress": video.progress,
                            "invalidState": video.invalidState,
                            "fileSubId": video.fileSubId,
                            "fileBizId": video.fileBizId,
                            "_msg_id": msg_id,
                            "_chat_type": chat_type,
                            "_peer_uin": peer_uin,
                        },
                    )
                )
            if element.elementType == 6:
                if TYPE_CHECKING:
                    assert element.faceElement
                face = element.faceElement
                msg.append(MessageSegment.face(face.faceIndex))
            if element.elementType == 7:
                if TYPE_CHECKING:
                    assert element.replyElement
                reply = element.replyElement
                msg.append(
                    MessageSegment(
                        "reply",
                        {
                            "msg_id": reply.sourceMsgIdInRecords,
                            "msg_seq": reply.replayMsgSeq,
                            "sender_uid": reply.senderUid,
                        },
                    )
                )
            if element.elementType == 10:
                if TYPE_CHECKING:
                    assert element.arkElement
                ark = element.arkElement
                msg.append(MessageSegment.ark(ark.bytesData))
            if element.elementType == 11:
                if TYPE_CHECKING:
                    assert element.marketFaceElement
                market_face = element.marketFaceElement
                msg.append(
                    MessageSegment(
                        "market_face",
                        {
                            "package_id": market_face.emojiPackageId,
                            "face_name": market_face.faceName,
                            "emoji_id": market_face.emojiId,
                            "key": market_face.key,
                            "static_path": market_face.staticFacePath,
                            "dynamic_path": market_face.dynamicFacePath,
                        },
                    )
                )
            if element.elementType == 16:
                if TYPE_CHECKING:
                    assert element.multiForwardMsgElement
                forward_msg = element.multiForwardMsgElement
                msg.append(
                    MessageSegment(
                        "forward",
                        {
                            "xml": forward_msg.xmlContent,
                            "id": forward_msg.resId,
                            "name": forward_msg.fileName,
                        },
                    )
                )
        return msg

    async def export(self, bot: "Bot") -> List[dict]:
        res = []
        for seg in self:
            if seg.type == "text":
                res.append(
                    {"elementType": 1, "textElement": {"content": seg.data["text"]}}
                )
            elif seg.type == "at":
                res.append(
                    {
                        "elementType": 1,
                        "textElement": {"atType": 2, "atNtUin": seg.data["user_id"]},
                    }
                )
            elif seg.type == "at_all":
                res.append({"elementType": 1, "textElement": {"atType": 1}})
            elif seg.type == "image":
                if TYPE_CHECKING:
                    assert isinstance(seg, MediaMessageSegment)
                resp = await seg.upload(bot)
                file = Path(resp["ntFilePath"])
                res.append(
                    {
                        "elementType": 2,
                        "picElement": {
                            "original": True,
                            "md5HexStr": resp["md5"],
                            "picWidth": resp["imageInfo"]["width"],
                            "picHeight": resp["imageInfo"]["height"],
                            "fileSize": resp["fileSize"],
                            "fileName": file.name,
                            "sourcePath": resp["ntFilePath"],
                        },
                    }
                )
            elif seg.type == "file":
                raise NotImplementedError(
                    "Unsupported MessageSegment type: " f"{seg.type}"
                )
            elif seg.type == "voice":
                data = _handle_audio(seg.data["file"])
                res.append(
                    {
                        "elementType": 4,
                        "pttElement": {
                            "md5HexStr": data["md5"],
                            "fileSize": data["fileSize"],
                            "fileName": data["md5"] + ".amr",  # type: ignore
                            "filePath": data["filePath"],
                            "waveAmplitudes": [8, 0, 40, 0, 56, 0],
                            "duration": data["duration"],
                        },
                    }
                )
            elif seg.type == "video":
                raise NotImplementedError(
                    "Unsupported MessageSegment type: " f"{seg.type}"
                )
            elif seg.type == "face":
                res.append(
                    {
                        "elementType": 6,
                        "faceElement": {"faceIndex": seg.data["face_id"]},
                    }
                )
            elif seg.type == "reply":
                res.append(
                    {
                        "elementType": 7,
                        "replyElement": {
                            "sourceMsgIdInRecords": seg.data["msg_id"],
                            "replayMsgSeq": seg.data["msg_seq"],
                            "senderUid": seg.data["sender_uid"],
                        },
                    }
                )
            elif seg.type == "ark":
                res.append(
                    {"elementType": 10, "arkElement": {"bytesData": seg.data["data"]}}
                )
            elif seg.type == "market_face":
                raise NotImplementedError(
                    "Unsupported MessageSegment type: " f"{seg.type}"
                )
            elif seg.type == "forward_msg":
                raise NotImplementedError(
                    "Unsupported MessageSegment type: " f"{seg.type}"
                )
        return res


@dataclass
class ForwardNode:
    uid: str
    name: str
    group: Union[int, str]
    message: Message
    time: datetime = field(default_factory=datetime.now)

    async def export(self, seq: int, bot: "Bot") -> dict:
        elems = []
        for seg in self.message:
            if seg.type == "text":
                elems.append({"text": {"str": seg.data["text"]}})
            elif seg.type == "at":
                elems.append({"text": {"str": f"@{seg.data['user_id']}"}})
            elif seg.type == "at_all":
                elems.append({"text": {"str": "@全体成员"}})
            elif seg.type == "image":
                if TYPE_CHECKING:
                    assert isinstance(seg, MediaMessageSegment)
                resp = await seg.upload(bot)
                md5 = resp["md5"]
                file = Path(resp["ntFilePath"])
                pid = f"{{{md5[:8].upper()}-{md5[8:12].upper()}-{md5[12:16].upper()}-{md5[16:20].upper()}-{md5[20:].upper()}}}{file.suffix}"  # noqa: E501
                elems.append(
                    {
                        "customFace": {
                            "filePath": pid,
                            "fileId": random.randint(0, 65535),
                            "serverIp": -1740138629,
                            "serverPort": 80,
                            "fileType": 1001,
                            "useful": 1,
                            "md5": [int(md5[i : i + 2], 16) for i in range(0, 32, 2)],
                            "imageType": 1001,
                            "width": resp["imageInfo"]["width"],
                            "height": resp["imageInfo"]["height"],
                            "size": resp["fileSize"],
                            "origin": 0,
                            "thumbWidth": 0,
                            "thumbHeight": 0,
                            "pbReserve": [2, 0],
                        }
                    }
                )
            else:
                elems.append({"text": {"str": f"[{seg.type}]"}})
        return {
            "head": {
                "field2": self.uid,
                "field8": {
                    "field1": int(self.group),
                    "field4": self.name,
                },
            },
            "content": {
                "field1": 82,
                "field4": random.randint(0, 4294967295),
                "field5": seq,
                "field6": int(self.time.timestamp()),
                "field7": 1,
                "field8": 0,
                "field9": 0,
                "field15": {"field1": 0, "field2": 0},
            },
            "body": {"richText": {"elems": elems}},
        }
