import json
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Iterable, Optional, List
from urllib.parse import urlparse

import requests
from pydantic import BaseModel
from websockets.sync.client import connect as ws_connect, ClientConnection

__version__ = '0.7.1'


class Status(str, Enum):
    Unknown = 'unknown'
    Scheduled = 'scheduled'
    Queued = 'queued'
    Running = 'running'
    Completed = 'completed'
    Failed = 'failed'
    Canceled = 'canceled'


class Answer(BaseModel):
    content: str


class ChatMessage(BaseModel):
    id: str
    content: str
    reply_to: Optional[str]
    votes: int
    created_at: datetime


class ChatMessageReference(BaseModel):
    document_id: str
    document_name: str
    chunk_id: int
    pages: str
    score: float


class ChatSessionCount(BaseModel):
    chat_session_count: int


class ChatSessionForCollection(BaseModel):
    id: str
    latest_message_content: Optional[str]
    updated_at: datetime


class ChatSessionInfo(BaseModel):
    id: str
    latest_message_content: Optional[str]
    collection_id: str
    collection_name: str
    updated_at: datetime


class Chunk(BaseModel):
    text: str


class Chunks(BaseModel):
    result: List[Chunk]


class Collection(BaseModel):
    id: str
    name: str
    description: str
    document_count: int
    document_size: int
    created_at: datetime
    updated_at: datetime


class CollectionCount(BaseModel):
    collection_count: int


class CollectionInfo(BaseModel):
    id: str
    name: str
    description: str
    document_count: int
    document_size: int
    updated_at: datetime


class Document(BaseModel):
    id: str
    name: str
    type: str
    size: int
    status: Status
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class DocumentCount(BaseModel):
    document_count: int


class DocumentInfo(BaseModel):
    id: str
    name: str
    type: str
    size: int
    status: Status
    updated_at: datetime

    class Config:
        use_enum_values = True


class Identifier(BaseModel):
    id: str


class JobStatus(BaseModel):
    id: str
    status: str


class Job(BaseModel):
    id: str
    passed: float
    failed: float
    progress: float
    completed: bool
    canceled: bool
    date: datetime
    statuses: List[JobStatus]
    errors: List[str]


class Meta(BaseModel):
    version: str
    build: str
    username: str
    email: str
    license_expired: bool
    license_expiry_date: str


class ObjectCount(BaseModel):
    chat_session_count: int
    collection_count: int
    document_count: int


class Result(BaseModel):
    status: Status

    class Config:
        use_enum_values = True


class SchedulerStats(BaseModel):
    queue_length: int


class SearchResult(BaseModel):
    id: str
    topic: str
    name: str
    text: str
    size: int
    pages: str
    score: float


class SearchResults(BaseModel):
    result: List[SearchResult]


@dataclass
class ChatRequest:
    t: str  # cq
    mode: str  # l=lexical, s=semantic, h=hybrid
    session_id: str
    correlation_id: str
    body: str


@dataclass
class ChatAcknowledgement:
    t: str  # cx
    session_id: str
    correlation_id: str
    message_id: str


@dataclass
class ChatResponse:
    t: str  # ca
    session_id: str
    message_id: str
    reply_to_id: str
    body: str


@dataclass
class ChatError:
    t: str  # ce
    session_id: str
    reply_to_id: str
    body: str


class SessionError(Exception):
    pass


