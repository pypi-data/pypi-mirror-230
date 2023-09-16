from .componenttestcase import ComponentTestCase, ComponentTestCase2
from .collectiontestcase import CollectionTestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin, _ordered
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.testcase.collection import get_collection_key_from_name
from heaserver.service.representor import nvpjson
from heaobject.user import NONE_USER
from heaobject.root import copy_heaobject_dict_with
from heaobject.volume import MongoDBFileSystem, DEFAULT_FILE_SYSTEM
from aiohttp import hdrs


class TestGetComponent(ComponentTestCase, GetOneMixin):
    pass


class TestGetAllComponents(ComponentTestCase, GetAllMixin):
    pass


class TestPostComponent(ComponentTestCase, PostMixin):

    async def test_post_status_invalid_base_url(self):
        await self._test_invalid({'base_url': 2})

    async def test_post_status_invalid_resource(self):
        await self._test_invalid({'resources': [2]})

    async def test_post_status_invalid_resources_list(self):
        await self._test_invalid({'resources': 2})


class TestPutComponent(ComponentTestCase, PutMixin):

    async def test_put_status_invalid_base_url(self):
        await self._test_invalid({'base_url': 2})

    async def test_put_status_invalid_resource(self):
        await self._test_invalid({'resources': [2]})


class TestDeleteComponent(ComponentTestCase, DeleteMixin):
    pass


class TestGetResource(ComponentTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = {SUB: NONE_USER, hdrs.X_FORWARDED_HOST: 'localhost:8080'}
        desktop_objects = getattr(self, '_MicroserviceTestCase__desktop_objects')
        coll = get_collection_key_from_name(desktop_objects, self._coll)
        del desktop_objects[coll][0]['resources'][0]['file_system_type']
        del desktop_objects[coll][1]['resources'][0]['file_system_name']
        del desktop_objects[coll][1]['resources'][0]['file_system_type']

    async def test_no_file_system(self):
        expected = [{"collection": {
            "version": "1.0",
            "href": "http://localhost:8080/components/bytype/heaobject.folder.Folder",
            "items": [{
                "data": [
                    {
                        "name": "id",
                        "value": "666f6f2d6261722d71757578",
                        "prompt": "id",
                        "display": False},
                    {
                        "name": "created",
                        "value": None,
                        "prompt": "created",
                        "display": True},
                    {
                        "name": "derived_by",
                        "value": None,
                        "prompt": "derived_by",
                        "display": True},
                    {
                        "name": "derived_from",
                        "value": [],
                        "prompt": "derived_from",
                        "display": True},
                    {
                        "name": "description",
                        "value": None,
                        "prompt": "description",
                        "display": True},
                    {
                        "name": "display_name",
                        "value": "Reximus",
                        "prompt": "display_name",
                        "display": True},
                    {
                        "name": "invites",
                        "prompt": "invites",
                        "value": [],
                        "display": True
                    },
                    {
                        "name": "shares",
                        "prompt": "shares",
                        "value": [],
                        "display": True
                    },
                    {
                        "name": "modified",
                        "value": None,
                        "prompt": "modified",
                        "display": True},
                    {
                        "name": "name",
                        "value": "reximus",
                        "prompt": "name",
                        "display": True},
                    {
                        "name": "owner",
                        "value": "system|none",
                        "prompt": "owner",
                        "display": True},
                    {
                        "name": "type",
                        "value": "heaobject.registry.Component",
                        "prompt": "type",
                        "display": True
                    },
                    {
                        "name": "source",
                        "value": None,
                        "prompt": "source",
                        "display": True},
                    {
                        "name": "base_url",
                        "value": "http://localhost/foo",
                        "prompt": "base_url",
                        "display": True},
                    {
                        "name": "external_base_url",
                        "value": None,
                        "prompt": "external_base_url",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "resource_type_name",
                        "value": "heaobject.folder.Folder",
                        "prompt":
                            "resource_type_name",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "base_path",
                        "value": "folders",
                        "prompt": "base_path",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "file_system_name",
                        "value": "DEFAULT_FILE_SYSTEM",
                        "prompt": "file_system_name",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "type",
                        "value": "heaobject.registry.Resource",
                        "prompt": "type",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "resource_collection_type_display_name",
                        "value": "heaobject.folder.Folder",
                        "prompt": "resource_collection_type_display_name",
                        "display": True}],
                "links": []}]}}]
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=self._headers)
        self.assertEquals(_ordered(expected), _ordered(await obj.json()))

    async def test_no_file_system_status(self):
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=self._headers)
        self.assertEquals(200, obj.status)

    async def test_right_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemtype' / MongoDBFileSystem.get_type_name()).path,
                                        headers=self._headers)
        self.assertEquals(200, obj.status)

    async def test_wrong_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemtype' / 'WRONG_FILE_SYSTEM').path,
                                        headers=self._headers)
        self.assertEquals(404, obj.status)


