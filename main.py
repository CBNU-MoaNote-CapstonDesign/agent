from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import httpx
import asyncio

# uvicorn main:app --host 0.0.0.0 --port 8000

class UserChatMessageBroadcastDTO:
    def __init__(self, message_type, sender_id, sender_name, date, message_content, chat_id):
        self.message_type = message_type
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.date = date
        self.message_content = message_content
        self.chat_id = chat_id

    def __repr__(self):
        return f"<UserChatMessageBroadcastDTO {self.__dict__}>"

    def to_dict(self):
        return self.__dict__

    def to_camel_case_dict(self):
        return {
            "messageType": self.message_type,
            "senderId": self.sender_id,
            "senderName": self.sender_name,
            "date": self.date,
            "messageContent": self.message_content,
            "chatId": self.chat_id,
        }

    @staticmethod
    def from_dict(data: dict):
        return UserChatMessageBroadcastDTO(
            message_type=data.get("messageType"),
            sender_id=data.get("senderId"),
            sender_name=data.get("senderName"),
            date=data.get("date"),
            message_content=data.get("messageContent"),
            chat_id=data.get("chatId")
        )

app = FastAPI()

async def buildBotMessage(channel_id):
    """
    채팅에 봇 메시지를 만드는 함수
    :param channel_id: 채팅방 UUID
    :param content: 콘텐츠
    :return:
    """
    async with httpx.AsyncClient() as client:
        print("Build Bot Message")
        try:
            print(f" channel_id: {channel_id}")
            url = f"http://localhost:8080/api/agent/chat/{channel_id}"

            response = await client.post(url)
            body = response.json()

            if response.status_code != 200:
                print("Build Bot Message Fail")

            dto = UserChatMessageBroadcastDTO.from_dict(body)

            return dto
        except Exception as e:
            print("Build Bot Message Fail",e)
            return None

async def updateBotMessage(channel_id:str,message:UserChatMessageBroadcastDTO,content:str):
    """
    봇이 보낸 채팅 메시지를 업데이트하는 함수
    :param chatId: 메시지 id
    :param content: 업데이트 된 메시지
    :return:
    """
    async with httpx.AsyncClient() as client:
        print("Update Bot Message")
        try:
            url = f"http://localhost:8080/api/agent/chat/{channel_id}/{message.chat_id}"

            message.message_content = content
            print(message.to_camel_case_dict())

            response = await client.post(url, json=message.to_camel_case_dict())

            if response.status_code != 200:
                print("Update Bot Message Fail : status code ", response.status_code)

            return True
        except Exception as e:
            print("Update Bot Message Fail",e)
            return False

class RequestPayload(BaseModel):
    channelId: str
    content: str

@app.post("/request")
async def handle_request(payload: RequestPayload):
    # 1. Bot Message Build
    message = await buildBotMessage(channel_id=payload.channelId)

    # 2. Bot Message Edit
    asyncio.create_task(updateBotMessage(channel_id=payload.channelId, message=message, content="봇 메시지 입니다."))

    return Response(status_code=200)
