#    Copyright 2020 Jonas Waeber
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from init_client import client, world_id

if __name__ == '__main__':

    notebook = client.notebook.put(
        {
            'title': 'A New Notebook',
            'world': {
                'id': world_id
            }
        }
    )
    value = client.notebook.get(notebook['id'], 1)
    print(value)

    note_section = client.note_section.put(
         {
             'title': 'A new section',
             'notebook': {
                 'id': notebook['id']
             }
         }
    )
    print(client.note_section.get(note_section['id'], 2))

    note = client.note.put(
         {
             'title': "A New Note",
             'content': 'Some content',
             'notesection': {
                 'id': note_section['id']
             }
         }
     )
    print(client.note.get(note['id'], 2))

    client.note.delete(note['id'])
    client.note_section.delete(note_section['id'])
    client.notebook.delete(notebook['id'])