class TestGetResource2(ComponentTestCase2):
    _headers = {SUB: NONE_USER, hdrs.X_FORWARDED_HOST: 'localhost:8080'}

    async def test_no_file_system(self):
        expected = [{"collection": {
            "version": "1.0",
            "href": "http://localhost:8080/components/bytype/heaobject.folder.Folder",
            "items": [{
                "data": [
                    {
                        "name": "id",
                        "value": "666f6f2d6261722d71757578",
                        "prompt": "id",
                        "display": False},
                    {
                        "name": "created",
                        "value": None,
                        "prompt": "created",
                        "display": True},
                    {
                        "name": "derived_by",
                        "value": None,
                        "prompt": "derived_by",
                        "display": True},
                    {
                        "name": "derived_from",
                        "value": [],
                        "prompt": "derived_from",
                        "display": True},
                    {
                        "name": "description",
                        "value": None,
                        "prompt": "description",
                        "display": True},
                    {
                        "name": "display_name",
                        "value": "Reximus",
                        "prompt": "display_name",
                        "display": True},
                    {
                        "name": "invite",
                        "index": 0,
                        "section": "shares",
                        "prompt": "invite",
                        "value": None,
                        "display": True
                    },
                    {
                        "name": "permissions",
                        "index": 0,
                        "section": "shares",
                        "prompt": "permissions",
                        "value": ['DELETER', 'EDITOR', 'VIEWER'],
                        "display": True
                    },
                    {
                        "name": "user",
                        "index": 0,
                        "section": "shares",
                        "prompt": "user",
                        "value": 'system|test',
                        "display": True
                    },
                    {
                        "name": "type",
                        "index": 0,
                        "section": "shares",
                        "prompt": "type",
                        "value": "heaobject.root.ShareImpl",
                        "display": True
                    },
                    {
                        "name": "modified",
                        "value": None,
                        "prompt": "modified",
                        "display": True},
                    {
                        "name": "name",
                        "value": "reximus",
                        "prompt": "name",
                        "display": True},
                    {
                        "name": "owner",
                        "value": "system|none",
                        "prompt": "owner",
                        "display": True},
                    {
                        "name": "source",
                        "value": None,
                        "prompt": "source",
                        "display": True},
                    {
                        "name": "type",
                        "value": "heaobject.registry.Component",
                        "prompt": "type",
                        "display": True
                    },
                    {
                        "name": "base_url",
                        "value": "http://localhost/foo",
                        "prompt": "base_url",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "resource_type_name",
                        "value": "heaobject.folder.Folder",
                        "prompt":
                            "resource_type_name",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "base_path",
                        "value": "folders",
                        "prompt": "base_path",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "file_system_name",
                        "value": "DEFAULT_FILE_SYSTEM",
                        "prompt": "file_system_name",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "type",
                        "value": "heaobject.registry.Resource",
                        "prompt": "type",
                        "display": True
                    },
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "resource_collection_type_display_name",
                        "value": "heaobject.folder.Folder",
                        "prompt": "resource_collection_type_display_name",
                        "display": True}],
                "links": []}]}}]
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=TestGetResource2._headers)
        self.assertEquals(_ordered(expected), _ordered(await obj.json()))

    async def test_no_file_system_status(self):
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=TestGetResource2._headers)
        self.assertEquals(200, obj.status)

    async def test_right_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemtype' / MongoDBFileSystem.get_type_name()).path,
                                        headers=TestGetResource2._headers)
        self.assertEquals(200, obj.status)

    async def test_wrong_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemtype' / 'WRONG_FILE_SYSTEM').path,
                                        headers=TestGetResource2._headers)
        self.assertEquals(404, obj.status)

    async def test_right_file_system_type_and_name_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemtype' / MongoDBFileSystem.get_type_name() / 'byfilesystemname' / DEFAULT_FILE_SYSTEM).path,
                                        headers=TestGetResource2._headers)
        self.assertEquals(200, obj.status)

    async def test_wrong_file_system_type_and_name_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemtype' / MongoDBFileSystem.get_type_name() / 'byfilesystemname' / 'WRONG_FILE_SYSTEM').path,
                                        headers=TestGetResource2._headers)
        self.assertEquals(404, obj.status)


class TestGetCollection(CollectionTestCase, GetOneMixin):
    pass


class TestGetAllCollections(CollectionTestCase, GetAllMixin):
    pass


class TestDeleteCollection(CollectionTestCase):
    async def test_delete_then_get(self) -> None:
        """Tries to delete a collection, which should fail."""
        async with self.client.delete((self._href / self.expected_one_id()).path,
                                       headers=self._headers) as resp:
            self.assertEqual(405, resp.status)

class TestPutCollection(CollectionTestCase):
    async def test_attempt_put(self):
        changed = copy_heaobject_dict_with(self._body_put, {'uri': 2})
        async with self.client.put((self._href / self.body_put_id()).path,
                                       json=changed,
                                       headers={**self._headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE}) as obj:
            self.assertEqual(405, obj.status)

class TestPostCollection(CollectionTestCase):
    async def test_attempt_put(self):
        changed = copy_heaobject_dict_with(self._body_post, {'id': None, 'name': 'foobar'})
        async with self.client.post((self._href / self.body_put_id()).path,
                                       json=changed,
                                       headers={**self._headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE}) as obj:
            self.assertEqual(405, obj.status)
