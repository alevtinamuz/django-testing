from notes.forms import NoteForm
from .test_base import BaseTestCase, LIST_URL, ADD_URL


class TestContent(BaseTestCase):

    def test_note_in_object_list(self):
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_forms_on_edit_and_add_pages(self):
        urls = (self.edit_url, ADD_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