class Session:
    def __init__(self, address: str, api_key: str, chat_session_id: str):
        url = urlparse(address)
        scheme = 'wss' if url.scheme == 'https' else 'ws'
        # TODO handle base URLs
        self._address = f'{scheme}://{url.netloc}/ws'
        self._api_key = api_key
        self._chat_session_id = chat_session_id
        self._connection: Optional[ClientConnection] = None

    def connect(self):
        self._connection = ws_connect(self._address, additional_headers={
            'Authorization': f'Bearer {self._api_key}'
        })

    def query(self, message: str, timeout: Optional[float] = None) -> ChatMessage:
        correlation_id = str(uuid.uuid4())
        req = asdict(ChatRequest(
            t='cq',
            mode='s',
            session_id=self._chat_session_id,
            correlation_id=correlation_id,
            body=message,
        ))
        self._connection.send(marshal(req))

        deadline = time.time() + timeout
        request_id: Optional[str] = None
        response = ''
        while True:
            res = self._connection.recv(deadline - time.time())
            payloads = res.splitlines()
            for payload in payloads:
                data = unmarshal(payload)
                t = data['t']

                if t == 'cx':  # ack
                    res = ChatAcknowledgement(**data)
                    if res.session_id != self._chat_session_id:
                        continue
                    if res.correlation_id == correlation_id:
                        request_id = res.message_id
                elif t == 'ca':  # response
                    res = ChatResponse(**data)
                    if res.session_id != self._chat_session_id:
                        continue
                    if res.reply_to_id == request_id:
                        response += res.body
                        return ChatMessage(
                            id=res.message_id,
                            content=response,
                            reply_to=res.reply_to_id,
                            votes=0,
                            created_at=datetime.now(),
                        )
                elif t == 'ce':
                    res = ChatError(**data)
                    if res.session_id != self._chat_session_id:
                        continue
                    if res.reply_to_id == request_id:
                        raise SessionError(f'Remote error: {res.body}')
                else:
                    raise SessionError(f'Invalid chat response type {t}.')

    def disconnect(self):
        self._connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class Helium:
    def __init__(self, address: str, api_key: str):
        self._address = address
        self._api_key = api_key
        self._auth_header = f'Bearer {self._api_key}'

    def _get(self, slug: str):
        res = requests.get(
            f'{self._address}{slug}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': self._auth_header,
            },
        )
        if res.status_code != 200:
            raise Exception(f'HTTP error: {res.status_code} {res.reason}')
        return unmarshal(res.text)

    def _post(self, slug: str, data: any):
        res = requests.post(
            f'{self._address}{slug}',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': self._auth_header,
            },
        )
        if res.status_code != 200:
            raise Exception(f'HTTP error: {res.status_code} {res.reason}')
        return unmarshal(res.text)

    def _db(self, method: str, *args):
        return self._post('/rpc/db', marshal([method, *args]))

    def _job(self, method: str, **kwargs):
        return self._post('/rpc/job', marshal([method, kwargs]))

    def _lang(self, method: str, **kwargs):
        res = self._post('/rpc/lang', marshal(dict(method=method, params=kwargs)))
        err = res.get('error')
        if err:
            raise Exception(err)
        return res['result']

    def _vex(self, method: str, collection_id: str, **kwargs):
        return self._post('/rpc/vex', marshal(dict(method=method, collection_id=collection_id, params=kwargs)))

    def _wait(self, d):
        job_id = _to_id(d)
        while True:
            time.sleep(1)
            job = self.get_job(job_id)
            if job.completed or job.canceled:
                break
        return job

    def answer_question(self, question: str, context: str):
        return Answer(**self._lang('answer_question_using_context', question=question, context=context))

    def cancel_job(self, job_id: str) -> Result:
        return Result(**self._job('.Cancel', job_id=job_id))

    def count_chat_sessions(self) -> int:
        return ChatSessionCount(**self._db('count_chat_sessions')).chat_session_count

    def count_chat_sessions_for_collection(self, collection_id: str) -> int:
        return ChatSessionCount(**self._db('count_chat_sessions_for_collection', collection_id)).chat_session_count

    def count_collections(self) -> int:
        return CollectionCount(**self._db('count_collections')).collection_count

    def count_documents(self) -> int:
        return DocumentCount(**self._db('count_documents')).document_count

    def count_documents_in_collection(self, collection_id: str) -> int:
        return DocumentCount(**self._db('count_documents_in_collection', collection_id)).document_count

    def count_assets(self) -> ObjectCount:
        return ObjectCount(**self._db('count_assets'))

    def create_chat_session(self, collection_id: str) -> str:
        return _to_id(self._db('create_chat_session', collection_id))

    def create_collection(self, name: str, description: str) -> str:
        return _to_id(self._db('create_collection', name, description))

    def delete_chat_sessions(self, chat_session_ids: Iterable[str]) -> Result:
        return Result(**self._db('delete_chat_sessions', chat_session_ids))

    def delete_collections(self, collection_ids: Iterable[str]):
        return self._wait(self._job('crawl.DeleteCollectionsJob', collection_ids=collection_ids))

    def delete_documents(self, document_ids: Iterable[str]):
        return self._wait(self._job('crawl.DeleteDocumentsJob', document_ids=document_ids))

    def delete_documents_from_collection(self, collection_id: str, document_ids: Iterable[str]):
        return self._wait(self._job('crawl.DeleteDocumentsFromCollectionJob', collection_id=collection_id,
                                    document_ids=document_ids))

    def encode_for_retrieval(self, chunks: List[str]) -> List[List[float]]:
        return self._lang('encode_for_retrieval', chunks=chunks)

    def get_chunks(self, collection_id: str, chunk_ids: Iterable[int]) -> List[Chunk]:
        res = self._vex('get_chunks', collection_id, chunk_ids=list(chunk_ids))
        return Chunks(**res).result

    def get_collection(self, collection_id: str) -> Collection:
        res = self._db('get_collection', collection_id)
        if len(res) == 0:
            raise KeyError(f'Collection {collection_id} not found')
        return Collection(**res[0])

    def get_collection_for_chat_session(self, chat_session_id: str) -> Collection:
        res = self._db('get_collection_for_chat_session', chat_session_id)
        if len(res) == 0:
            raise KeyError(f'Collection not found')
        return Collection(**res[0])

    def get_document(self, document_id: str) -> Document:
        res = self._db('get_document', document_id)
        if len(res) == 0:
            raise KeyError(f'Document {document_id} not found')
        return Document(**res[0])

    def get_job(self, job_id: str) -> Job:
        res = self._job('.Get', job_id=job_id)
        if len(res) == 0:
            raise KeyError(f'Job {job_id} not found')
        return Job(**(res[0]))

    def get_meta(self) -> Meta:
        return Meta(**(self._get('/rpc/meta')))

    def get_scheduler_stats(self) -> SchedulerStats:
        return SchedulerStats(**self._job('.Stats'))

    def ingest_from_file_system(self, collection_id: str, root_dir: str, glob: str):
        return self._wait(self._job(
            'crawl.IngestFromFileSystemJob', collection_id=collection_id, root_dir=root_dir, glob=glob
        ))

    def ingest_uploads(self, collection_id: str, upload_ids: Iterable[str]):
        return self._wait(self._job('crawl.IngestUploadsJob', collection_id=collection_id, upload_ids=upload_ids))

    def ingest_website(self, collection_id: str, url: str):
        return self._wait(self._job('crawl.IngestWebsiteJob', collection_id=collection_id, url=url))

    def list_chat_messages(self, chat_session_id: str, offset: int, limit: int) -> List[ChatMessage]:
        return [ChatMessage(**d) for d in self._db('list_chat_messages', chat_session_id, offset, limit)]

    def list_chat_message_references(self, message_id: str) -> List[ChatMessageReference]:
        return [ChatMessageReference(**d) for d in self._db('list_chat_message_references', message_id)]

    def list_chat_sessions_for_collection(
            self, collection_id: str, offset: int, limit: int
    ) -> List[ChatSessionForCollection]:
        return [ChatSessionForCollection(**d) for d in
                self._db('list_chat_sessions_for_collection', collection_id, offset, limit)]

    def list_collections_for_document(self, document_id: str, offset: int, limit: int) -> List[CollectionInfo]:
        return [CollectionInfo(**d) for d in self._db('list_collections_for_document', document_id, offset, limit)]

    def list_documents_in_collection(self, collection_id: str, offset: int, limit: int) -> List[DocumentInfo]:
        return [DocumentInfo(**d) for d in self._db('list_documents_in_collection', collection_id, offset, limit)]

    def list_jobs(self) -> List[Job]:
        return [Job(**d) for d in self._job('.List')]

    def list_recent_chat_sessions(self, offset: int, limit: int) -> List[ChatSessionInfo]:
        return [ChatSessionInfo(**d) for d in self._db('list_recent_chat_sessions', offset, limit)]

    def list_recent_collections(self, offset: int, limit: int) -> List[CollectionInfo]:
        return [CollectionInfo(**d) for d in self._db('list_recent_collections', offset, limit)]

    def list_recent_documents(self, offset: int, limit: int) -> List[DocumentInfo]:
        return [DocumentInfo(**d) for d in self._db('list_recent_documents', offset, limit)]

    def match_chunks(
            self, collection_id: str, vectors: List[List[float]], topics: List[str], offset: int, limit: int,
            cut_off: float = 0, width: int = 0
    ) -> List[SearchResult]:
        res = self._vex('match_chunks', collection_id, vectors=vectors, topics=topics, offset=offset, limit=limit,
                        cut_off=cut_off, width=width)
        return SearchResults(**res).result

    def search_chunks(
            self, collection_id: str, query: str, topics: List[str], offset: int, limit: int
    ) -> List[SearchResult]:
        res = self._vex('search_chunks', collection_id, query=query, topics=topics, offset=offset, limit=limit)
        return SearchResults(**res).result

    def set_chat_message_votes(self, chat_message_id: str, votes: int) -> Result:
        return Result(**self._db('set_chat_message_votes', chat_message_id, votes))

    def update_collection(self, collection_id: str, name: str, description: str) -> str:
        return _to_id(self._db('update_collection', collection_id, name, description))

    def upload(self, file_name: str, file: any) -> str:
        res = requests.post(
            f'{self._address}/rpc/fs',
            headers={
                'Authorization': self._auth_header,
            },
            files=dict(file=(file_name, file)),
        )
        if res.status_code != 200:
            raise Exception(f'HTTP error: {res.status_code} {res.reason}')
        return _to_id(unmarshal(res.text))

    def connect(self, chat_session_id: str) -> Session:
        return Session(self._address, api_key=self._api_key, chat_session_id=chat_session_id)


def _to_id(data: dict) -> str:
    return Identifier(**data).id


def marshal(d):
    return json.dumps(d, allow_nan=False, separators=(',', ':'))


def unmarshal(s):
    return json.loads(s)
