from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import BaseTestCase, SUCCESS_URL, ADD_URL, LOGIN_URL

User = get_user_model()


class TestLogic(BaseTestCase):
    NEW_NOTE_TITLE = 'new note'
    NEW_NOTE_TEXT = 'new text note'
    NEW_NOTE_SLUG = 'new-slug-note'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_user_can_create_note(self):
        count_notes_before_add = Note.objects.count()
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), count_notes_before_add + 1)
        note = Note.objects.get(slug=self.NEW_NOTE_SLUG)
        self.assertEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        count_notes_before_add = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, f'{LOGIN_URL}?next={ADD_URL}')
        self.assertEqual(Note.objects.count(), count_notes_before_add)

    def test_unique_slug(self):
        data = self.form_data.copy()
        data['slug'] = self.note.slug
        count_notes_before_add = Note.objects.count()
        response = self.author_client.post(ADD_URL, data=data)
        self.assertFormError(
            response.context['form'],
            'slug',
            self.note.slug + WARNING,
        )
        self.assertEqual(Note.objects.count(), count_notes_before_add)

    def test_empty_slug(self):
        data = self.form_data.copy()
        data.pop('slug')
        count_notes_before_add = Note.objects.count()
        response = self.author_client.post(ADD_URL, data=data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), count_notes_before_add + 1)
        expected_slug = slugify(data['title'])
        note = Note.objects.get(slug=expected_slug)
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_delete_note(self):
        count_notes_before_delete = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), count_notes_before_delete - 1)

    def test_user_cant_delete_note_of_another_user(self):
        count_notes_before_delete = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), count_notes_before_delete)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
